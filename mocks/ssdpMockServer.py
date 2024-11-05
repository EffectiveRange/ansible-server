#!/usr/bin/env python

# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

from threading import Thread
from typing import Any, Optional

from context_logger import get_logger
from ssdpy import SSDPServer

log = get_logger('SsdpMockServer')


class SsdpMockServer(object):

    def __init__(self, usn: str, device_type: str, location: str) -> None:
        self.usn = usn
        self.device_type = device_type
        self.location = location
        self.server: Optional[SSDPServer] = None
        self.thread: Optional[Thread] = None

    def start(self, timeout: int = 5) -> None:
        self.stop()
        self.server = SSDPServer(self.usn, device_type=self.device_type, location=self.location)
        self.server.sock.settimeout(timeout)
        self.thread = Thread(target=self._start_server, args=())
        log.info('Starting SSDP server', usn=self.usn, device_type=self.device_type, location=self.location)
        self.thread.start()

    def stop(self) -> None:
        if self.server is not None:
            log.info('Shutting down')
            self.server.stopped = True
        if self.thread is not None:
            self.thread.join()

    def _start_server(self) -> None:
        if self.server is not None:
            try:
                self.server.serve_forever()
            except OSError as error:
                log.info('Server stopped', reason=error)


class SsdpMockServerPool(object):

    def __init__(self) -> None:
        self.servers: list[SsdpMockServer] = []

    def __enter__(self) -> 'SsdpMockServerPool':
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        for server in self.servers:
            server.stop()

    def add(self, usn: str, device_type: str, location: str, timeout: int = 5) -> None:
        server = SsdpMockServer(usn, device_type, location)
        self.servers.append(server)
        server.start(timeout)
