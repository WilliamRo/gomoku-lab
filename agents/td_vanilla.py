from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from tframe import console
from tframe import FLAGS

from tframe.models.rl.random_players import FMDRandomPlayer

from agents import models

from gomoku.game import Game
from tkboard import TkBoard


def main(_):
  FLAGS.overwrite = False
  FLAGS.train = True
  play = True

  console.suppress_logging()
  console.start('TD Gomoku - vanilla')

  with tf.Graph().as_default():
    model = models.mlp00('mlp00_00')

  with tf.Graph().as_default():
    opponent = models.mlp00('mlp00_00')

  game = Game()
  if FLAGS.train:
    model.train(game, episodes=500000, print_cycle=100, snapshot_cycle=1000,
                match_cycle=2000, rounds=5, rate_thresh=1.0, shadow=opponent,
                save_cycle=200, snapshot_function=game.snapshot)
  else:
    if play:
      TkBoard(player=model).show()
    else:
      model.compete(game, rounds=100, opponent=opponent)

  console.end()


if __name__ == '__main__':
  tf.app.run()
