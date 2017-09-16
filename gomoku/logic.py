from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np


def get_status(board):
  assert isinstance(board, np.ndarray) and board.shape == (15, 15)
