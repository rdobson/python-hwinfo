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


class TestSingleDeviceNNMMParse(unittest.TestCase):

    SAMPLE_DATA = '02:00.0 "Ethernet controller [0200]" "Broadcom Corporation [14e4]" "NetXtreme II BCM5716 Gigabit Ethernet [163b]" -r20 "Dell [1028]" "Device [02a3]'

    DEVICE_REC = {
        'pci_device_bus_id': '02:00.0',
        'pci_device_type_id': '0200',
        'pci_device_type_name': 'Ethernet controller',
        'pci_vendor_name': 'Broadcom Corporation',
        'pci_vendor_id': '14e4',
        'pci_device_id': '163b',
        'pci_device_name': 'NetXtreme II BCM5716 Gigabit Ethernet',
        'pci_subvendor_name': 'Dell',
        'pci_subvendor_id': '1028',
        'pci_subdevice_name': 'Device',
        'pci_subdevice_id': '02a3',
    }

    def setUp(self):
        self.parser = LspciNNMMParser(self.SAMPLE_DATA)
        self.rec = self.parser.parse_items()[0]

    def _assert_rec_key(self, key):
        self.assertEquals(self.rec[key], self.DEVICE_REC[key])

    def test_pci_device_bus_id(self):
        self._assert_rec_key('pci_device_bus_id')

    def test_pci_device_type_id(self):
        self._assert_rec_key('pci_device_type_id')

    def test_pci_device_type_name(self):
        self._assert_rec_key('pci_device_type_name')

    def test_pci_vendor_name(self):
        self._assert_rec_key('pci_vendor_name')

    def test_pci_vendor_id(self):
        self._assert_rec_key('pci_vendor_id')

    def test_pci_device_id(self):
        self._assert_rec_key('pci_device_id')

    def test_pci_device_name(self):
        self._assert_rec_key('pci_device_name')

    def test_pci_subvendor_name(self):
        self._assert_rec_key('pci_subvendor_name')

    def test_pci_subdevice_name(self):
        self._assert_rec_key('pci_subdevice_name')

    def test_pci_subdevice_id(self):
        self._assert_rec_key('pci_subdevice_id')

class LsiDeviceParse(TestSingleDeviceNNMMParse):

    SAMPLE_DATA = '03:00.0 "SCSI storage controller [0100]" "LSI Logic / Symbios Logic [1000]" "SAS1068E PCI-Express Fusion-MPT SAS [0058]" -r08 "Dell [1028]" "SAS 6/iR Integrated Blades RAID Controller [1f0f]"'

    DEVICE_REC = {
        'pci_device_bus_id': '03:00.0',
        'pci_device_type_id': '0100',
        'pci_device_type_name': 'SCSI storage controller',
        'pci_vendor_name': 'LSI Logic / Symbios Logic',
        'pci_vendor_id': '1000',
        'pci_device_id': '0058',
        'pci_device_name': 'SAS1068E PCI-Express Fusion-MPT SAS',
        'pci_subvendor_name': 'Dell',
        'pci_subvendor_id': '1028',
        'pci_subdevice_name': 'SAS 6/iR Integrated Blades RAID Controller',
        'pci_subdevice_id': '1f0f',
    }


class IntelUSBControllerDeviceParse(TestSingleDeviceNNMMParse):

    SAMPLE_DATA = '00:1d.0 "USB controller [0c03]" "Intel Corporation [8086]" "5 Series/3400 Series Chipset USB2 Enhanced Host Controller [3b34]" -r05 -p20 "Dell [1028]" "Device [02a3]"'

    DEVICE_REC = {
        'pci_device_bus_id': '00:1d.0',
        'pci_device_type_id': '0c03',
        'pci_device_type_name': 'USB controller',
        'pci_vendor_name': 'Intel Corporation',
        'pci_vendor_id': '8086',
        'pci_device_id': '3b34',
        'pci_device_name': '5 Series/3400 Series Chipset USB2 Enhanced Host Controller',
        'pci_subvendor_name': 'Dell',
        'pci_subvendor_id': '1028',
        'pci_subdevice_name': 'Device',
        'pci_subdevice_id': '02a3',
    }

class TestMultiDeviceNNMMParse(unittest.TestCase):

    SAMPLE_FILE = '%s/lspci-nnmm' % DATA_DIR

    def setUp(self):
        fh = open(self.SAMPLE_FILE)
        data = fh.read()
        fh.close()
        self.parser = LspciNNMMParser(data)

    def test_number_of_devices(self):
        recs = self.parser.parse_items()
        self.assertEqual(len(recs), 37)
