try:
  import tkinter as tk
except:
  import Tkinter as tk

from PIL import Image as Image_
from PIL import ImageTk

import numpy as np

from gomoku.game import Game


stone_size = 21


class Images:
  @staticmethod
  def grid(i, j):
    assert 0 <= i < 15 and 0 <= j < 15

    arr = np.ones([stone_size, stone_size]) * 255

    mid = (stone_size - 1) // 2
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
    # Special position
    r = 2
    if (i, j) in [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]:
      arr[mid-r:mid+r+1, mid-r:mid+r+1] = 0

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
    X = np.vstack((scale.reshape(1, stone_size),) * stone_size)
    Y = np.hstack((scale.reshape(stone_size, 1),) * stone_size)
    D = np.round(np.sqrt(X**2 + Y**2))
    mask = D <= rad if color == 1 else D == rad
    arr[mask] = 0

    img = Image_.fromarray(arr)
    return ImageTk.PhotoImage(img)


class TkBoard(object):
  def __init__(self, game=None):
    self.game = Game() if game is None else game
    self.game.notify = self.notify

    self.form = tk.Tk()
    self.grids = {}
    # Images must be generated after an instance of Tk has been created
    self.stones = {1: Images.stone(1), -1:Images.stone(-1)}
    self.positions = {}

    # region: Design form

    # region: Layout

    self.form.bind('<Key>', self.on_key_press)
    self.form.title('Gomoku')
    self.form.resizable(width=False, height=False)

    self.status_bar = tk.Frame(self.form, bg='white')
    self.status_bar.pack(side=tk.TOP, fill=tk.X)
    self.chess_board = tk.Frame(self.form, bg='white')
    self.chess_board.pack(side=tk.TOP)
    self.control_center = tk.Frame(self.form, bg='white')
    self.control_center.pack(side=tk.TOP, fill=tk.X)

    # endregion: Layout

    # Status bar
    self.next_stone = tk.Label(self.status_bar)
    self.next_stone.pack(side=tk.LEFT, padx=4)
    self.status = tk.Label(self.status_bar, text='Status bar', bg='white')
    self.status.pack(side=tk.LEFT, padx=0)

    # Chess board
    for i in range(15):
      frame = tk.Frame(self.chess_board, bg='white')
      frame.pack(side=tk.TOP)
      for j in range(15):
        coord = (i, j)
        self.grids[coord] = Images.grid(i, j)
        self.positions[coord] = tk.Button(
          frame, cursor='hand2', relief='flat', bd=0)
        self.positions[coord].coord = coord
        self.positions[coord].bind('<Button>', self.on_board_press)
        self.positions[coord].pack(side=tk.LEFT)

    self.refresh()

    # Control center
    tk.Button(self.form, text='Button1').pack(side=tk.LEFT, padx=2, pady=2)

    # endregion: Design form

  # region: Public Methods

  def show(self):
    self.form.mainloop()

  # endregion: Public Methods

  # region: Private Methods

  def set_image(self, coord, color=None):
    color = self.game[coord] if color is None else color

    if color:
      # If color is not 0, place stone
      self.positions[coord].config(image=self.stones[color])
    else:
      # Else show grid
      self.positions[coord].config(image=self.grids[coord])

  def refresh(self):
    assert isinstance(self.game, Game)
    # Refresh status bar
    self.update_status()
    # Refresh chess board
    for i in range(15):
      for j in range(15):
        self.set_image((i, j))

  def update_status(self):
    color = self.game.next_stone
    self.next_stone.config(image=self.stones[color])
    self.status.config(
      text="{}'s turn".format("Black" if color == 1 else "White"))

  # endregion: Private Methods

  # region: Events

  def on_key_press(self, event):
    assert isinstance(event, tk.Event)
    if event.keysym == 'Escape':
      self.form.quit()

  def on_board_press(self, event):
    button = event.widget
    coord = button.coord
    if not self.game[coord]:
      self.game.place_stone(*coord)

  def notify(self):
    self.update_status()
    if self.game.last_action == self.game.place_stone:
      coord = self.game.records[-1]
      self.set_image(coord)

  # endregion: Events

  '''For some reason, do not remove this line'''


if __name__ == "__main__":
  tkb = TkBoard()
  tkb.show()
