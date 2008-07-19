# parse_argument.py

# parses third part of line

# Grammar of mix's arguments (n - means that this function does self.next() in the end):
# + SYMBOL          ::==  string with length from 1 to 10 of digits or alphas (one alpha required)
# +                       also special symbols dH, dF, dB - where "d" is digit
# + NUMBER          ::==  string with length from 1 to 10 of digits
# + DEFINED_SYMBOL  ::==  symbol which was previously defined in source file
# + FUTURE_SYMBOL   ::==  symbol which was nextly defined in source file
# + ALF_WORD        ::==  mix-chars in or not in inverted
# + NONE            ::==  can be missed
# + CUR_ADDR        ::==  "*"
# + S_EXP           ::==  NUMBER | DEFINED_SYMBOL | CUR_ADDR
# + EXP             ::==  [ "+" | "-" ] S_EXP [ ( "+" | "-" | "*" | "/" | "//" | ":" ) S_EXP]*
# + IND_PART       n::==  NONE | ( "," EXP )
# + F_PART         n::==  NONE | ( "(" EXP ")" )
# + W_EXP          n::==  EXP F_PART [ "," EXP F_PART ]*
# + LITERAL         ::==  "=" W_EXP "="
# + ADDR_PART      n::==  NONE | EXP | FUTURE_SYMBOL | LITERAL
# + ARGUMENT        ::== ( ADDR_PART IND_PART F_PART ) |    # if is_instruction(operation)
# +                      W_EXP |        # if operation in("EQU", "ORIG", "CON", "END")
# +                      ALF_WORD       # if operation == "ALF"

from math import *
from operations import *
from errors import *
from memory import Memory

def parse_argument(line, symbol_table, cur_addr, npass = 1):
# + EQUAL           ::==  "="
  return ArgumentParser(line, symbol_table, cur_addr, npass).parse()

class ArgumentParser:
  unary_ops = "+ -".split(" ")
  unary_func = {
    "+":  lambda x : x,
    "-":  lambda x : -x
  }
  binary_ops = "+ - * / // :".split(" ")
  binary_func = {
    "+":  lambda x,y : x + y,
    "-":  lambda x,y : x - y,
    "*":  lambda x,y : x * y,
    "/":  lambda x,y : x / y,
    "//": lambda x,y : (x * 64**5) / y,
    ":":  lambda x,y : 8*x + y
  }

  charset = {
  # table is copied from mdk manual (10, 20, 21 = delta, sigma, pi)
    " ":  0,      "A":  1,      "B":  2,      "C":  3,
    "D":  4,      "E":  5,      "F":  6,      "G":  7,
    "H":  8,      "I":  9,      "~":  10,     "J":  11,
    "K":  12,     "L":  13,     "M":  14,     "N":  15,
    "O":  16,     "P":  17,     "Q":  18,     "R":  19,
    "[":  20,     "#":  21,     "S":  22,     "T":  23,
    "U":  24,     "V":  25,     "W":  26,     "X":  27,
    "Y":  28,     "Z":  29,     "0":  30,     "1":  31,
    "2":  32,     "3":  33,     "4":  34,     "5":  35,
    "6":  36,     "7":  37,     "8":  38,     "9":  39,
    ".":  40,     ",":  41,     "(":  42,     ")":  43,
    "+":  44,     "-":  45,     "*":  46,     "/":  47,
    "=":  48,     "$":  49,     "<":  50,     ">":  51,
    "@":  52,     ";":  53,     ":":  54,     "'":  55
  }

  def __init__(self, line, symbol_table, cur_addr, npass = 1):
    self.line = line
    self.symbol_table = symbol_table
    self.cur_addr = cur_addr
    self.npass = npass
    
    self.split() # create self.tokens and ct=0 (current token)

  def split(self):
    """Create tokens"""
    self.tokens = []
    self.ct = 0 # current token
    s = self.line.argument
    if s is None:
      return
    splitters = ", + - * / : ( ) \" =".split(" ")
    cur_token = ""
    i = 0
    while i < len(s):
      if s[i] not in splitters:
        cur_token += s[i]
      else:
        if s[i] == '"':
          inverted_end = s.find('"', i + 1)
          if inverted_end == -1:
            inverted_end = len(s) - 1
          for word in (cur_token, '"', s[i + 1:inverted_end], '"'):
            if word != '':
              self.tokens.append(word)
          i = inverted_end
        else:
          if cur_token != "": 
            self.tokens.append(cur_token)
          cur_token = ""
          if s[i] == "/" and i + 1 < len(s) and s[i+1] == "/":
            self.tokens.append("//")
            i += 1
          else:
            self.tokens.append(s[i])
      i += 1
    if cur_token != "":
      self.tokens += [cur_token]


  def parse(self):
    """Main parse function"""
    return self.try_argument()

# moving in tokens
  def get(self):
    try:
      return self.tokens[self.ct]
    except:
      return None

  def next(self):
    self.ct += 1

  def look(self):
    try:
      return self.tokens[self.ct + 1]
    except:
      return None

  def get_all_before_this(self):
    return "".join(self.tokens[:self.ct])

  def get_all_forward_from_this(self):
    return "".join(self.tokens[self.ct:])
    
  def get_all_after_this(self):
    return "".join(self.tokens[self.ct+1:])
# moving in tokens


  @staticmethod
  def try_any(seq):
    """Try all functions in seq and return not None result of one of them or None"""
    for f in (seq):
      res = f()
      if res is not None:
        return res
    return None


# all try_*() returns number or None if fails
# and can raise exceptions

  def try_symbol(self):
    if self.get() is not None:
      return self.symbol_table.find(self.get(), self.line.line_number)
    else:
      return None


  def try_number(self):
    if self.get() is not None and 1 <= len(self.get()) <= 10 and self.get().isdigit():
      return int(self.get())
    else:
      return None


  def try_defined_symbol(self):   # Program algorithm is so that difference of symbols destroied.
    return self.try_symbol()      # Init of symbol table - there parsed arguments of directives
                                  # which use only DEFINED_SYMBOLS with symbol table that created
                                  # from defined labels (see algorithm).
  def try_future_symbol(self):    # Assemble - there parsed arguments of instructions
    return self.try_symbol()      # which use any symbols with full symbol table.


  def try_alf_word(self):
    if self.get() == '"':
      # exactly five mix-chars in inverted or
      self.next()
      if self.get() == '"':
        s = ""
      else:
        s = self.get()
        if self.look() != '"':
          raise UnquotedStringError(self.line.argument)
        self.next()
    else:
      # less than six mix-chars not in inverted
      s = self.get()
      if s is None:
        s = ""

    s = s[:5]
    while len(s) < 5:
      s += " "
    # now s - string with len = 5

    word = Memory.positive_zero()
    try:
      for i in xrange(1,6):
        word[i] = self.charset[s[i-1]]
    except KeyError, ch:
      raise InvalidCharError(ch)
    return Memory.mix2dec(word)


  def try_cur_addr(self):
    if self.get() == "*":
      return self.cur_addr
    else:
      return None


  def try_s_exp(self):
    return self.try_any(
      (self.try_number, self.try_defined_symbol, self.try_cur_addr)
    )


  def try_exp(self):
    result = 0

    has_unary = False
    if self.get() in self.unary_ops:
      unary_str = self.get()
      unary = self.unary_func[unary_str]
      has_unary = True
      self.next()
    else:
      unary = lambda x : x # identical function

    s_exp = self.try_s_exp()
    if s_exp is None:
      if has_unary:
        raise ExpectedSExpError(self.get_all_before_this())
      else:
        return None
    result = unary(s_exp)

    while True:
      if self.look() not in self.binary_ops:
        break
      self.next()
      binary = self.binary_func[self.get()]
      self.next()
      s_exp = self.try_s_exp()
      if s_exp is None:
        raise ExpectedSExpError(self.get_all_before_this())
      result = binary(result, s_exp)

    return result


  def try_ind_part(self):
    """This function DO SELF.NEXT()"""
    if self.get() != ",":
      return 0
    else:
      self.next()
      exp = self.try_exp()
      if exp is None:
        raise ExpectedExpError(self.get_all_before_this())
      else:
        self.next()
        return exp


  def try_f_part(self):
    """This function DO SELF.NEXT()"""
    if self.get() != "(":
      return get_codes(self.line.operation)[1]
    else:
      self.next()
      exp = self.try_exp()
      if exp is None:
        raise ExpectedExpError(self.get_all_before_this())
      else:
        self.next()
        if self.get() != ")":
          raise NoClosedBracketError(self.get_all_before_this())
        else:
          self.next()
          if 0 <= exp <= 45 and (exp / 8) <= (exp % 8): # 45 = 8*5 + 5
            return exp
          else:
            raise InvalidFieldSpecError(exp)


  def try_w_exp(self):
    """This function DO SELF.NEXT()"""
    word = Memory.positive_zero()
    value = self.try_exp()
    if value is None:
      return None

    if self.look() == "(":
      self.next()
      field = self.try_f_part()
    else:
      field = 5 # it's property of w-exp that empty f-part means not default value but 0:5
      self.next()

    Memory.apply_to_word(value, word, field)

    while True:
      if self.get() != ",":
        break

      self.next()

      value = self.try_exp()
      if value is None:
        raise ExpectedExpError(self.get_all_before_this())

      if self.look() == "(":
        self.next()
        field = self.try_f_part()
      else:
        field = get_codes(self.line.operation)[1]
        self.next()

      Memory.apply_to_word(value, word, field)

    return Memory.mix2dec(word)


  def try_literal(self):
    if self.get() != "=":
      return None
    
    self.next()
    res = self.try_w_exp()
    if res is None:
      raise ExpectedWExpError(self.line.argument)
    else:
      if self.get() != "=":
        raise NoEqualSignError(self.get_all_before_this())
      else:
        # line of expression must be less than 10 digits
        length = self.line.argument.find("=", 1) - 1
        if length >= 10:
          raise TooLongLiteralError(self.line.argument[1 : length + 1])

        self.next()

        if self.npass == 1:
          return 0

        return self.symbol_table.add_literal(res)

  def try_addr_part(self):
    """This function DO SELF.NEXT()"""
    res = self.try_any(
      (self.try_exp, self.try_future_symbol, self.try_literal)
    )
    if res is None:
      return 0
    else:
      self.next()
      return res


  def try_argument(self):
    if is_instruction(self.line.operation):
      addr_part = self.try_addr_part()
      # done self.next() !!!
      ind_part = self.try_ind_part()
      # done self.next() !!!
      f_part = self.try_f_part()
      # done self.next() !!!
      if self.get() is not None:
        raise UnexpectedStrInTheEndError(self.get_all_forward_from_this())
      return Memory.sign(addr_part) * (abs(addr_part) * 64**3 + ind_part * 64**2 + f_part * 64)
    elif self.line.operation in ("EQU", "ORIG", "CON", "END"):
      res = self.try_w_exp()
      # done self.next() !!!
      if res is not None:
        if self.get() is not None:
          raise UnexpectedStrInTheEndError(self.get_all_forward_from_this())
        return res
      else:
        raise ExpectedWExpError(self.line.argument)
    else: # self.line.instruction = "ALF"
      res = self.try_alf_word()
      if self.look() is not None:
        raise UnexpectedStrInTheEndError(self.get_all_after_this())
      return res
