# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

import re
from typing import Generator, Optional

from context_logger import get_logger
from ssdpy import SSDPClient

log = get_logger('SsdpInventory')


class AnsibleInventory(object):

    def get_devices(self) -> Generator[dict[str, str], None, None]:
        raise NotImplementedError()


class SsdpInventory(AnsibleInventory):

    def __init__(self, ssdp_client: SSDPClient) -> None:
        self._ssdp_client = ssdp_client

    def get_devices(self, usn_filter: Optional[str] = None, nt_filter: Optional[str] = None,
                    timeout: int = 5) -> Generator[dict[str, str], None, None]:
        devices = self._ssdp_client.m_search("ssdp:all", timeout)

        log.info('Discovering devices', usn_filter=usn_filter, nt_filter=nt_filter, timeout=timeout)

        for device in devices:
            usn = device.get('usn', '')
            nt = device.get('nt', '')
            host = device.get('location', '')
            log.debug('Found device', usn=usn, nt=nt, host=host)
            if self._is_matching(usn_filter, usn) and self._is_matching(nt_filter, nt):
                name = usn.split(':')[1]
                log.info('Found matching device', usn=usn, nt=nt, name=name, host=host)
                yield {
                    'name': name,
                    'host': host,
                }

    def _is_matching(self, filter_regex: Optional[str], value: str) -> bool:
        if not filter_regex:
            return True
        return re.match(filter_regex, value) is not None
