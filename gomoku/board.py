from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np


class Board(object):
  """Chess board for Gomoku. Positions of black/white stones are stored
     in a 15x15 numpy array. Each entry in this array is an element of
     set {0(empty), 1(black stone), -1(white stone)}"""
  def __init__(self):
    # Initiate chess board
    self.matrix = np.zeros(shape=[15, 15], dtype=np.int8)

  # region : Properties

  @property
  def next_stone(self):
    assert (isinstance(self.matrix, np.ndarray)
            and self.matrix.shape == (15, 15))
    return -1 if self.matrix.sum() else 1

  @property
  def legal_positions(self):
    return [tuple(position) for position in np.argwhere(self.matrix == 0)]

  def __getitem__(self, item):
    assert isinstance(item, tuple) and len(item) == 2
    return self.matrix[item[0], item[1]]

  # endregion : Properties

  # endregion : Overwrite

  # region : Public Methods

  def clear(self):
    self.matrix = np.zeros(shape=[15, 15], dtype=np.int8)

  def place_stone(self, row, col):
    # Check input
    if not isinstance(row, int) or not 0 <= row < 15:
      raise ValueError('!! Input row must be an integer between 0 and 14')
    if not isinstance(col, int) or not 0 <= col < 15:
      raise ValueError('!! Input col must be an integer between 0 and 14')

    # Place stone on the corresponding position
    if self.matrix[row, col]:
      raise ValueError('!! A stone is already on that position')
    self.matrix[row, col] = self.next_stone

    return True

  def remove_stone(self, row, col):
    self.matrix[row, col] = 0

  # endregion : Public Methods

  '''For some reason ...'''

