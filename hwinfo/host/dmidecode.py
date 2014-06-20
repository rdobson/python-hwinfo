"""Module for host related info"""

from hwinfo.util import CommandParser

class DmidecodeParser(CommandParser):

    ITEM_REGEXS = [
        # BIOS Info
        r'BIOS\ Information\n(.)*Vendor:\ (?P<bios_vendor_name>.*)\n',
        r'BIOS\ Information\n(.)*\n\tVersion:\ (?P<bios_version>.*)\n',
        r'BIOS\ Information\n(.)*\n(.)*\n\tRelease\ Date:\ (?P<bios_release_date>.*)\n',
        # System Info
        r'System\ Information\n\tManufacturer:\ (?P<system_manufacturer>.*)\n',
        r'System\ Information\n(.)*\n\tProduct\ Name:\ (?P<system_product_name>.*)\n',
        r'System\ Information\n(.)*\n(.)*\n(.)*\n\tSerial\ Number:\ (?P<system_serial_number>.*)\n',
        r'System\ Information\n(.)*\n(.)*\n(.)*\n(.)*\n\tUUID:\ (?P<system_uuid>.*)\n',
    ]


