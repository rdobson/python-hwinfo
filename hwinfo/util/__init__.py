"""Util Module for functionality shared between modules"""

import re

class CommandParser(object):
    """Object for extending to parse command outputs"""

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

