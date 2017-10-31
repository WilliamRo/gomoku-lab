from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import copy


BLACK = 1
WHITE = -1

inbound = lambda c: (all(c >= np.array([0, 0])) and
                     all(c < np.array([15, 15])))

def get_situation(board, coord, situation):
  assert isinstance(board, np.ndarray) and board.shape == (15, 15)
  assert isinstance(coord, tuple) and len(coord) == 2
  assert isinstance(situation, Situation) and not situation.status
  stone_color = board[coord]
  situation = copy.deepcopy(situation)

  # Update precede situation
  situation.block(-stone_color, coord)

  # Analyze current situations
  for direction in [(0, 1), (1, 0), (1, 1), (1, -1)]:
    p = np.array(direction)
    # 0 for empty; 1 for current color; -1 for block
    pattern = [1]
    coords = [coord]
    # 'left' and 'right'
    for s in [-1, 1]:
      c = np.array(coord)
      d = p * s
      precede_is_empty = False
      flag = True
      while flag:
        # Move
        c = c + d
        color = board[tuple(c)] if inbound(c) else None
        # if block
        if not inbound(c) or color == -stone_color:
          token = -1
          flag = False
        # if empty
        elif color == 0:
          # At most 2 empty location will be add to each side of pattern
          token = 0
          flag = not precede_is_empty
          precede_is_empty = True
        # if same color
        else:
          token = 1
          precede_is_empty = False
        # Update pattern and coords
        if s == -1:
          pattern.insert(0, token)
          coords.insert(0, tuple(c))
        else:
          pattern.append(token)
          coords.append(tuple(c))

    # Check pattern
    assert len(pattern) >= 3
    if _terminated(pattern):
      situation.status = stone_color
      break

    criticals = _critical(pattern)
    if len(criticals) > 0:
      situation.add_critical(stone_color, coords, criticals, coord)
      continue

    potentials = _potential(pattern)
    if len(potentials) > 0:
      situation.add_potential(stone_color, pattern, coords, potentials)
      continue

  # Finish searching 4 directions
  return situation


class Situation(object):
  def __init__(self):
    self.status = 0
    # A list of coordinates
    self.criticals = {BLACK: [], WHITE: []}
    # A list of list
    self.potentials = {BLACK: [], WHITE: []}
    # Pattern backup for potentials
    self.patterns = {BLACK: {}, WHITE: {}}
    self.coords = {BLACK: {}, WHITE: {}}

  def block(self, color, coord):
    # Scan criticals
    if coord in self.criticals[color]:
      self.criticals[color].remove(coord)

    # Scan potentials
    remove_list = []
    for potential in self.potentials[color]:
      assert isinstance(potential, list) and len(potential) > 1
      if coord == potential[0]:
        remove_list.append(potential)
      elif coord in potential:
        if len(potential) == 2:
          remove_list.append(potential)
        else:
          potential.remove(coord)

    self._remove_potentials(color, remove_list)

  def reasonable_moves(self, color):
    # Win directly
    if len(self.criticals[color]) > 0:
      return self.criticals[color]
    # Prevent lose directly
    if len(self.criticals[-color]) > 0:
      return self.criticals[-color]
    # Try to checkmate
    moves = []
    for potential in self.potentials[color]:
      assert isinstance(potential, list)
      if len(potential) > 2:
        moves.append(potential[0])
    if len(moves) > 0:
      return moves
    # Avoid being checkmate
    for potential in self.potentials[-color]:
      assert isinstance(potential, list)
      if len(potential) > 2:
        coord = potential[0]
        pattern = self.patterns[-color][coord]
        coords = self.coords[-color][coord]
        for i in [k for k in range(len(pattern)) if not pattern[k]]:
          pattern[i] = -1
          gg = False
          for j in [k for k in range(len(pattern)) if not pattern[k]]:
            pattern[j] = 1
            if len(_critical(pattern)) > 1:
              gg = True
            pattern[j] = 0
          if not gg:
            moves.append(coords[i])
          pattern[i] = 0
    if len(moves) > 0:
      # Find potential moves
      append_list = []
      for potential in self.potentials[color]:
        assert isinstance(potential, list) and len(potential) == 2
        if potential[1] not in moves:
          append_list.append(potential[0])
      moves += append_list
      return moves

    return None

  def add_critical(self, color, coords, criticals, coord):
    assert isinstance(criticals, list) and len(criticals) > 0
    for index in criticals:
      self.criticals[color].append(coords[index])

    # Remove corresponding potentials
    # remove_list = []
    # for potential in self.potentials[color]:
    #   assert isinstance(potential, list)
    #   if coord in potential:
    #     pass
    # self._remove_potentials(color, remove_list)

  def add_potential(self, color, pattern, coords, potentials):
    assert isinstance(potentials, list) and len(potentials) > 0
    for t in potentials:
      assert isinstance(t, list) and len(t) > 1
      self.potentials[color].append([coords[i] for i in t])
      self.patterns[color][coords[t[0]]] = pattern
      self.coords[color][coords[t[0]]] = coords

  def _remove_potentials(self, color, remove_list):
    for potential in remove_list:
      assert isinstance(potential, list)
      self.potentials[color].remove(potential)
      self.patterns[color].pop(potential[0])
      self.coords[color].pop(potential[0])


def _terminated(pattern):
  assert isinstance(pattern, list)
  counter = 0
  for i in range(len(pattern)):
    counter = counter + 1 if pattern[i] == 1 else 0
    if counter >= 5:
      return True
  return False


def _critical(pattern):
  assert isinstance(pattern, list)
  criticals = []
  for i in range(len(pattern)):
    if not pattern[i]:
      pattern[i] = 1
      if _terminated(pattern):
        criticals.append(i)
      pattern[i] = 0
  return criticals


def _potential(pattern):
  assert isinstance(pattern, list)
  potentials = []
  for i in range(len(pattern)):
    if not pattern[i]:
      pattern[i] = 1
      criticals = _critical(pattern)
      if len(criticals) > 0:
        potentials.append([i] + criticals)
      pattern[i] = 0
  return potentials



















