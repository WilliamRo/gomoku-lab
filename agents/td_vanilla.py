from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from tframe import console
from tframe import FLAGS

from tframe.models.rl.random_players import FMDRandomPlayer

from agents import models

from gomoku.game import Game


def main(_):
  FLAGS.overwrite = False
  FLAGS.train = True

  console.suppress_logging()
  console.start('TD Gomoku - vanilla')

  with tf.Graph().as_default():
    model = models.mlp00('mlp00_00')

  with tf.Graph().as_default():
    opponent = models.mlp00('mlp00_00')

  game = Game()
  if FLAGS.train:
    model.train(game, episodes=100000, print_cycle=5, snapshot_cycle=400,
                match_cycle=500, rounds=100, rate_thresh=1.0, shadow=opponent,
                snapshot_function=game.snapshot)
  else:
    model.compete(game, rounds=100, opponent=opponent)

  console.end()


if __name__ == '__main__':
  tf.app.run()
