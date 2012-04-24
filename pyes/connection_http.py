# -*- coding: utf-8 -*-
from __future__ import absolute_import
from requests.exceptions import RequestException
from time import time
import random
import threading
import base64
import requests
from .exceptions import NoServerAvailable
from .fakettypes import Method, RestResponse
from . import logger

__all__ = ['connect', 'connect_thread_local']

DEFAULT_SERVER = ("http", "127.0.0.1", 9200)
SESSION = requests.session()

class ClientTransport(object):
    """Encapsulation of a client session."""

    def __init__(self, server, timeout, recycle, basic_auth=None):
        connection_type, host, port = server
        self.server_uri = '%s://%s:%s' % (connection_type, host, port)
        self.timeout = timeout
        self.headers = {}
        if recycle:
            self.recycle = time() + recycle + random.uniform(0, recycle * 0.1)
        else:
            self.recycle = None
        if basic_auth:
            username = basic_auth.get('username')
            password = basic_auth.get('password')
            base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
            self.headers["Authorization"] = 'Basic %s' % base64string

    def execute(self, request):
        """Execute a request and return a response"""
        headers = self.headers.copy()
        headers.update(request.headers)
        response = SESSION.request(
            method=Method._VALUES_TO_NAMES[request.method],
            url=self.server_uri + request.uri,
            params=request.parameters,
            data=request.body,
            headers=request.headers,
            timeout=self.timeout)
        return RestResponse(status=response.status_code,
                            body=response.content,
                            headers=response.headers)


def connect(servers=None, framed_transport=False, timeout=None,
            retry_time=60, recycle=None, round_robin=None,
            max_retries=3, basic_auth=None):
    """
    Constructs a single ElasticSearch connection. Connects to a randomly chosen
    server on the list.

    If the connection fails, it will attempt to connect to each server on the
    list in turn until one succeeds. If it is unable to find an active server,
    it will throw a NoServerAvailable exception.

    Failing servers are kept on a separate list and eventually retried, no
    sooner than `retry_time` seconds after failure.

    Parameters
    ----------
    servers : [server]
              List of ES servers with format: "hostname:port"

              Default: [("http", "127.0.0.1", 9200)]
    framed_transport: bool
              If True, use a TFramedTransport instead of a TBufferedTransport
    timeout: float
              Timeout in seconds (e.g. 0.5)

              Default: None (it will stall forever)
    retry_time: float
              Minimum time in seconds until a failed server is reinstated. (e.g. 0.5)

              Default: 60
    recycle: float
              Max time in seconds before an open connection is closed and returned to the pool.

              Default: None (Never recycle)
    max_retries: int
              Max retry time on connection down

    basic_auth: dict
              Use HTTP Basic Auth. Use ssl while using basic auth to keep the
              password from being transmitted in the clear.
              Expects keys:
                  * username
                  * password

    round_robin: bool
              *DEPRECATED*

    Returns
    -------
    ES client
    """

    if servers is None:
        servers = [DEFAULT_SERVER]
    return ThreadLocalConnection(servers, timeout, retry_time, recycle,
                                 max_retries, basic_auth)

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
            try:
                ts, server = self._dead.pop()
            except IndexError:
                pass
            else:
                if ts > time():  # Not yet, put it back
                    self._dead.append((ts, server))
                else:
                    self._servers.append(server)
                    logger.info('Server %r reinstated into working pool', server)

            try:
                return random.choice(self._servers)
            except IndexError:
                logger.critical('No servers available')
                raise NoServerAvailable

    def mark_dead(self, server):
        with self._lock:
            self._servers.remove(server)
            self._dead.insert(0, (time() + self._retry_time, server))
            logger.warning('Server %r removed from working pool', server)


class ThreadLocalConnection(object):
    def __init__(self, servers, timeout=None, retry_time=10, recycle=None,
                 max_retries=3, basic_auth=None):
        self._servers = ServerSet(servers, retry_time)
        self._timeout = timeout
        self._recycle = recycle
        self._max_retries = max_retries
        self._basic_auth = basic_auth
        self._local = threading.local()

    def __getattr__(self, attr):
        def _client_call(*args, **kwargs):
            retry = 0
            while True:
                try:
                    conn = self.connect()
                    if conn.recycle and conn.recycle < time():
                        logger.debug('Recycling expired client session after %is.',
                                     self._recycle)
                        self.close()
                        conn = self.connect()

                    return getattr(conn, attr)(*args, **kwargs)

                except RequestException:
                    self.mark_current_server_dead()
                    if retry >= self._max_retries:
                        logger.critical('Client error: bailing out after %d failed retries',
                                        self._max_retries, exc_info=1)
                        raise NoServerAvailable
                    logger.debug('Client error: %d retries left',
                                 self._max_retries - retry)
                    retry += 1

        setattr(self, attr, _client_call)
        return _client_call

    def connect(self):
        """Create new connection unless we already have one."""
        if not getattr(self._local, 'conn', None):
            server = self._servers.get()
            self._local.server = server
            self._local.conn = ClientTransport(server, self._timeout,
                                               self._recycle, self._basic_auth)
        return self._local.conn

    def mark_current_server_dead(self):
        server = getattr(self._local, 'server', None)
        if server:
            self._servers.mark_dead(server)
            self.close()

    def close(self):
        self._local.conn = None
        self._local.server = None
