# !/usr/bin/env python

# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

import json
import os.path
import sys
from typing import Any, Optional

from ansible.inventory.data import InventoryData
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.inventory import BaseInventoryPlugin
from context_logger import get_logger, setup_logging
from ssdpy import SSDPClient

PLUGIN_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(PLUGIN_DIR, '..'))

from inventory import SsdpInventory

log = get_logger('SsdpPlugin')


class InventoryModule(BaseInventoryPlugin):
    NAME = 'ssdpPlugin'

    def __init__(self) -> None:
        super(InventoryModule, self).__init__()

        setup_logging('ansible-server')

        self._ssdp_inventory = SsdpInventory(SSDPClient())
        self._configuration = None
        self._default_config_path = os.path.abspath(os.path.join(PLUGIN_DIR, '../configuration/ssdpPlugin.json'))

    def verify_file(self, path: Optional[str]) -> bool:
        if path and os.path.exists(path):
            self._configuration = self._read_configuration_file(path)

        if not self._configuration:
            log.info('Loading default configuration')
            self._configuration = self._read_configuration_file(self._default_config_path)

        if self._configuration:
            if logging := self._configuration.get('log'):
                setup_logging(
                    logging.get('application', 'ansible-server'),
                    logging.get('level', 'INFO'),
                    logging.get('file'),
                    warn_on_overwrite=False,
                )
            return True
        else:
            log.error('No valid configuration file found')
            return False

    def parse(self, inventory: InventoryData, loader: DataLoader, path: Optional[str], cache: bool = True) -> None:
        # call base method to ensure properties are available for use with other helper methods
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        if not self._configuration:
            log.error('Configuration not loaded, cannot proceed')
            return

        groups = self._configuration.get('groups', [])

        log.info('Collecting devices', groups=groups)

        for group in groups:
            group_name = group.get('name', '')
            if group_name:
                self.inventory.add_group(group_name)
                self.inventory.set_variable(group_name, 'ansible_connection', 'ssh')
                self.inventory.set_variable(group_name, 'ansible_user', group.get('user', 'admin'))
                self.inventory.set_variable(group_name, 'ansible_ssh_pass', group.get('password', 'admin'))

                usn_filter = group.get('usn_filter', None)
                nt_filter = group.get('nt_filter', None)
                timeout = group.get('timeout', 5)

                devices = self._ssdp_inventory.get_devices(usn_filter, nt_filter, timeout)

                for device in devices:
                    device_name = device.get('name', '')
                    device_host = device.get('host', '')
                    log.info('Adding device to group', device=device, group=group_name)
                    self.inventory.add_host(device_name, group=group_name)
                    self.inventory.set_variable(device_name, 'ansible_host', device_host)

        log.info('Inventory populated', inventory=inventory.serialize())

    def _read_configuration_file(self, path: str) -> Any:
        try:
            log.info('Reading configuration file', path=path)
            with open(path, 'r') as file:
                return json.load(file)
        except Exception as error:
            log.error('Error reading configuration file', path=path, error=error)
            return None
