from PyQt4.QtCore import *
from PyQt4.QtGui import *

from word_edit import word2toolTip

from code_view import AbstractCodeView

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'vm'))
from word import Word

class ListingView(AbstractCodeView):
  def __init__(self, parent = None):
    AbstractCodeView.__init__(self, parent)
    self.ModelClass = ListingModel

  def updateVM(self, vm_data):
    for i in range(len(self.code_model.lines)):
      line = self.code_model.lines[i]
      if line.addr != None and not line.modified and self.snap_mem[line.addr] != self.code_model.words[line.addr]:
        # check if this line was modified before update or now
        line.modified = True
        self.code_model.lineChanged(i)
    del self.snap_mem
    self.code_model.current_line = self.code_model.addr2num(vm_data.ca())
    self.caChanged()

  def caChanged(self):
    num = self.code_model.current_line
    if num is not None:
      self.setCurrentIndex(self.code_model.index(num, 0))

class ListingModel(QAbstractTableModel):
  def __init__(self, vm_data = None, asm_data = None, parent = None): # asm_data not used
    QAbstractTableModel.__init__(self, parent)
    if vm_data is not None:
      self.lines = vm_data.listing.lines[:]
      # new lines where word is Word (class), not list
      for line in self.lines:
        line.modified = False

      self.words = vm_data.vm.memory
      self.is_readable = vm_data.is_readable
      self.is_locked = lambda x: not (vm_data.is_readable(x) and vm_data.is_writeable(x))
      self.create_addr2num_data() # creates data for addr2num(...)
      self.current_line = self.addr2num(vm_data.ca())
      self.inited = True
    else:
      self.inited = False

  def addBreakpoint(self, index):
    addr = self.lines[index.row()].addr
    if addr is not None:
      if addr in self.breaks:
        self.breaks.remove(addr)
      else:
        self.breaks.add(addr)
      self.lineChanged(index.row())

  def rowCount(self, parent):
    if self.inited:
      return len(self.lines)
    else:
      return 0

  def columnCount(self, parent):
    return 3 # addr, word, source-lines

  def data(self, index, role = Qt.DisplayRole):
    if not index.isValid():
      return QVariant()

    if role == Qt.TextAlignmentRole:
      if index.column() in (0,1):
        # address, mix word
        return QVariant(Qt.AlignHCenter | Qt.AlignVCenter)
      else:
        # source line
        return QVariant(Qt.AlignLeft | Qt.AlignVCenter)

    elif role == Qt.BackgroundRole:
      changed_row = self.lines[index.row()].modified
      ca_row = index.row() == self.current_line
      locked_row = self.is_locked(self.lines[index.row()].addr)
      if changed_row and ca_row and locked_row:
        return QVariant(QColor(200, 150, 0))

      elif changed_row and ca_row:
        return QVariant(QColor(220, 220, 0))
      elif changed_row and locked_row:
        return QVariant(QColor(200, 25, 0))
      elif locked_row and ca_row:
        return QVariant(QColor(255, 175, 0))

      elif changed_row:
        return QVariant(QColor(Qt.gray))
      elif ca_row:
        return QVariant(QColor(255, 255, 0))
      elif locked_row:
        return QVariant(QColor(255, 50, 0))
      else:
        return QVariant()

    elif role == Qt.DisplayRole:
      listing_line = self.lines[index.row()]
      column = index.column()

      if column == 0:
        if listing_line.addr is not None:
          return QVariant(listing_line.addr2str())
        else:
          return QVariant(u"")

      elif column == 1:
        if listing_line.addr is not None:
          if self.is_readable(listing_line.addr):
            return QVariant(self.words[listing_line.addr].addr_str()) # print first two bytes as one address
          else:
            return QVariant(self.tr("LOCKED"))
        else:
          return QVariant(u"")

      else:
        return QVariant(listing_line.line)

    elif role == Qt.ToolTipRole:
        if self.lines[index.row()].addr is not None and index.column() == 1:
          if self.is_readable(self.lines[index.row()].addr):
            return QVariant(word2toolTip( self.words[self.lines[index.row()].addr] ))
          else:
            return QVariant(self.tr("This memory cell is locked for reading"))
        else:
          return QVariant(u"")

    else:
      return QVariant()

  def headerData(self, section, orientation, role = Qt.DisplayRole):
    if role == Qt.TextAlignmentRole:
      if orientation == Qt.Vertical:
        return QVariant(Qt.AlignRight | Qt.AlignVCenter)
      else:
        return QVariant(Qt.AlignHCenter | Qt.AlignVCenter)
    elif role == Qt.DisplayRole:
      if orientation == Qt.Horizontal:
        return QVariant(self.tr(("Addr", "Mix word", "Source line")[section]))
      else:
        return QVariant(str(section + 1))
    elif role == Qt.BackgroundRole and orientation == Qt.Vertical and self.lines[section].addr in self.breaks:
      # breakpoint
      return QVariant(QColor(Qt.red))
    else:
      return QVariant()

  def lineChanged(self, num):
    """dataChange for all line"""
    if num is not None:
      self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
          self.index(num, 0),
          self.index(num, 2))
      self.emit(SIGNAL("headerDataChanged(Qt::Orientation, int, int)"),
          Qt.Vertical, num, num)

  def hook(self, item, old, new):
    if item == "cur_addr": # cpu hook
      old_num = self.addr2num(old)
      if old_num is not None:
        self.lineChanged(old_num)
      self.current_line = num = self.addr2num(new)
      self.lineChanged(num)
    elif isinstance(item, int): # mem hook
      num = self.addr2num(item)
      if num is None:
        return
      self.lines[num].word = new
      self.lines[num].modified = True
      self.lineChanged(num)
    elif item in ("rw", "w"): # lock hook
      for addr in old.symmetric_difference(new):
        self.lineChanged(self.addr2num(addr))
    # else any cpu hook but cur_addr


  def create_addr2num_data(self):
    self.addr2num_data = dict([
        (self.lines[i].addr, i)
        for i in range(len(self.lines)) if self.lines[i].addr is not None
    ])

  def addr2num(self, addr):
    return self.addr2num_data.get(addr)
