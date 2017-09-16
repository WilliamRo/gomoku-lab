try:
  import tkinter as tk
except:
  import Tkinter as tk

from PIL import Image as Image_
from PIL import ImageTk

import numpy as np


stone_size = 21


class Images:
  @staticmethod
  def grid(i, j):
    assert 0 <= i < 15 and 0 <= j < 15

    arr = np.ones([stone_size, stone_size]) * 255

    mid = (stone_size - 1) / 2
    # Vertical
    if i == 0:
      arr[mid:, mid] = 0
    elif i == 14:
      arr[:mid+1, mid] = 0
    else:
      arr[:, mid] = 0
    # Horizontal
    if j == 0:
      arr[mid, mid:] = 0
    elif j == 14:
      arr[mid, :mid+1] = 0
    else:
      arr[mid, :] = 0

    img = Image_.fromarray(arr)
    return ImageTk.PhotoImage(img)

  @staticmethod
  def stone(color):
    '''
    Generate a binary image for stone
    :param color: integer in {-1, 1}, -1 for white, 1 for black
    :return: An instance of ImageTk.PhotoImage
    '''
    arr = np.ones([stone_size, stone_size]) * 255

    rad = (stone_size - 1) / 2
    scale = np.arange(stone_size) - rad
    X = scale.reshape(1, stone_size)

    img = Image_.fromarray(arr)
    return ImageTk.PhotoImage(img)


class TkBoard(object):
  _button_size = 2

  def __init__(self):
    self._form = tk.Tk()

    for i in range(15):
      for j in range(15):
        tk.Button(self._form, width=self._button_size,
                  height=self._button_size).grid(row=i, column=j)

  def run(self):
    self._form.mainloop()


if __name__ == "__main__":
  tkb = TkBoard()
  tkb.run()
