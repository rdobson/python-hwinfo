"""Core PCI module"""

class PCIDevice(object):

    def __init__(self, record):
        self.rec = record

    def lookup_value(self, k):
        return self.rec[k]

    def get_device_name(self):
        name = self.lookup_value('pci_device_name')
        if name == 'Device':
            # If the input has come from lspci, this is the value for
            # not being able to find a key in the pciids db.
            return 'unknown [%s]' % self.get_device_id()
        else:
            return name


    def get_device_id(self):
        return self.lookup_value('pci_device_id')

    def get_vendor_name(self):
        return self.lookup_value('pci_vendor_name')

    def get_vendor_id(self):
        return self.lookup_value('pci_vendor_id')

    def get_subdevice_name(self):
        name = self.lookup_value('pci_subdevice_name')
        if name == 'Device':
            # If the input has come from lspci, this is the value for
            # not being able to find a key in the pciids db.
            return 'unknown [%s]' % self.get_subdevice_id()
        else:
            return name

    def get_subdevice_id(self):
        return self.lookup_value('pci_subdevice_id')

    def get_subvendor_name(self):
        return self.lookup_value('pci_subvendor_name')

    def get_subvendor_id(self):
        return self.lookup_value('pci_subvendor_id')

    def get_pci_id(self):
        return "%s:%s %s:%s" % (
            self.lookup_value('pci_vendor_id'),
            self.lookup_value('pci_device_id'),
            self.lookup_value('pci_subvendor_id'),
            self.lookup_value('pci_subdevice_id'),
        )

    def is_subdevice(self):
        return 'pci_subvendor_id' in self.rec and 'pci_subdevice_id' in self.rec

    def get_info(self):

        if self.is_subdevice():
            return "%s %s (%s %s)" % (self.get_subvendor_name(), self.get_subdevice_name(), self.get_vendor_name(), self.get_device_name())
