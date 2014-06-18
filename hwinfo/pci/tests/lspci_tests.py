"""Unit tests for the lspci module"""

import unittest
from hwinfo.pci.lspci import *

DATA_DIR = 'hwinfo/pci/tests/data'

class TestSingleDeviceVVParse(unittest.TestCase):

    SAMPLE_DEVICE_FILE = "%s/single_network_device_lspci_vv" % DATA_DIR
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
        fh = open(self.SAMPLE_DEVICE_FILE)
        data = fh.read()
        fh.close()
        self.parser = LspciVVParser(data)

    def _assert_rec_key(self, rec, key):
        self.assertEquals(rec[key], self.DEVICE_REC[key])

    def test_pci_device_string(self):
        rec = self.parser.parse_items().pop()
        self._assert_rec_key(rec, 'pci_device_string')

    def test_pci_device_bus_id(self):
        rec = self.parser.parse_items().pop()
        self._assert_rec_key(rec, 'pci_device_bus_id')

    def test_pci_device_type(self):
        rec = self.parser.parse_items().pop()
        self._assert_rec_key(rec, 'pci_device_type')

    def test_pci_device_sub_string(self):
        rec = self.parser.parse_items().pop()
	self._assert_rec_key(rec, 'pci_device_sub_string')

    def test_pci_device_vpd_product_name(self):
        rec = self.parser.parse_items().pop()
	self._assert_rec_key(rec, 'pci_device_vpd_product_name')

class TestMultiDeviceVVParse(unittest.TestCase):

    SAMPLE_DEVICE_FILE = "%s/lspci_vv" % DATA_DIR

    def setUp(self):
        fh = open(self.SAMPLE_DEVICE_FILE)
        data = fh.read()
        fh.close()
        self.parser = LspciVVParser(data)

    def test_parse_all_devices(self):
        recs = self.parser.parse_items()
        self.assertEqual(len(recs), 58)

class TestSingleDeviceNParse(unittest.TestCase):

    DATA = "ff:10.5 0880: 8086:0eb5 (rev 04)"

    DEVICE_REC = {
        'pci_device_bus_id': 'ff:10.5',
        'pci_vendor_id': '8086',
        'pci_device_id': '0eb5',
        'pci_device_type_id': '0880',
    }

    def setUp(self):
        self.parser = LspciNParser(self.DATA)
        self.rec = self.parser.parse_items().pop()

    def _assert_rec_key(self, key):
        self.assertEquals(self.rec[key], self.DEVICE_REC[key])

    def test_pci_device_bus_id(self):
        self._assert_rec_key('pci_device_bus_id')

    def test_pci_vendor_id(self):
        self._assert_rec_key('pci_vendor_id')

    def test_pci_device_id(self):
        self._assert_rec_key('pci_device_id')

    def test_pci_device_type_id(self):
        self._assert_rec_key('pci_device_type_id')

class TestMultiDeviceNParse(unittest.TestCase):
 
    SAMPLE_DEVICE_FILE = "%s/lspci_n" % DATA_DIR

    def setUp(self):
        fh = open(self.SAMPLE_DEVICE_FILE)
        data = fh.read()
        fh.close()
        self.parser = LspciNParser(data)

    def test_parse_all_devices(self):
        recs = self.parser.parse_items()
        self.assertEqual(len(recs), 171)
