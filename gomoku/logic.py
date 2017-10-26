from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np


def get_status(board, coord):
  assert isinstance(board, np.ndarray) and board.shape == (15, 15)
  assert isinstance(coord, tuple) and len(coord) == 2
  color = board[coord]

  inbound = lambda c: (all(c >= np.array([0, 0])) and
                        all(c < np.array([15, 15])))

  for direction in [(0, 1), (1, 0), (1, 1), (1, -1)]:
    p = np.array(direction)
    counter = 1
    for s in [-1, 1]:
      c = np.array(coord)
      d = p*s
      while True:
        c = c + d
        if not inbound(c) or board[tuple(c)] != color:
          break
        counter += 1

    if counter >= 5:
      return color

  return 0


