from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import Iterable

import numpy as np
import six

from .board import Board
from .logic import get_status


class Game(object):
  """A gomoku game."""
  def __init__(self):
    # Initiate board
    self.board = Board()
    # Game records
    self.records = []
    self.redos = []
    # Notify
    self.notify = self.default_notify
    # Last action
    self.last_action = None

  # region : Properties

  def __getitem__(self, item):
    assert isinstance(item, tuple) and len(item) == 2
    return self.board[item]

  @property
  def next_stone(self):
    return self.board.next_stone

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

  def place_stone(self, row, col):
    if self.board.place_stone(row, col):
      self.records.append((row, col))
      self.redos = []
      self.last_action = self.place_stone
      self.notify()

  # endregion : Public Methods

  # region : Private Methods

  def default_notify(self):
    pass

  # endregion : Private Methods

  '''For some reason, do not remove this line'''