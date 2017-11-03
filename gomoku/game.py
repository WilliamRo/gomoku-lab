from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pickle
import numpy as np

from .board import Board
from .brain import Situation

from tframe.models.rl.interfaces import FMDPAgent
from tframe.models.rl.interfaces import Player


class Game(FMDPAgent):
  """A gomoku game."""

  # region : Constants

  BLACK_WIN = 1
  WHITE_WIN = -1
  NONTERMINAL = 0
  TIE = 2
  BLACK = 1
  WHITE = -1
  HUMAN_INTERFERENCE = True
  SAMPLE = False

  # endregion : Constants

  def __init__(self):
    # Initiate board
    self.board = Board()
    # Initialize stacks
    self.records = []
    self.redos = []

    self.situation_records = [Situation()]
    self.situation_redos = []

    self.candidate_moves = None


  # region : Properties

  def __getitem__(self, item):
    assert isinstance(item, tuple) and len(item) == 2
    return self.board[item]

  @property
  def moves(self):
    return len(self.records)

  @property
  def next_stone(self):
    return self.board.next_stone

  @property
  def legal_moves(self):
    return self.board.legal_positions

  @property
  def status(self):
    """Game status. 1: Black wins; -1: White wins; 2: Tie; 0: Non-terminal"""
    stat = self.situation_records[-1].status
    if stat != 0:
      return stat

    return self.NONTERMINAL if len(self.records) < 225 else self.TIE

  @property
  def terminated(self):
    return self.status != self.NONTERMINAL

  @property
  def state(self):
    return self.board.matrix

  @property
  def recommended_moves(self):
    return self.situation.recommended_moves(self.next_stone)

  @property
  def situation(self):
    return self.situation_records[-1]

  @property
  def candidate_states(self):
    if self.terminated:
      return None

    moves = self.legal_moves
    if self.HUMAN_INTERFERENCE:
      recommended_moves = self.recommended_moves
      if recommended_moves is not None:
        moves = recommended_moves

    moves = list(set(moves))
    assert len(moves) > 0
    candidates = np.stack([self.state] * len(moves))
    stone = self.next_stone
    for i, move in enumerate(moves):
      candidates[i, move[0], move[1]] = stone

    self.candidate_moves = moves
    return candidates

  # endregion : Properties

  # region : Public Methods

  def coords_with_color(self, color):
    return self.situation.coords_with_level(color)

  def compete(self, players, rounds, **kwargs):
    if (not isinstance(players[0], Player) or
        not isinstance(players[1], Player)):
      raise TypeError('players should be a list of Player')

    results = [[0, 0, 0, 1], [0, 0, 0, 1]]
    for offensive in range(2):
      defensive = 1 - offensive
      for _ in range(rounds):
        self.restart()
        self.default_first_move()
        next_player = defensive
        while not self.terminated:
          players[next_player].next_step(self)
          results[offensive][3] += 1
          next_player = 1 - next_player
        if self.status == self.BLACK_WIN:
          results[offensive][offensive] += 1
        elif self.status == self.WHITE_WIN:
          results[offensive][defensive] += 1
        elif self.status == self.TIE:
          results[offensive][2] += 1
        else:
          raise ValueError('The game is expected to be terminated')

    # Generate report
    ties = [' ({} ties)'.format(results[0][2]) if results[0][2] else '',
            ' ({} ties)'.format(results[1][2]) if results[1][2] else '']
    avg_steps = ['{:.1f} steps on average'.format(results[0][3] / rounds),
                 '{:.1f} steps on average'.format(results[1][3] / rounds)]
    reports = ['Player 1 holds black: {}-{}{}, {}'.format(
               results[0][0], results[0][1], ties[0], avg_steps[0]),
               'Player 1 holds white: {}-{}{}, {}'.format(
               results[1][0], results[1][1], ties[1], avg_steps[1])]
    rate = (results[0][0] + results[1][0]) / (2 * rounds)

    return rate, reports

  def action_index(self, values):
    if not self.SAMPLE:
      return (np.argmax(values) if self.next_stone == self.BLACK
               else np.argmin(values))

    if self.next_stone == self.WHITE:
      values = 1 - values
    exps = np.exp(values)
    probability = exps / np.sum(exps)
    index = np.random.choice(len(values), 1, p=probability.flatten())
    return index[0]

  def act(self, index):
    assert (self.candidate_moves is not None and
             len(self.candidate_moves) > index)
    position = self.candidate_moves[index]
    self.place_stone(int(position[0]), int(position[1]))
    reward = self.status
    return reward if reward == 1 else 0

  def snapshot(self, filename):
    self.save(filename)

  def restart(self):
    self.board.clear()
    self.records = []
    self.redos = []
    self.situation_records = [Situation()]
    self.situation_redos = []

  def default_first_move(self):
    assert self.place_stone(7, 7)

  def place_stone(self, row, col):
    if self.board.place_stone(row, col):
      self.records.append((row, col))
      self.redos = []

      situation = self.situation.new_situation(self.board.matrix, (row, col))
      self.situation_records.append(situation)
      self.situation_redos = []

      return True

    return False

  def undo(self):
    if not len(self.records) > 0:
      return False
    coord = self.records.pop()
    self.redos.append(coord)
    self.board.remove_stone(*coord)

    self.situation_redos.append(self.situation_records.pop())

    return True

  def redo(self):
    if not len(self.redos) > 0:
      return False
    coord = self.redos.pop()
    self.records.append(coord)
    self.board.place_stone(*coord)

    self.situation_records.append(self.situation_redos.pop())

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
    if filename[-4:] != '.gmk':
      filename = '{}.gmk'.format(filename)
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