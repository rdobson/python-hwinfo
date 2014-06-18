"""Unittests for parser objects"""

import unittest
from hwinfo.util import CommandParser

class TestCommandParser(unittest.TestCase):

    def test_parse_item(self):
        data = 'one two three four: 845 six'
	cp = CommandParser()
	cp.ITEM_REGEXS = [r'four:\ (?P<num>\w+)']
	rec = cp.parse_item(data)
	self.assertEquals(rec['num'], '845')

    def test_parse_items(self):
        data = """
eth0      Link encap:Ethernet  HWaddr f8:b1:56:d5:e6:8c
          inet addr:10.80.3.223  Bcast:10.80.3.255  Mask:255.255.254.0
          inet6 addr: fe80::fab1:56ff:fed5:e68c/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:1848944 errors:0 dropped:0 overruns:0 frame:0
          TX packets:1683421 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:1525454582 (1.5 GB)  TX bytes:1125497021 (1.1 GB)
          Interrupt:20 Memory:fb200000-fb220000

lo        Link encap:Local Loopback
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:16849 errors:0 dropped:0 overruns:0 frame:0
          TX packets:16849 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:3684827 (3.6 MB)  TX bytes:3684827 (3.6 MB)
"""
        regexs = [r'Link encap:(?P<encap>[\w]+)']
	cp = CommandParser(data, regexs, seperator='\n\n')
	recs = cp.parse_items()
	to_match = ['Ethernet', 'Local']
	for rec in recs:
            val = rec['encap']
            to_match.remove(val)

    def test_parse_item(self):
        data = """
eth0      Link encap:Ethernet  HWaddr f8:b1:56:d5:e6:8c
          inet addr:10.80.3.223  Bcast:10.80.3.255  Mask:255.255.254.0
          inet6 addr: fe80::fab1:56ff:fed5:e68c/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:1848944 errors:0 dropped:0 overruns:0 frame:0
          TX packets:1683421 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:1525454582 (1.5 GB)  TX bytes:1125497021 (1.1 GB)
          Interrupt:20 Memory:fb200000-fb220000
"""
        regexs = ['Link encap:(?P<encap>[\w]+)']
        cp = CommandParser(data, regexs)
        rec = cp.parse()
        self.assertEqual(rec['encap'], 'Ethernet')

    def test_parse_item_with_parse_items(self):
        data = """
eth0      Link encap:Ethernet  HWaddr f8:b1:56:d5:e6:8c
          inet addr:10.80.3.223  Bcast:10.80.3.255  Mask:255.255.254.0
          inet6 addr: fe80::fab1:56ff:fed5:e68c/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:1848944 errors:0 dropped:0 overruns:0 frame:0
          TX packets:1683421 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:1525454582 (1.5 GB)  TX bytes:1125497021 (1.1 GB)
          Interrupt:20 Memory:fb200000-fb220000
"""
        regexs = ['Link encap:(?P<encap>[\w]+)']
        cp = CommandParser(data, regexs)
        rec = cp.parse_items()[0]
        self.assertEqual(rec['encap'], 'Ethernet')


    def test_assert_raises_use_parse_items(self):
        data = "thisdoesnotmatter"
        regexs = [r'(?<anything>[\w+])']
        cp = CommandParser(data, regexs, seperator='\n')
        self.assertRaises(Exception, cp.parse)
