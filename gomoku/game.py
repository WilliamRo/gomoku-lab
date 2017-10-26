from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pickle

from .board import Board
from .logic import get_status


class Game(object):
  """A gomoku game."""
  def __init__(self):
    # Initiate board
    self.board = Board()
    # Initialize stacks
    self.records = []
    self.redos = []

  # region : Properties

  def __getitem__(self, item):
    assert isinstance(item, tuple) and len(item) == 2
    return self.board[item]

  @property
  def next_stone(self):
    return self.board.next_stone

  @property
  def legal_positions(self):
    return self.board.legal_positions

  @property
  def status(self):
    if len(self.records) == 0:
      return 0
    stat = get_status(self.board.matrix, self.records[-1])
    if stat != 0:
      return stat

    return 0 if len(self.records) < 225 else 2

  # endregion : Properties

  # region : Public Methods

  def restart(self):
    self.board.clear()
    self.records = []
    self.redos = []

  def place_stone(self, row, col):
    if self.board.place_stone(row, col):
      self.records.append((row, col))
      self.redos = []
      return True

    return False

  def undo(self):
    if not len(self.records) > 0:
      return False
    coord = self.records.pop()
    self.redos.append(coord)
    self.board.remove_stone(*coord)
    return True

  def redo(self):
    if not len(self.redos) > 0:
      return False
    coord = self.redos.pop()
    self.records.append(coord)
    self.board.place_stone(*coord)
    return True

  def home(self):
    flag = False
    while self.undo():
      flag = True
    return flag

  def end(self):
    flag = False
    while self.redo():
      flag = True
    return flag

  def save(self, filename):
    with open(filename, 'wb') as output:
      pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

  @staticmethod
  def load(filename):
    with open(filename, 'rb') as input_:
      return pickle.load(input_)

  # endregion : Public Methods

  # region : Private Methods

  def default_notify(self):
    pass

  # endregion : Private Methods

  '''For some reason, do not remove this line'''