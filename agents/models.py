from __future__ import absolute_import
from __future__ import division
from __future__ import absolute_import

from tframe import console

from tframe.models import TDPlayer

from tframe.layers import Activation
from tframe.layers import BatchNorm
from tframe.layers import Conv2D
from tframe.layers import Dropout
from tframe.layers import Flatten
from tframe.layers import Linear
from tframe.layers import Input

from gomoku.game import Game


# region : Vanilla

def mlp00(mark):
  # Define model
  model = TDPlayer(mark=mark)

  model.add(Input(sample_shape=[15, 15]))
  model.add(Flatten())

  model.add(Linear(225))
  model.add(Activation.ReLU())

  model.add(Linear(225))
  model.add(Activation.ReLU())

  model.add(Linear(1))
  model.add(Activation('sigmoid'))

  # Build model
  model.build()

  return model

# endregion : Vanilla


if __name__ == '__main__':
  model = mlp00('test')
