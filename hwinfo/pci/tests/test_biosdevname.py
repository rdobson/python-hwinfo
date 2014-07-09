"""Module for unittesting biosdevname methods"""

import unittest
from hwinfo.pci.biosdevname import *

DATA_DIR = 'hwinfo/pci/tests/data'

class BiosdevnameDSingleDeviceParserTests(unittest.TestCase):

    RAW_DATA = """
BIOS device: eth0
Kernel name: eth0
Permanent MAC: 6C:AE:8B:22:B7:CA
Assigned MAC : 6C:AE:8B:22:B7:CA
Driver: igb
Driver version: 5.2.5
Firmware version: 1.52.0
Bus Info: 0000:06:00.0
PCI name      : 0000:06:00.0
PCI Slot      : embedded
SMBIOS Device Type: Ethernet
SMBIOS Instance: 2
SMBIOS Label: Intel i350
sysfs Index: 2
sysfs Label: Intel i350
Embedded Index: 1"""

    DATA_REC = {
        'bios_device': 'eth0',
        'kernel_name': 'eth0',
        'permanent_mac': '6C:AE:8B:22:B7:CA',
        'assigned_mac': '6C:AE:8B:22:B7:CA',
        'driver': 'igb',
        'driver_version': '5.2.5',
        'firmware_version': '1.52.0',
        'bus_info': '0000:06:00.0',
        'pci_name': '0000:06:00.0',
        'smbios_device_type': 'Ethernet',
        'smbios_instance': '2',
        'smbios_label': 'Intel i350',
        'sysfs Index': '2',
        'sysfs Label': 'Intel i350',
        'Embedded Index': '1',
    }


    def setUp(self):
        self.parser = BiosdevnameDParser(self.RAW_DATA)

    def _assert_equal(self, key):
        rec = self.parser.parse_items()[0]
        return self.assertEqual(rec[key], self.DATA_REC[key])

    def test_biosdevname_bios_device(self):
        return self._assert_equal('bios_device')

    def test_biosdevname_kerenl_name(self):
        return self._assert_equal('kernel_name')

    def test_biosdevname_driver(self):
        return self._assert_equal('driver')

    def test_biosdevname_driver_version(self):
        return self._assert_equal('driver_version')

    def test_biosdevname_firmware_version(self):
        return self._assert_equal('firmware_version')

class BiosdevnameDMultiDeviceTests(unittest.TestCase):

    DATA_FILE = "%s/%s" % (DATA_DIR, 'biosdevname-d')

    def setUp(self):
        fh = open(self.DATA_FILE)
        sample_data = fh.read()
        fh.close()
        self.parser = BiosdevnameDParser(sample_data)

    def test_parse_correct_number_of_devices(self):
        items = self.parser.parse_items()
        self.assertEqual(len(items), 12)

    def test_count_number_of_be2net_devices(self):
        items = self.parser.parse_items()
        count = 0
        for item in items:
            if item['driver'] == 'be2net':
                count = count + 1

        self.assertEqual(count, 4)

    def test_driver_versions_match(self):
        items = self.parser.parse_items()
        for item in items:
            if item['driver'] == 'be2net':
                self.assertEqual(item['driver_version'], '4.6.62.0u')
                self.assertEqual(item['firmware_version'], '4.2.412.0')
            elif item['driver'] == 'igb':
                self.assertEqual(item['driver_version'], '5.2.5')
                self.assertEqual(item['firmware_version'], '1.52.0')
