from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import copy


BLACK = 1
WHITE = -1

class Situation(object):
  """Situation of a gomoku game"""
  def __init__(self):
    self.status = 0
    self.crystals = {BLACK: [], WHITE: []}
    self.eye_of = {BLACK: {}, WHITE: {}}

  # region : Properties

  # endregion : Properties

  # region : Public Methods

  def new_situation(self, board, coord):
    assert isinstance(board, np.ndarray) and board.shape == (15, 15)
    assert isinstance(coord, tuple) and len(coord) == 2
    stone_color = board[coord]
    assert stone_color in (BLACK, WHITE)
    situation = copy.deepcopy(self)

    # Update own crystals
    crystals = situation.eye_of[stone_color].pop(coord, [])
    for crystal in crystals:
      assert isinstance(crystal, Crystal)
      crystal.remove(coord)
      # If crystal bursts, a mate is formed
      if crystal.level == 5:
        situation.status = stone_color
        return situation

    # Destroy opponent's crystals
    crystals = situation.eye_of[-stone_color].get(coord, []).copy()
    for crystal in crystals:
      assert isinstance(crystal, Crystal)
      situation.crystals[-stone_color].remove(crystal)
      # Unlink eye_of to this destroyed crystal
      for eye in crystal:
        situation.eye_of[-stone_color][eye].remove(crystal)
        if len(situation.eye_of[-stone_color][eye]) == 0:
          situation.eye_of[-stone_color].pop(eye)

    # Search for new crystals
    inbound = lambda c: (all(c >= np.array([0, 0])) and
                          all(c < np.array([15, 15])))
    for direction in np.array([[0, 1], [1, 0], [1, 1], [1, -1]]):
      # Initialize pattern
      pattern = Pattern(coord)
      # Go for each side
      for side in (-1, 1):
        c = np.array(coord)
        step = direction * side
        flag = True
        while flag:
          # Move forward
          c += step
          color = board[tuple(c)] if inbound(c) else None
          token = (Pattern.BLOCK if color == -stone_color else
                   (Pattern.OWN if color == stone_color else Pattern.EMPTY ))
          # Update pattern
          flag = pattern.add(side, token, tuple(c))

      # Try to register new crystals in this direction
      for crystal in pattern.new_crystals:
        assert isinstance(crystal, Crystal)
        situation.crystals[stone_color].append(crystal)
        for eye in crystal:
          if eye not in situation.eye_of[stone_color].keys():
            situation.eye_of[stone_color][eye] = []
          situation.eye_of[stone_color][eye].append(crystal)

    # Return the updated situation
    return situation

  def recommended_moves(self, color):
    return None

  def coords_with_level(self, color):
    coords = {}
    for coord, crystals in self.eye_of[color].items():
      assert isinstance(crystals, list) and len(crystals) > 0
      coords[coord] = sum([crystal.level for crystal in crystals])
    return coords

  # endregion : Public Methods

  # region : Private Methods

  def _mate_moves(self, color):
    return [crystal[0] for crystal in self.crystals[color]
             if crystal.level == 4]

  def _four_mate_moves(self, color):
    moves = []
    for coord, crystals in self.eye_of[color].items():
      assert isinstance(crystals, list) and len(crystals) > 0
      if len([crystal for crystal in crystals if crystal.level == 3]) > 1:
        moves.append(coord)

    return moves

  def _slay_moves(self, color):
    moves = []
    return moves

  # endregion : Private Methods

  """End of class Situation"""


class Crystal(list):
  """Crystal"""
  def __init__(self, center, closed_eyes):
    """Four closed eyes must be provided to activate a crystal"""
    assert isinstance(center, tuple) and len(center) == 2
    assert isinstance(closed_eyes, list) and len(closed_eyes) == 4
    super(Crystal, self).__init__()
    self.center = center
    self.extend(closed_eyes)

  @property
  def level(self):
    return 5 - len(self)


class Pattern(list):
  """Raw stone pattern in one single direction"""
  EMPTY = 0
  OWN = 1
  BLOCK = -1

  def __init__(self, coord):
    assert isinstance(coord, tuple) and len(coord) == 2
    super(Pattern, self).__init__()
    self.append(1)
    self.coords = [coord]
    self.counter = {1: 0, -1: 0}

  # region : Properties

  @property
  def new_crystals(self):
    if len(self) < 5:
      return []

    crystals = []
    for offset in range(len(self) - 4):
      sub_pattern = self[offset:offset+5]
      if sum(sub_pattern) == 1:
        sub_coords = self.coords[offset:offset+5]
        center = sub_coords[2]
        # Remove opened eye
        sub_coords.pop(np.argmax(sub_pattern))
        crystals.append(Crystal(center, sub_coords))

    return crystals

  # endregion : Properties

  # region : Public Methods

  def add(self, side, token, coord):
    assert side in (-1, 1)
    assert token in [self.EMPTY, self.OWN, self.BLOCK]
    assert isinstance(coord, tuple) and len(coord) == 2

    if token == self.BLOCK:
      return False

    if side == -1:
      self.insert(0, token)
      self.coords.insert(0, coord)
    else:
      self.append(token)
      self.coords.append(coord)

    self.counter[side] += 1
    return self.counter[side] < 4

  # endregion : Public Methods


  '''For some reason, do not delete this line'''








