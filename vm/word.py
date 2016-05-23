# encoding=utf-8
from functools import reduce

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
            int((u_num >> shift) & mask) for shift in range(24, -1, -6)
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
        is_word_len = len(word_list) == 6
        is_word_sign = word_list[0] in (1, -1)
        is_word_byte = all([0 <= byte < MAX_BYTE for byte in word_list[1:6]])
        return is_word_len and is_word_sign and is_word_byte

    def __getitem__(self, x):
        if isinstance(x, slice):
            return self.getslice(x.start, x.stop)
        else:
            return self.word_list[x]

    def __setitem__(self, x, value):
        if isinstance(x, slice):
            self.setslice(x.start, x.stop, value)
        else:
            self.word_list[x] = value

    def getslice(self, l, r):
        """get a part of a word

        On all operations when a partial field is used as an input, the sign
        is used if it is a part of the filed, otherwise the sign + is
        understood. The field is shifted over to the right-hand part of the
        register as it is loaded.

        Hence suppose the original word w equals "- 01 16 03 05 04". Then

        w[0:5]  "- 01 16 03 05 04"
        w[1:5]  "+ 01 16 03 05 04"
        w[3:5]  "+ 00 00 03 05 04"
        w[0:3]  "- 00 00 01 16 03"
        w[4:4]  "+ 00 00 00 00 05"
        w[0:0]  "- 00 00 00 00 00"
        w[1:1]  "+ 00 00 00 00 01"

        This method would be used in instructions like LDA, LDX, LDi and so on.

        :param l:
        :param r:
        :return:
        """
        l = max(l, 0) if l is not None else 0
        r = min(r, 5) if r is not None else 5
        new = Word()
        if l == 0:
            new[0] = self[0]
        for i in range(r, max(l - 1, 0), -1):
            new[5 - r + i] = self[i]
        return new

    def setslice(self, l, r, value):
        """ set a put of a word

        This method would be used in instructions like STA, STX, and so on.

        On a store operation the field F has the opposite significance from
        the load operation: THe number of bytes in the field is taken from
        the right-hand portion of the register and shifted left if necessary
        to be inserted in the proper field of CONTENTS(M). THe sign is not
        altered unless it is part of the field.

        For example,

        w1 = ""

        :param l:
        :param r:
        :param value:
        :return:
        """
        l = max(l, 0) if l is not None else 0
        r = min(r, 5) if r is not None else 5
        word = Word(value)
        if l == 0:
            self[0] = word[0]
        for i in range(r, max(l - 1, 0), -1):
            self[i] = word[5 - r + i]

    def is_zero(self):
        return self.word_list[1:] == ([0] * 5)

    def __eq__(self, cmp_word):
        """to tell if tow word is equal

        :param cmp_word:
        :return:
        """
        if self.is_zero() and cmp_word.is_zero():
            return True
        return True if all(
            self[i] == cmp_word[i] for i in range(0, 6)) else False

    def __ne__(self, cmp_word):
        return not self.__eq__(cmp_word)

    def __str__(self):
        return reduce(lambda x, y: "%s %02i" % (x, y), self.word_list[1:6],
                      "+" if self[0] == 1 else "-")

    __repr__ = __str__

    def addr_str(self):
        return "%s %04i %02i %02i %02i" % tuple(
            ["+" if self[0] == 1 else "-",
             self[1] * MAX_BYTE + self[2]] + self.word_list[3:])

    def __init__(self, obj=None):
        """initialize a word by four ways.

        the usage is quite like constructor overload in C++.
        :param obj:
        """
        if obj is None:
            self.word_list = [+1, 0, 0, 0, 0, 0]
        elif isinstance(obj, list) or isinstance(obj, tuple):
            self.word_list = list(obj)
        elif isinstance(obj, int):
            self.word_list = self.from_dec(obj)
        elif isinstance(obj, Word):
            self.word_list = obj.word_list[:]
