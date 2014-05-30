"""Module for inspecting PCI device info"""

import re

class ParserException(Exception):
    pass


class CommandParser(object):

    ITEM_REGEXS = []
    ITEM_SEPERATOR = False
    DATA = None
    MUST_HAVE_FIELDS = []

    def parse_item(self, item):
        rec = {}
        for regex in self.ITEM_REGEXS:
            match = re.search(regex, item)
            if match:
                rec = dict(rec.items() + match.groupdict().items())

        return rec

    def parse(self):
        if not self.ITEM_SEPERATOR:
            return self.parse_item(self.DATA)
        else:
            recs = []
            for data in self.DATA.split(self.ITEM_SEPERATOR):
                rec = self.parse_item(data)
                recs.append(rec)
            return recs


class LspciVVParser(CommandParser):
    """Parser object for the output of lspci -vv"""

    ITEM_REGEXS = [
        r'(?P<pci_device_bus_id>([0-9][0-9]:[0-9][0-9]\.[0-9]))\ (?P<pci_device_type>[\w\ ]*):\ (?P<pci_device_string>(.*))\n',
        r'Product\ Name:\ (?P<pci_device_vpd_product_name>(.)*)\n',
        r'Subsystem:\ (?P<pci_device_sub_string>(.)*)\n',
    ]

    ITEM_SEPERATOR = r'^\n'

    MUST_HAVE_FIELDS = [
        'pci_device_bus_id',
        'pci_device_type',
        'pci_device_string',
    ]
