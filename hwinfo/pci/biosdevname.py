"""Module for host related info"""

from hwinfo.util import CommandParser

class BiosdevnameDParser(CommandParser):

    ITEM_SEPERATOR = "\n\n"

    ITEM_REGEXS = [
        r'BIOS\ device:\ (?P<bios_device>.*)\n',
        r'Kernel\ name:\ (?P<kernel_name>.*)\n',
        r'Driver:\ (?P<driver>.*)\n',
        r'Driver\ version:\ (?P<driver_version>.*)\n',
        r'Firmware\ version:\ (?P<firmware_version>.*)\n',
    ]
