from vm_errors import *

MAX_BYTE = 64


class Word:
    """A word in MIX is five adjacent bytes plus (+/-)

    What's a byte? Today a byte is universally regarded as being an 8-bit
    quantity. The Art of Computer Programming (TAOCP) was written with the
    assumption that a byte could be something entirely different, in this case 6
    bits. However, it is not defined by the number of bits but rather the
    range of values it is capable of representing. In MIX a byte must be
    capable of containing at least 64 distinct values(0-63). Further,
    each byte contains at most 100 distinct values. Hence on a binary computer (
    MIX can be binary or decimal) we require 6 bits.

    But in this implementation, a byte is capable of containing exactly 64
    distinct values.

    """

    @staticmethod
    def sign(x):
        return 1 if x >= 0 else -1

    @staticmethod
    def from_dec(num):
        """convert a decimal number to a word

        :param num: a decimal number
        :return: a word
        """
        mask = MAX_BYTE - 1  # 1<<6 - 1
        u_num = abs(num)
        return [Word.sign(num)] + [
            int((u_num >> shift) & mask) for shift in xrange(24, -1, -6)
            ]  # 24 = 6 * (5-1)

    @staticmethod
    def norm_2bytes(addr):
        """truncate the last two bytes and the sign

        :param addr: a decimal number, may be an address
        :return: a decimal number
        """
        return Word.sign(addr) * (abs(addr) % MAX_BYTE ** 2)

    def __int__(self):
        """transfer a word to an int

        :return: a decimal number
        """
        return self.word_list[0] * reduce(
            lambda x, y: (x << 6) | y, self.word_list[1:], 0)

    @staticmethod
    def is_word_list(word_list):
        """to tell if word_list is a word or not.

        :param word_list: a list
        :return: bool. True if word_list is a word
        """
        return len(word_list) == 6 \
               and word_list[0] in (1, -1) \
               and all([0 <= byte < MAX_BYTE for byte in word_list[1:6]])

    def __getitem__(self, x):
        return self.word_list[x]

    def __setitem__(self, x, value):
        self.word_list[x] = value

    def __getslice__(self, l, r):
        l = max(l, 0)
        r = min(r, 5)
        new = Word()
        if l == 0:
            new[0] = self[0]
        for i in xrange(r, max(l - 1, 0), -1):
            new[5 - r + i] = self[i]
        return new

    def __setslice__(self, l, r, value):
        l = max(l, 0)
        r = min(r, 5)
        word = Word(value)
        if l == 0:
            self[0] = word[0]
        for i in xrange(r, max(l - 1, 0), -1):
            self[i] = word[5 - r + i]

    def is_zero(self):
        return self.word_list[1:] == ([0] * 5)

    def __cmp__(self, cmp_word):
        if self.is_zero() and cmp_word.is_zero():
            return 0
        return 0 if all(self[i] == cmp_word[i] for i in xrange(0, 6)) else 1

    def __str__(self):
        return reduce(lambda x, y: "%s %02i" % (x, y), self.word_list[1:6],
                      "+" if self[0] == 1 else "-")

    def addr_str(self):
        return "%s %04i %02i %02i %02i" % tuple(
            ["+" if self[0] == 1 else "-",
             self[1] * MAX_BYTE + self[2]] + self.word_list[3:])

    def __init__(self, obj=None):
        if obj is None:
            self.word_list = [+1, 0, 0, 0, 0, 0]
        elif isinstance(obj, list) or isinstance(obj, tuple):
            self.word_list = list(obj)
        elif isinstance(obj, int) or isinstance(obj, long):
            self.word_list = self.from_dec(obj)
        elif isinstance(obj, Word):
            self.word_list = obj.word_list[:]
