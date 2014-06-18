"""Util Module for functionality shared between modules"""

import re

class CommandParser(object):
    """Object for extending to parse command outputs"""

    ITEM_REGEXS = []
    ITEM_SEPERATOR = False
    DATA = None
    MUST_HAVE_FIELDS = []

    def __init__(self, data, regexs=None, seperator=None):
        self.set_data(data)
        self.set_regexs(regexs)
        self.set_seperator(seperator)

    def set_data(self, data):
        self.DATA = data.strip()

    def set_regexs(self, regexs):
        if regexs:
            self.ITEM_REGEXS = regexs

    def set_seperator(self, seperator):
        if seperator:
            self.ITEM_SEPERATOR = seperator

    def parse_item(self, item):
        rec = {}
        for regex in self.ITEM_REGEXS:
            match = re.search(regex, item)
            if match:
                rec = dict(rec.items() + match.groupdict().items())

        return rec

    def parse_items(self):
        if not self.ITEM_SEPERATOR:
            return [self.parse_item(self.DATA)]
        else:
            recs = []
            for data in self.DATA.split(self.ITEM_SEPERATOR):
                rec = self.parse_item(data)
                recs.append(rec)
            return recs

    def parse(self):
        if self.ITEM_SEPERATOR:
            raise Exception("A seperator has been specified: '%s'. " + \
            "Please use 'parse_items' instead")

        return self.parse_item(self.DATA)
