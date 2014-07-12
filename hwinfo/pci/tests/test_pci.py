"""Module for unittesting the core pci module"""

import unittest
from hwinfo.pci import *

class TestPCIDeviceObject(unittest.TestCase):

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
        self.device = PCIDevice(self.DEVICE_REC)

    def test_get_device_name(self):
        name = self.device.get_device_name()
        self.assertEqual(name, 'NetXtreme II BCM5716 Gigabit Ethernet')

    def test_get_vendor_name(self):
        name = self.device.get_vendor_name()
        self.assertEqual(name, 'Broadcom Corporation')

    def test_get_vendor_id(self):
        name = self.device.get_vendor_id()
        self.assertEqual(name, '14e4')

    def test_get_subdevice_name(self):
        name = self.device.get_subdevice_name()
        self.assertEqual(name, 'unknown [02a3]')

    def test_get_subvendor_name(self):
        name = self.device.get_subvendor_name()
        self.assertEqual(name, 'Dell')

    def test_get_subvendor_id(self):
        name = self.device.get_subvendor_id()
        self.assertEqual(name, '1028')

    def test_get_device_id(self):
        name = self.device.get_device_id()
        self.assertEqual(name, '163b')

    def test_get_subdevice_id(self):
        name = self.device.get_subdevice_id()
        self.assertEqual(name, '02a3')

    def test_get_pci_id(self):
        pciid = self.device.get_pci_id()
        self.assertEqual(pciid, '14e4:163b 1028:02a3')

    def test_is_subdevice(self):
        self.assertTrue(self.device.is_subdevice())

    def test_get_device_info(self):
        info = self.device.get_info()
        self.assertEqual(info, 'Dell unknown [02a3] (Broadcom Corporation NetXtreme II BCM5716 Gigabit Ethernet)')
