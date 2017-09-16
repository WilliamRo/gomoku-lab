from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy as np

from .board import Board


def clc():
  print('\n' * 80)
  # os.system('cls' if os.name == 'nt' else 'clear')


def gen_board_chars():
  chars = []
  for i in range(15):
    if i == 0:
      row = list('\u252c' * 15)
      row[0] = '\u250c'
      row[-1] = '\u2510'
    elif i == 14:
      row = list('\u2534' * 15)
      row[0] = '\u2514'
      row[-1] = '\u2518'
    else:
      row = list('\u253c' * 15)
      row[0] = '\u251c'
      row[-1] = '\u2524'

    # Append row to chars
    chars.append(row)

  # Return
  return chars


def print_board(board):
  assert isinstance(board, Board)
  chars = gen_board_chars()
  for i in range(15):
    for j in range(15):
      if board._board[i, j] == 1:
        chars[i][j] = '\u25cf'
        # chars[i][j] = '\u2b24'
      elif board._board[i, j] == -1:
        chars[i][j] = '\u25cb'
        # chars[i][j] = '\u25ef'  # large circle
    # Print row
    print(''.join(chars[i]))

