# -*- coding: utf-8 -*-
from __future__ import absolute_import
import random
import socket
import threading
import time

from thrift import Thrift
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from .pyesthrift import Rest

from .exceptions import NoServerAvailable
from . import logger

__all__ = ['connect', 'connect_thread_local', 'NoServerAvailable']

"""
Work taken from pycassa.

You need installed "thrift" to use this.
Just do a "pip install thrift".

"""

DEFAULT_SERVER = ("thrift", "127.0.0.1", 9500)

class ClientTransport(object):
    """Encapsulation of a client session."""

    def __init__(self, server, framed_transport, timeout, recycle):
        socket = TSocket.TSocket(server.hostname, server.port)
        if timeout is not None:
            socket.setTimeout(timeout * 1000.0)
        if framed_transport:
            transport = TTransport.TFramedTransport(socket)
        else:
            transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
        client = Rest.Client(protocol)
        transport.open()

        #        server_api_version = client.describe_version().split('.', 1)
        #        assert server_api_version[0] == API_VERSION[0], \
        #                "Thrift API version mismatch. " \
        #                 "(Client: %s, Server: %s)" % (API_VERSION[0], server_api_version[0])

        self.client = client
        self.transport = transport

        if recycle:
            self.recycle = time.time() + recycle + random.uniform(0, recycle * 0.1)
        else:
            self.recycle = None


def connect(servers=None, framed_transport=False, timeout=None,
            retry_time=60, recycle=None, round_robin=None, max_retries=3):
    """
    Constructs a single ElasticSearch connection. Connects to a randomly chosen
    server on the list.

    If the connection fails, it will attempt to connect to each server on the
    list in turn until one succeeds. If it is unable to find an active server,
    it will throw a NoServerAvailable exception.

    Failing servers are kept on a separate list and eventually retried, no
    sooner than `retry_time` seconds after failure.

    :keyword servers: [server]
                      List of ES servers with format: "hostname:port"
                      Default: [("127.0.0.1",9500)]

    :keyword framed_transport: If True, use a TFramedTransport instead of a TBufferedTransport

    :keyword timeout: Timeout in seconds (e.g. 0.5)
                      Default: None (it will stall forever)

    :keyword retry_time: Minimum time in seconds until a failed server is reinstated. (e.g. 0.5)
                         Default: 60

    :keyword recycle:  Max time in seconds before an open connection is closed and returned to the pool.
                       Default: None (Never recycle)

    :keyword max_retries: Max retry time on connection down

    :keyword round_robin: *DEPRECATED*

    :return ES client
    """

    if servers is None:
        servers = [DEFAULT_SERVER]
    return ThreadLocalConnection(servers, framed_transport, timeout,
        retry_time, recycle, max_retries=max_retries)

connect_thread_local = connect


class ServerSet(object):
    """Automatically balanced set of servers.
       Manages a separate stack of failed servers, and automatic
       retrial."""

    def __init__(self, servers, retry_time=10):
        self._lock = threading.RLock()
        self._servers = list(servers)
        self._retry_time = retry_time
        self._dead = []

    def get(self):
        with self._lock:
            if self._dead:
                ts, revived = self._dead.pop()
                if ts > time.time():  # Not yet, put it back
                    self._dead.append((ts, revived))
                else:
                    self._servers.append(revived)
                    logger.info('Server %r reinstated into working pool', revived)
            if not self._servers:
                logger.critical('No servers available')
                raise NoServerAvailable()
            return random.choice(self._servers)

    def mark_dead(self, server):
        with self._lock:
            try:
                self._servers.remove(server)
                self._dead.insert(0, (time.time() + self._retry_time, server))
            except ValueError:
                pass



class ThreadLocalConnection(object):
    def __init__(self, servers, framed_transport=False, timeout=None,
                 retry_time=10, recycle=None, max_retries=3):
        self._servers = ServerSet(servers, retry_time)
        self._framed_transport = framed_transport
        self._timeout = timeout
        self._recycle = recycle
        self._max_retries = max_retries
        self._local = threading.local()

    def __getattr__(self, attr):
        def _client_call(*args, **kwargs):
            for retry in range(self._max_retries + 1):
                try:
                    conn = self._ensure_connection()
                    return getattr(conn.client, attr)(*args, **kwargs)
                except (Thrift.TException, socket.timeout, socket.error) as exc:
                    logger.exception('Client error: %s', exc)
                    self.close()

                    if retry < self._max_retries:
                        continue

                    raise NoServerAvailable(exc)

        setattr(self, attr, _client_call)
        return getattr(self, attr)

    def _ensure_connection(self):
        """Make certain we have a valid connection and return it."""
        conn = self.connect()
        if conn.recycle and conn.recycle < time.time():
            logger.debug('Client session expired after %is. Recycling.', self._recycle)
            self.close()
            conn = self.connect()
        return conn

    def connect(self):
        """Create new connection unless we already have one."""
        if not getattr(self._local, 'conn', None):
            try:
                server = self._servers.get()
                logger.debug('Connecting to %s', server)
                self._local.conn = ClientTransport(server, self._framed_transport,
                    self._timeout, self._recycle)
            except (Thrift.TException, socket.timeout, socket.error):
                logger.warning('Connection to %s failed.', server)
                self._servers.mark_dead(server)
                return self.connect()
        return self._local.conn

    def close(self):
        """If a connection is open, close its transport."""
        if self._local.conn:
            self._local.conn.transport.close()
        self._local.conn = None
