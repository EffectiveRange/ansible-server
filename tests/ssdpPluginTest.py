import os
import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from ansible.inventory.data import InventoryData
from context_logger import setup_logging

from inventory import SsdpInventory
from plugin import InventoryModule

TESTS_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class SsdpPluginTest(TestCase):

    @classmethod
    def setUpClass(cls):
        setup_logging('ansible-server', 'DEBUG', warn_on_overwrite=False)

    def setUp(self):
        print()

    def test_returns_true_when_configuration_is_loaded_from_path(self):
        # Given
        ssdp_plugin = InventoryModule()
        config_file_path = os.path.abspath(f'{TESTS_DIR_PATH}/configuration/ssdpPlugin.json')

        # When
        result = ssdp_plugin.verify_file(config_file_path)

        # Then
        self.assertTrue(result)
        self.assertEqual('test_devices', ssdp_plugin._configuration['groups'][0]['name'])

    def test_returns_true_when_path_is_invalid_and_default_config_is_loaded(self):
        # Given
        ssdp_plugin = InventoryModule()
        ssdp_plugin._default_config_path = os.path.abspath(f'{TESTS_DIR_PATH}/configuration/ssdpPlugin.json')
        config_file_path = '/non/existent/path'

        # When
        result = ssdp_plugin.verify_file(config_file_path)

        # Then
        self.assertTrue(result)
        self.assertEqual('test_devices', ssdp_plugin._configuration['groups'][0]['name'])

    def test_returns_true_when_path_is_none_and_default_config_is_loaded(self):
        # Given
        ssdp_plugin = InventoryModule()
        ssdp_plugin._default_config_path = os.path.abspath(f'{TESTS_DIR_PATH}/configuration/ssdpPlugin.json')

        # When
        result = ssdp_plugin.verify_file(None)

        # Then
        self.assertTrue(result)
        self.assertEqual('test_devices', ssdp_plugin._configuration['groups'][0]['name'])

    def test_returns_false_when_path_is_invalid_and_default_config_path_is_invalid(self):
        # Given
        ssdp_plugin = InventoryModule()
        ssdp_plugin._default_config_path = '/invalid/path'
        config_file_path = '/non/existent/path'

        # When
        result = ssdp_plugin.verify_file(config_file_path)

        # Then
        self.assertFalse(result)

    def test_device_discovery_skipped_when_configuration_is_not_loaded(self):
        # Given
        ssdp_plugin = InventoryModule()

        inventory = InventoryData()

        # When
        ssdp_plugin.parse(inventory, MagicMock(), None)

        # Then
        self.assertIsNone(inventory.groups.get('test_devices'))

    def test_device_discovery(self):
        # Given
        ssdp_plugin = InventoryModule()
        ssdp_plugin.verify_file(f'{TESTS_DIR_PATH}/configuration/ssdpPlugin.json')
        ssdp_plugin._ssdp_inventory = MagicMock(spec=SsdpInventory)
        ssdp_plugin._ssdp_inventory.get_devices.side_effect = [[
            {'name': 'device-1', 'host': 'host-1'},
            {'name': 'device-2', 'host': 'host-2'},
        ], [
            {'name': 'service-1', 'host': 'host-3'},
            {'name': 'service-2', 'host': 'host-4'},
        ]]

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
        self.assertCountEqual({'service-1', 'service-2'}, inventory.groups.get('test_services').host_names)
        self.assertEqual('host-3', inventory.hosts.get('service-1').vars['ansible_host'])
        self.assertEqual('host-4', inventory.hosts.get('service-2').vars['ansible_host'])


if __name__ == "__main__":
    unittest.main()
