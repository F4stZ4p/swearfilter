# coding: utf-8


__author__ = 'Polkisss'
__license__ = 'MIT'

import re
from inspect import getfile
from os import environ
from os import path

from .settingswriter import Config


class Filter:
    def __init__(self, messsage: str):
        """
        Scanning message for words.

        Example:

            from swearfilter import Filter

            if __name__ == '__main__':
                f = Filter('Your text')
                print(f.examine())


        :param messsage:
            Your text to scan.
        """
        self.msg = messsage.lower().replace('ё', 'е').replace('й', 'и')
        self.reg_samples = {}

        location = path.dirname(getfile(Config))

        def mkway(x: str):
            return path.join(location, x)

        self._tmp = path.join(environ['TEMP'], '.~swfilter_temp~')

        # Configuration variables
        self.blacklist = Config(mkway('blacklist.txt')).get()['words']
        self.whitelist = Config(mkway('whitelist.txt')).get()['whitelist']
        self.other = Config(mkway('other.txt')).get()

    def examine(self):
        """
        Scan for swear words.
        :return:
            <bool>
        """

        self._load_temp()
        self._make_regex()  # caching
        self._dump_temp()

        for word in self.whitelist:
            self.msg = self.msg.replace(word, '')

        for ex in self.other['special']:
            self.msg = self.msg.replace(ex, '')

        for kw in self.reg_samples:
            match = re.findall(self.reg_samples[kw], self.msg)
            if match:
                return True

        return False

    def _make_regex(self):
        """
        Makes regex samples from a blacklist
        :return:
        """

        for word in self.blacklist:  # idk whats going on

            if word in self.reg_samples:
                continue

            sample = []
            groups = []

            for char in word:
                tmp = ''
                for alt_chars in self.other['symbols'][char]:
                    for alt_char in alt_chars:
                        tmp += alt_char
                groups.append('[' + tmp + ']+')

            for i in groups:
                sample.append(i)
                sample.append(self.other['trash'])

            sample = ''.join(sample)

            self.reg_samples[word] = sample

    def _load_temp(self):
        try:
            self.reg_samples = eval(open(self._tmp, 'r', encoding='utf-8').read())
        except FileNotFoundError:
            self._dump_temp()

    def _dump_temp(self):
        with open(self._tmp, 'w', encoding='utf-8') as f:
            f.write(str(self.reg_samples))
