"""Module for inspecting PCI device info"""

from hwinfo.util import CommandParser

class ParserException(Exception):
    pass

class LspciVVParser(CommandParser):
    """Parser object for the output of lspci -vv"""

    ITEM_REGEXS = [
        r'(?P<pci_device_bus_id>([0-9][0-9]:[0-9][0-9]\.[0-9]))\ (?P<pci_device_class_name>[\w\ ]*):\ (?P<pci_device_string>(.*))\n',
        r'Product\ Name:\ (?P<pci_device_vpd_product_name>(.)*)\n',
        r'Subsystem:\ (?P<pci_device_sub_string>(.)*)\n',
    ]

    ITEM_SEPERATOR = "\n\n"

    MUST_HAVE_FIELDS = [
        'pci_device_bus_id',
        'pci_device_class_name',
        'pci_device_string',
    ]

class LspciNParser(CommandParser):
    """Parser object for the output of lspci -n"""

    #ff:0d.1 0880: 8086:0ee3 (rev 04)
    ITEM_REGEXS = [
        r'(?P<pci_device_bus_id>([0-9a-f][0-9a-f]:[0-9a-f][0-9a-f]\.[0-9a-f]))\ (?P<pci_device_class>[0-9a-f]{4}):\ (?P<pci_vendor_id>[0-9a-f]{4}):(?P<pci_device_id>[0-9a-f]{4})',
    ]

    ITEM_SEPERATOR = "\n"

    MUST_HAVE_FIELDS = [
        'pci_device_bus_id',
        'pci_device_id',
        'pci_vendor_id',
        'pci_device_class',
    ]


LABEL_REGEX = r'[\w+\ \.\-\/]+'
CODE_REGEX = r'[0-9a-fA-F]{4}'

class LspciNNMMParser(CommandParser):
    """Parser object for the output of lspci -nnmm"""

    #02:00.1 "Ethernet controller [0200]" "Broadcom Corporation [14e4]" "NetXtreme II BCM5716 Gigabit Ethernet [163b]" -r20 "Dell [1028]" "Device [02a3]"

    ITEM_REGEXS = [
        r'(?P<pci_device_bus_id>([0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-9a-fA-F]))\ "(?P<pci_device_class_name>' + LABEL_REGEX + r')\ \[(?P<pci_device_class>' + CODE_REGEX + r')\]"' \
        + r'\ "(?P<pci_vendor_name>' + LABEL_REGEX + r')\ \[(?P<pci_vendor_id>' + CODE_REGEX + r')\]"\ "(?P<pci_device_name>' + LABEL_REGEX + r')\ \[(?P<pci_device_id>' + CODE_REGEX + r')\]"' \
        + r'\ .*\ "((?P<pci_subvendor_name>' + LABEL_REGEX + r')\ \[(?P<pci_subvendor_id>' + CODE_REGEX + r')\])*"\ "((?P<pci_subdevice_name>' + LABEL_REGEX + r')\ \[(?P<pci_subdevice_id>' + CODE_REGEX + r')\])*',
    ]

    ITEM_SEPERATOR = "\n"
