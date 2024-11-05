import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from context_logger import setup_logging
from ssdpy import SSDPClient

from inventory import SsdpInventory


class SsdpInventoryTest(TestCase):

    @classmethod
    def setUpClass(cls):
        setup_logging('ansible-server', 'DEBUG', warn_on_overwrite=False)

    def setUp(self):
        print()

    def test_returns_all_devices_when_no_filtering(self):
        # Given
        ssdp_client = set_up_ssdp_client()
        ssdp_inventory = SsdpInventory(ssdp_client)

        # When
        devices = list(ssdp_inventory.get_devices())

        # Then
        expected = [
            {'name': 'device-1', 'host': 'host-1'},
            {'name': '01234567', 'host': 'host-2'},
            {'name': 'device-3', 'host': 'host-3'}
        ]
        self.assertCountEqual(expected, devices)

    def test_returns_devices_when_usn_is_filtered(self):
        # Given
        ssdp_client = set_up_ssdp_client()
        ssdp_inventory = SsdpInventory(ssdp_client)

        # When
        devices = list(ssdp_inventory.get_devices(usn_filter='^testid:.*'))

        # Then
        expected = [
            {'name': 'device-1', 'host': 'host-1'},
            {'name': 'device-3', 'host': 'host-3'}
        ]
        self.assertCountEqual(expected, devices)

    def test_returns_devices_when_nt_is_filtered(self):
        # Given
        ssdp_client = set_up_ssdp_client()
        ssdp_inventory = SsdpInventory(ssdp_client)

        # When
        devices = list(ssdp_inventory.get_devices(nt_filter='^test:device$'))

        # Then
        expected = [
            {'name': 'device-1', 'host': 'host-1'},
            {'name': '01234567', 'host': 'host-2'}
        ]
        self.assertCountEqual(expected, devices)

    def test_returns_device_when_usn_and_nt_is_filtered(self):
        # Given
        ssdp_client = set_up_ssdp_client()
        ssdp_inventory = SsdpInventory(ssdp_client)

        # When
        devices = list(ssdp_inventory.get_devices(usn_filter='^testid:.*', nt_filter='^test:device$'))

        # Then
        expected = [
            {'name': 'device-1', 'host': 'host-1'}
        ]
        self.assertCountEqual(expected, devices)


def set_up_ssdp_client():
    ssdp_client = MagicMock(spec=SSDPClient)
    ssdp_client.m_search.return_value = [
        {'usn': 'testid:device-1', 'nt': 'test:device', 'location': 'host-1'},
        {'usn': 'uuid:01234567', 'nt': 'test:device', 'location': 'host-2'},
        {'usn': 'testid:device-3', 'nt': 'test:service', 'location': 'host-3'}
    ]
    return ssdp_client


if __name__ == "__main__":
    unittest.main()
