from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import Iterable

import numpy as np
import six

from .board import Board


class Game(object):
  """A gomoku game."""
  def __init__(self):
    # Initiate board
    self.board = Board()

  # region : Properties

  # endregion : Properties

  # region : Public Methods

  def restart(self):
    self.board.clear()

  def place_stone(self, row, col):
    self.board.place_stone(row, col)

  # endregion : Public Methods

  # region : Private Methods


  # endregion : Private Methods

  '''For some reason, do not remove this line'''