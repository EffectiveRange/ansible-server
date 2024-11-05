import os
import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from ansible.inventory.data import InventoryData
from context_logger import setup_logging

from mocks import SsdpMockServerPool
from plugin import InventoryModule

TESTS_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class SsdpPluginIntegrationTest(TestCase):

    @classmethod
    def setUpClass(cls):
        setup_logging('ansible-server', 'DEBUG', warn_on_overwrite=False)

    def setUp(self):
        print()

    def test_device_discovery(self):
        with SsdpMockServerPool() as pool:
            # Given
            pool.add('testid:device-1', 'test:device', 'host-1', 10)
            pool.add('testid:device-2', 'test:device', 'host-2', 10)
            pool.add('testid:device-3', 'test:service', 'host-3', 10)

            ssdp_plugin = InventoryModule()
            ssdp_plugin.verify_file(f'{TESTS_DIR_PATH}/configuration/ssdpPlugin.json')

            inventory = InventoryData()

            # When
            ssdp_plugin.parse(inventory, MagicMock(), None)

            # Then
            self.assertIsNotNone(inventory.groups.get('test_devices'))
            self.assertEqual('ssh', inventory.groups.get('test_devices').vars['ansible_connection'])
            self.assertEqual('admin', inventory.groups.get('test_devices').vars['ansible_user'])
            self.assertEqual('admin', inventory.groups.get('test_devices').vars['ansible_ssh_pass'])
            self.assertCountEqual({'device-1', 'device-2'}, inventory.groups.get('test_devices').host_names)
            self.assertEqual('host-1', inventory.hosts.get('device-1').vars['ansible_host'])
            self.assertEqual('host-2', inventory.hosts.get('device-2').vars['ansible_host'])

            self.assertIsNotNone(inventory.groups.get('test_services'))
            self.assertEqual('ssh', inventory.groups.get('test_services').vars['ansible_connection'])
            self.assertEqual('admin', inventory.groups.get('test_services').vars['ansible_user'])
            self.assertEqual('admin', inventory.groups.get('test_services').vars['ansible_ssh_pass'])
            self.assertCountEqual({'device-3'}, inventory.groups.get('test_services').host_names)
            self.assertEqual('host-3', inventory.hosts.get('device-3').vars['ansible_host'])


if __name__ == "__main__":
    unittest.main()
