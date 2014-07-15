"""Module for unittesting dmidecode methods"""

import unittest
from hwinfo.host.cpuinfo import CPUInfoParser

DATA_DIR = 'hwinfo/host/tests/data'

class CPUInfoParserTests(unittest.TestCase):

    DATA = """
processor	: 0
vendor_id	: GenuineIntel
cpu family	: 6
model		: 30
model name	: Intel(R) Xeon(R) CPU           X3430  @ 2.40GHz
stepping	: 5
microcode	: 0x3
cpu MHz		: 2394.052
cache size	: 8192 KB
fpu		: yes
fpu_exception	: yes
cpuid level	: 11
wp		: yes
flags		: fpu de tsc msr pae mce cx8 apic sep mca cmov pat clflush acpi mmx fxsr sse sse2 ss ht syscall nx lm constant_tsc rep_good nopl nonstop_tsc pni monitor vmx est ssse3 cx16 sse4_1 sse4_2 popcnt hypervisor lahf_lm dtherm tpr_shadow vnmi flexpriority ept vpid
bogomips	: 4788.10
clflush size	: 64
cache_alignment	: 64
address sizes	: 36 bits physical, 48 bits virtual
power management:
"""

    DATA_REC = {
        'processor': '0',
        'vendor_id': 'GenuineIntel',
        'cpu_family': '6',
        'model': '30',
        'model_name': 'Intel(R) Xeon(R) CPU           X3430  @ 2.40GHz',
        'stepping': '5',
        'microcode': '0x3',
        'cpu_mhz': '2394.052',
        'cache_size': '8192 KB',
        'fpu': 'yes',
        'fpu_exception': 'yes',
        'cpuid_level': '11',
        'wp': 'yes',
        'flags': 'fpu de tsc msr pae mce cx8 apic sep mca cmov pat clflush acpi mmx fxsr sse sse2 ss ht syscall nx lm constant_tsc rep_good nopl nonstop_tsc pni monitor vmx est ssse3 cx16 sse4_1 sse4_2 popcnt hypervisor lahf_lm dtherm tpr_shadow vnmi flexpriority ept vpid',
        'bogomips': '4788.10',
        'clflush_size': '64',
        'cache_alignment': '64',
        'address_sizes': '36 bits physical, 48 bits virtual',
        'power_management': '',
    }


    def setUp(self):
        self.parser = CPUInfoParser(self.DATA.strip())

    def _assert_equal(self, key):
        rec = self.parser.parse()
        return self.assertEqual(rec[key], self.DATA_REC[key])

    def test_cpuinfo_processor(self):
        return self._assert_equal('processor')

    def test_vendor_id(self):
        return self._assert_equal('vendor_id')

    def test_cpu_family(self):
        return self._assert_equal('cpu_family')

    def test_model(self):
        return self._assert_equal('model')

    def test_model_name(self):
        return self._assert_equal('model_name')

    def test_stepping(self):
        return self._assert_equal('stepping')

    def test_microcode(self):
        return self._assert_equal('microcode')

    def test_cpu_mhz(self):
        return self._assert_equal('cpu_mhz')

    def test_cache_size(self):
        return self._assert_equal('cache_size')

    def test_fpu(self):
        return self._assert_equal('fpu')

    def test_fpu_exception(self):
        return self._assert_equal('fpu_exception')

    def test_cpuid_level(self):
        return self._assert_equal('cpuid_level')

    def test_wp(self):
        return self._assert_equal('wp')

    def test_flags(self):
        return self._assert_equal('flags')

    def test_bogomips(self):
        return self._assert_equal('bogomips')

    def test_clflush_size(self):
        return self._assert_equal('clflush_size')

    def test_cache_alignment(self):
        return self._assert_equal('cache_alignment')

    def test_address_sizes(self):
        return self._assert_equal('address_sizes')
