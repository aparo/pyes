# -*- coding: utf-8 -*-
from __future__ import absolute_import
from . import logger
from .exceptions import NoServerAvailable
from .fakettypes import Method, RestResponse
from time import time
from urllib import urlencode
from urlparse import urlparse
import random
import threading
import urllib3

__all__ = ["connect"]

DEFAULT_SERVER = ("http", "127.0.0.1", 9200)
POOL_MANAGER = urllib3.PoolManager()


class Connection(object):
    """An ElasticSearch connection to a randomly chosen server of the list.

    If the connection fails, it attempts to connect to another random server
    of the list until one succeeds. If it is unable to find an active server,
    it throws a NoServerAvailable exception.

    Failing servers are kept on a separate list and eventually retried, no
    sooner than `retry_time` seconds after failure.

    Parameters
    ----------

    servers: List of ES servers represented as (`scheme`, `hostname`, `port`)
             tuples. Default: [("http", "127.0.0.1", 9200)]

    retry_time: Minimum time in seconds until a failed server is reinstated.
                Default: 60

    max_retries: Max number of attempts to connect to some server.

    timeout: Timeout in seconds. Default: None (wait forever)

    basic_auth: Use HTTP Basic Auth. A (`username`, `password`) tuple or a dict
                with `username` and `password` keys.
    """

    def __init__(self, servers=None, retry_time=60, max_retries=3, timeout=None,
                 basic_auth=None):
        if servers is None:
            servers = [DEFAULT_SERVER]
        self._active_servers = [server.geturl() for server in servers]
        self._inactive_servers = []
        self._retry_time = retry_time
        self._max_retries = max_retries
        self._timeout = timeout
        if basic_auth:
            self._headers = urllib3.make_headers(basic_auth="%(username)s:%(password)s" % basic_auth)
        else:
            self._headers = {}
        self._lock = threading.RLock()
        self._local = threading.local()

    def execute(self, request):
        """Execute a request and return a response"""
        url = request.uri
        if request.parameters:
            url += '?' + urlencode(request.parameters)

        if request.headers:
            headers = dict(self._headers, **request.headers)
        else:
            headers = self._headers

        kwargs = dict(
            method=Method._VALUES_TO_NAMES[request.method],
            url=url,
            body=request.body,
            headers=headers,
            timeout=self._timeout,
        )

        retry = 0
        server = getattr(self._local, "server", None)
        while True:
            if not server:
                self._local.server = server = self._get_server()
            try:
                parse_result = urlparse(server)
                conn = POOL_MANAGER.connection_from_host(parse_result.hostname,
                                                         parse_result.port,
                                                         parse_result.scheme)
                response = conn.urlopen(**kwargs)
                return RestResponse(status=response.status,
                                    body=response.data,
                                    headers=response.headers)
            except urllib3.exceptions.HTTPError:
                self._drop_server(server)
                self._local.server = server = None
                if retry >= self._max_retries:
                    logger.error("Client error: bailing out after %d failed retries",
                                 self._max_retries, exc_info=1)
                    raise NoServerAvailable
                logger.exception("Client error: %d retries left", self._max_retries - retry)
                retry += 1

    def _get_server(self):
        with self._lock:
            try:
                ts, server = self._inactive_servers.pop()
            except IndexError:
                pass
            else:
                if ts > time():  # Not yet, put it back
                    self._inactive_servers.append((ts, server))
                else:
                    self._active_servers.append(server)
                    logger.info("Restored server %s into active pool", server)

            try:
                return random.choice(self._active_servers)
            except IndexError:
                raise NoServerAvailable

    def _drop_server(self, server):
        with self._lock:
            try:
                self._active_servers.remove(server)
            except ValueError:
                pass
            else:
                self._inactive_servers.insert(0, (time() + self._retry_time, server))
                logger.warning("Removed server %s from active pool", server)

connect = Connection
