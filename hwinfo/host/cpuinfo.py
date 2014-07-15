"""Module for parsing the output of /proc/cpuinfo"""

from hwinfo.util import CommandParser

REGEX_TEMPLATE = r'%s([\ \t])+\:\ (?P<%s>.*)'

class CPUInfoParser(CommandParser):

    ITEM_SEPERATOR = "\n\n"

    ITEM_REGEXS = [
        REGEX_TEMPLATE % ('processor', 'processor'),
        REGEX_TEMPLATE % ('vendor_id', 'vendor_id'),
        REGEX_TEMPLATE % (r'cpu\ family', 'cpu_family'),
        REGEX_TEMPLATE % ('model', 'model'),
        REGEX_TEMPLATE % (r'model\ name', 'model_name'),
        REGEX_TEMPLATE % ('stepping', 'stepping'),
        REGEX_TEMPLATE % ('microcode', 'microcode'),
        REGEX_TEMPLATE % (r'cpu\ MHz', 'cpu_mhz'),
        REGEX_TEMPLATE % (r'cache\ size', 'cache_size'),
        REGEX_TEMPLATE % (r'fpu', 'fpu'),
        REGEX_TEMPLATE % (r'fpu_exception', 'fpu_exception'),
        REGEX_TEMPLATE % (r'cpuid\ level', 'cpuid_level'),
        REGEX_TEMPLATE % (r'wp', 'wp'),
        REGEX_TEMPLATE % (r'flags', 'flags'),
        REGEX_TEMPLATE % (r'bogomips', 'bogomips'),
        REGEX_TEMPLATE % (r'clflush\ size', 'clflush_size'),
        REGEX_TEMPLATE % (r'cache_alignment', 'cache_alignment'),
        REGEX_TEMPLATE % (r'address\ sizes', 'address_sizes'),
        REGEX_TEMPLATE % (r'power\ management', 'power_management'),
    ]
