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
    # Initialize pattern
    pattern = Pattern(coord)
    # For each side
    for s in [-1, 1]:
      c = np.array(coord)
      d = p * s
      flag = True
      while flag:
        # Move
        c = c + d
        color = board[tuple(c)] if inbound(c) else None
        # if block
        if not inbound(c) or color == -stone_color:
          token = Pattern.BLOCK
        # empty or own
        else:
          token = Pattern.EMPTY if color == 0 else Pattern.OWN
        # Update pattern
        flag = pattern.add(s, token, tuple(c))

    # Check pattern
    assert len(pattern) >= 3
    if pattern.terminated:
      situation.status = stone_color
      return situation

    criticals = pattern.criticals
    if len(criticals) > 0:
      situation.add_critical(stone_color, criticals)
      continue

    potentials = pattern.potentials
    if len(potentials) > 0:
      situation.add_potential(stone_color, potentials)
      continue

  # Finish searching 4 directions
  return situation


# region : Basic classed

class Pattern(list):
  EMPTY = 0
  OWN = 1
  BLOCK = -1
  def __init__(self, coord):
    super(Pattern, self).__init__()
    self.append(self.OWN)
    self.coords = [coord]

  # region : Properties

  @property
  def terminated(self):
    counter = 0
    for i in range(len(self)):
      counter = counter + 1 if self[i] == self.OWN else 0
      if counter >= 5:
        return True
    return False

  @property
  def empty_indices(self):
    return [i for i in range(len(self)) if self[i] == self.EMPTY]

  @property
  def criticals(self):
    indices = self._try(self.OWN, cond=lambda: self.terminated)
    return [self.coords[i] for i in indices]

  @property
  def potentials(self):
    def try_criticals(pattern, collection, i):
      assert isinstance(pattern, Pattern)
      assert isinstance(collection, list)

      criticals = pattern.criticals
      if len(criticals) > 0:
        collection.append(Potential(pattern.coords[i], criticals, pattern))

    return self._try(self.OWN, fn=try_criticals)

  @property
  def parry_moves(self):
    def block_test(pattern, collection, k):
      assert isinstance(pattern, Pattern)
      assert isinstance(collection, list)
      # Here self[k] has been blocked
      fatals = [p for p in pattern.potentials if p.fatal]
      if len(fatals) == 0:
        collection.append(pattern.coords[k])

    return self._try(self.BLOCK, fn=block_test)

  # endregion : Properties

  def add(self, side, token, coord):
    assert side in [-1, 1]
    assert token in [self.EMPTY, self.OWN, self.BLOCK]
    assert isinstance(coord, tuple) and len(coord) == 2

    if side == -1:
      self.insert(0, token)
      self.coords.insert(0, coord)
      alfa = sum(self[:2])
    else:
      self.append(token)
      self.coords.append(coord)
      alfa = sum(self[-2:])

    # Stop at [0, 0] or [-1] for each side
    return alfa > 0

  def _try(self, token, cond=None, fn=None):
    if fn is None:
      fn = lambda _, c, k: c.append(k)
    assert (cond is None or callable(cond)) and callable(fn)

    collection = []
    for i in self.empty_indices:
      self[i] = token
      if cond() if cond is not None else True:
        fn(self, collection, i)
      self[i] = self.EMPTY

    return collection


class Potential(object):
  def __init__(self, coord, criticals, pattern):
    assert isinstance(coord, tuple) and len(coord) == 2
    assert isinstance(criticals, list) and len(criticals) > 0
    assert isinstance(pattern, Pattern)

    self.coord = coord
    self.criticals = criticals
    self.pattern = pattern

  @property
  def fatal(self):
    return len(self.criticals) > 1

  @property
  def is_potential(self):
    return len(self.criticals) > 0

  @property
  def parry_moves(self):
    assert self.fatal
    return self.pattern.parry_moves

# endregion : Basic classed


class Situation(object):
  def __init__(self):
    self.status = 0
    # A list of coordinates
    self.criticals = {BLACK: [], WHITE: []}
    # A list of list
    self.potentials = {BLACK: [], WHITE: []}

  def block(self, color, coord):
    # Scan criticals
    if coord in self.criticals[color]:
      self.criticals[color].remove(coord)

    # Scan potentials
    remove_list = []
    for potential in self.potentials[color]:
      assert isinstance(potential, Potential) and potential.is_potential
      if coord == potential.coord:
        remove_list.append(potential)
      elif coord in potential.criticals:
        potential.criticals.remove(coord)
        if not potential.is_potential:
          remove_list.append(potential)
    # Remove potentials
    for potential in remove_list:
      self.potentials[color].remove(potential)

  # region : Recommend

  def recommended_moves(self, color):
    # Win directly
    if len(self.criticals[color]) > 0:
      return self.criticals[color]
    # Prevent lose directly
    if len(self.criticals[-color]) > 0:
      return self.criticals[-color]
    # Try to check and win
    moves = self._find_check_win(color)
    if len(moves) > 0:
      return moves
    # Avoid being checkmate
    moves = self._parry_check_win(color)
    if len(moves) > 0:
      return moves

    # If no recommended moves are found, return None
    return None

  def _find_siblings(self, color):
    siblings = []

    potentials = copy.copy(self.potentials[color])
    while len(potentials) > 0:
      # Pick the 1st potential
      sibling = [potentials[0]]
      # Find its sibling
      for potential in potentials[1:]:
        if potential.coord == sibling[0].coord:
          sibling.append(potential)
      # Remove sibling from potentials
      for potential in sibling:
        potentials.remove(potential)
      # If more than 1 potentials share the same coord, record them
      if len(sibling) > 1:
        siblings.append(sibling)

    return siblings

  def _find_check_win(self, color, with_potentials=False):
    """Moves which produces at least 2 criticals"""
    moves = []
    fatals = []

    # Find potentials with 2 criticals in one direction
    for potential in self.potentials[color]:
      assert isinstance(potential, Potential)
      if potential.fatal:
        moves.append(potential.coord)
        fatals.append(potential)

    # Find potentials with more than 2 criticals in different direction
    siblings = self._find_siblings(color)
    if len(siblings) > 0:
      for sibling in siblings:
        assert isinstance(sibling[0], Potential)
        moves.append(sibling[0].coord)

    # Return results
    return (moves, fatals, siblings) if with_potentials else moves

  def _find_check_check_win(self, color):
    moves = []
    return moves

  def _parry_check_win(self, color):
    # Find opponent's check win
    check_wins, fatals, siblings = self._find_check_win(-color, True)
    if len(check_wins) == 0:
      return []

    # Find strategies to parry check win
    moves = []
    # Parry fatal moves
    for potential in fatals:
      assert isinstance(potential, Potential)
      moves.extend(potential.parry_moves)
    # Parry sibling moves
    for sibling in siblings:
      assert isinstance(sibling, list) and len(sibling) > 1
      moves.append(sibling[0].coord)
      if len(sibling) == 2:
        moves.extend([sibling[0].criticals[0], sibling[1].criticals[0]])

    assert len(moves) > 0
    # Find potential moves
    append_list = []
    for potential in self.potentials[color]:
      assert isinstance(potential, Potential) and not potential.fatal
      if potential.criticals[0] not in check_wins:
        append_list.append(potential.coord)
    moves.extend(append_list)

    return moves

  def _find_potential_check_win(self, color):
    pass

  # endregion : Recommend

  # region : Add and remove

  def add_critical(self, color, criticals):
    assert isinstance(criticals, list) and len(criticals) > 0
    self.criticals[color].extend(criticals)

  def add_potential(self, color, potentials):
    assert isinstance(potentials, list) and len(potentials) > 0
    self.potentials[color].extend(potentials)

  # endregion : Add and remove

  '''For some reason, do not remove this line'''

