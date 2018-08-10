# coding: utf-8


__author__ = 'Polkisss'
__license__ = 'MIT'

import re
from os import environ
from os import path

from .settingswriter import Config


class Message:
    """
    Represents Filter.msg as object

    """
    __slots__ = ['trip_amount', 'reaction', 'message', 'hasWords']

    def __init__(self, trip_amount, reaction, message):
        self.trip_amount = trip_amount
        self.reaction = reaction
        self.message = message
        self.hasWords = trip_amount > 0

    def __bool__(self):
        return self.hasWords


class Filter:
    __slots__ = ['msg', 'reg_samples', '_tmp', '_blacklist', '_whitelist', '_other', 'priority_temp']

    def __init__(self, messsage: str, *, tempfile=None):
        """
        Scanning message for words.

        Example:

            import swearfilter as sf

            if __name__ == '__main__':
                foo = sf.Filter('message').scan()
                print('%s, %s' % (foo.hasWords, foo.message))

        Output:
            False, message


        :param messsage:
            Your text to scan.
        """

        self.msg = messsage.lower().replace('ё', 'е').replace('й', 'и')
        self.reg_samples = {}

        location = path.dirname(__file__)

        def mkway(x: str):
            return path.join(location, x)

        if tempfile:
            self._tmp = tempfile
        else:
            try:
                self._tmp = path.join(environ['TEMP'], '.~swfilter_temp~')  # Windows
            except KeyError:  # dividing by OS
                self._tmp = '/tmp/.~swfilter_temp~'

        # Configuration variables
        self._blacklist = Config(mkway('blacklist.txt')).get()['words']
        self._whitelist = Config(mkway('whitelist.txt')).get()['whitelist']
        self._other = Config(mkway('other.txt')).get()

    def scan(self):
        """
        Scan for swear words.
        :return:
            <bool>
        """

        self._load_temp()
        self._make_regex()  # caching
        self._dump_temp()

        for word in self._whitelist:
            self.msg = self.msg.replace(word, '')

        trips = 0
        reaction = []
        for kw in self.reg_samples:
            match = re.findall(self.reg_samples[kw], self.msg)
            if match:
                reaction.append({  # some debug info
                    'sample': self.reg_samples[kw],
                    'matched': match[0],
                    'on': kw,
                })
                trips += 1

        return Message(trips, reaction, self.msg, )

    def _make_regex(self):
        """
        Makes regex samples from a blacklist
        :return:
        """

        for word in self._blacklist:  # idk whats going on

            if word in self.reg_samples:
                continue

            sample = []
            groups = []

            for char in word:
                tmp = ''
                for alt_chars in self._other['symbols'][char]:
                    for alt_char in alt_chars:
                        tmp += alt_char
                groups.append('[' + tmp + ']+')

            for i in groups:
                sample.append(i)
                sample.append(self._other['trash'])

            sample = ''.join(sample)

            self.reg_samples[word] = sample

    def __str__(self):
        return self.msg

    def _load_temp(self):
        try:
            self.reg_samples = eval(open(self._tmp, 'r', encoding='utf-8').read())
        except FileNotFoundError:
            self._dump_temp()

    def _dump_temp(self):
        with open(self._tmp, 'w', encoding='utf-8') as f:
            f.write(str(self.reg_samples))
