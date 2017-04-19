"""Core PCI module"""

class PCIDevice(object):

    NONE_VALUE = 'unknown'

    def __init__(self, record):
        self.rec = record

    def lookup_value(self, k):
        if k in self.rec:
            return self.rec[k]
        else:
            return None

    def _fmt(self, value, wrap=None):
        if not value:
            return self.NONE_VALUE
        else:
            if wrap:
                return "%s%s%s" % (wrap, value, wrap)
            else:
                return value

    def get_device_name(self):
        wrap = None
        name = self.lookup_value('pci_device_name')

        # Fall back to using pci_device_string if it exists.
        if not name:
            name = self.lookup_value('pci_device_string')
            wrap = '-'

        if name == 'Device':
            # If the input has come from lspci, this is the value for
            # not being able to find a key in the pciids db.
            return '[Device %s]' % self.get_device_id()
        else:
            return self._fmt(name, wrap)


    def get_device_id(self):
        return self._fmt(self.lookup_value('pci_device_id'))

    def get_device_bus_id(self):
        return self._fmt(self.lookup_value('pci_device_bus_id'))

    def get_vendor_name(self):
        return self._fmt(self.lookup_value('pci_vendor_name'))

    def get_vendor_id(self):
        return self._fmt(self.lookup_value('pci_vendor_id'))

    def get_subdevice_name(self):
        name = self.lookup_value('pci_subdevice_name')
        wrap = None

        # Fall back to using pci_device_string if it exists.
        if not name:
            name = self.lookup_value('pci_device_sub_string')
            wrap = '-'

        if name == 'Device':
            # If the input has come from lspci, this is the value for
            # not being able to find a key in the pciids db.
            return '[Device %s]' % self.get_subdevice_id()
        else:
            return self._fmt(name, wrap)

    def get_subdevice_id(self):
        return self._fmt(self.lookup_value('pci_subdevice_id'))

    def get_subvendor_name(self):
        return self._fmt(self.lookup_value('pci_subvendor_name'))

    def get_subvendor_id(self):
        return self._fmt(self.lookup_value('pci_subvendor_id'))

    def get_pci_id(self):
        return "%s:%s %s:%s" % (
            self._fmt(self.lookup_value('pci_vendor_id')),
            self._fmt(self.lookup_value('pci_device_id')),
            self._fmt(self.lookup_value('pci_subvendor_id')),
            self._fmt(self.lookup_value('pci_subdevice_id')),
        )

    def get_pci_class(self):
        return self._fmt(self.lookup_value('pci_device_class'))

    def is_subdevice(self):
        return self.lookup_value('pci_subvendor_id') and self.lookup_value('pci_subdevice_id') or self.lookup_value('pci_device_sub_string')

    def get_info(self):

        if self.is_subdevice():
            return "%s %s (%s %s)" % (self.get_subvendor_name(), self.get_subdevice_name(), self.get_vendor_name(), self.get_device_name())
        else:
            return "%s %s" % (self.get_vendor_name(), self.get_device_name())

    def get_rec(self):
        rec = {}
        rec['device_bus_id'] = self.get_device_bus_id()
        rec['vendor_name'] = self.get_vendor_name()
        rec['device_name'] = self.get_device_name()
        rec['vendor_id'] = self.get_vendor_id()
        rec['device_id'] = self.get_device_id()
        rec['class'] = self.get_pci_class()
        rec['subvendor_name'] = self.get_subvendor_name()
        rec['subdevice_name'] = self.get_subdevice_name()
        rec['subvendor_id'] = self.get_subvendor_id()
        rec['subdevice_id'] = self.get_subdevice_id()

        return rec
