"""Unit tests for the lspci module"""

import unittest
from pci.lspci import *

class TestSingleDeviceVVParse(unittest.TestCase):

    SAMPLE_DEVICE_FILE = 'pci/tests/data/single_network_device_lspci_vv'
    DEVICE_DATA = ""

    DEVICE_REC = {
        'pci_device_string': 'Broadcom Corporation NetXtreme II BCM5716 Gigabit Ethernet (rev 20)',
	'pci_device_type': 'Ethernet controller',
	'pci_device_bus_id': '02:00.0',
	'pci_device_sub_string': 'Dell Device 0488',
	'pci_device_vpd_product_name': 'Broadcom NetXtreme II Ethernet Controller',
        }

    def setUp(self):
        # Load device data from sample file
	self.parser = LspciVVParser()
        fh = open(self.SAMPLE_DEVICE_FILE)
        self.DEVICE_DATA = fh.read()
        fh.close()

    def _assert_rec_key(self, rec, key):
        self.assertEquals(rec[key], self.DEVICE_REC[key])

    def test_pci_device_string(self):
        rec = self.parser.parse_item(self.DEVICE_DATA)
        self._assert_rec_key(rec, 'pci_device_string')

    def test_pci_device_bus_id(self):
        rec = self.parser.parse_item(self.DEVICE_DATA)
        self._assert_rec_key(rec, 'pci_device_bus_id')

    def test_pci_device_type(self):
        rec = self.parser.parse_item(self.DEVICE_DATA)
        self._assert_rec_key(rec, 'pci_device_type')

    def test_pci_device_sub_string(self):
        rec = self.parser.parse_item(self.DEVICE_DATA)
	self._assert_rec_key(rec, 'pci_device_sub_string')

    def test_pci_device_vpd_product_name(self):
        rec = self.parser.parse_item(self.DEVICE_DATA)
	self._assert_rec_key(rec, 'pci_device_vpd_product_name')
