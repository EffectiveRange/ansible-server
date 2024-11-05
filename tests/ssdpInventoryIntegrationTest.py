import unittest
from unittest import TestCase

from context_logger import setup_logging
from ssdpy import SSDPClient

from inventory import SsdpInventory
from mocks import SsdpMockServerPool


class SsdpInventoryIntegrationTest(TestCase):

    @classmethod
    def setUpClass(cls):
        setup_logging('ansible-server', 'DEBUG', warn_on_overwrite=False)

    def setUp(self):
        print()

    def test_get_devices_with_single_match(self):
        with SsdpMockServerPool() as pool:
            # Given
            pool.add('testid:device-1', 'test:device', 'host-1', 1)

            ssdp_client = SSDPClient()
            ssdp_inventory = SsdpInventory(ssdp_client)

            # When
            devices = list(ssdp_inventory.get_devices('^testid:.*', '^test:.*', 1))

            # Then
            expected = [
                {'name': 'device-1', 'host': 'host-1'}
            ]
            self.assertCountEqual(expected, devices)

    def test_get_devices_with_multiple_matches(self):
        with SsdpMockServerPool() as pool:
            # Given
            pool.add('testid:device-1', 'test:device', 'host-1', 1)
            pool.add('testid:device-2', 'skip:device', 'host-2', 1)
            pool.add('testid:device-3', 'test:device', 'host-3', 1)

            ssdp_client = SSDPClient()
            ssdp_inventory = SsdpInventory(ssdp_client)

            # When
            devices = list(ssdp_inventory.get_devices('^testid:.*', '^test:.*', 1))

            # Then
            expected = [
                {'name': 'device-1', 'host': 'host-1'},
                {'name': 'device-3', 'host': 'host-3'}
            ]
            self.assertCountEqual(expected, devices)


if __name__ == "__main__":
    unittest.main()
