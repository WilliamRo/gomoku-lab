try:
  import tkinter as tk
  from tkinter import filedialog
except:
  import Tkinter as tk
  import tkFileDialog as filedialog

from PIL import Image as Image_
from PIL import ImageTk

import numpy as np
import re
import os

from gomoku.game import Game


stone_size = 21
mid = (stone_size - 1) // 2


class Images:
  @staticmethod
  def grid(i, j):
    assert 0 <= i < 15 and 0 <= j < 15

    arr = np.ones([stone_size, stone_size]) * 255

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
    :param color: integer in {-1, 1}, -1 for white, 1 for black, 0 for draw
                                       -2/2 for highlighted white/black
    :return: An instance of ImageTk.PhotoImage
    '''
    arr = np.ones([stone_size, stone_size]) * 255

    # Calculate distance to origin for each pixel
    rad = (stone_size - 1) / 2
    scale = np.arange(stone_size) - rad
    X = np.vstack((scale.reshape(1, stone_size),) * stone_size)
    Y = np.hstack((scale.reshape(stone_size, 1),) * stone_size)
    D = np.round(np.sqrt(X ** 2 + Y ** 2))

    # Generate images
    rad = rad - 1
    if color in [-1, 1, -2, 2]:
      mask = D <= rad if color > 0 else D == rad
      arr[mask] = 0
      if color in [-2, 2]:
        brush = 255 if color == 2 else 0
        half = int(np.round(rad / 2))
        r = half
        arr[mid-1:mid+2, mid-r+1:mid+r] = brush
        arr[mid-r+1:mid+r, mid-1:mid+2] = brush

        rs = 0  # keep it
        arr[mid, mid-r+1-rs:mid+r+rs] = brush
        arr[mid-r+1-rs:mid+r+rs, mid] = brush
    else:
      mask = D <= rad
      arr[mask] = 0
      mask = D <= np.round(rad / 2)
      arr[mask] = 255

    # Convert array to PhotoImage
    img = Image_.fromarray(arr)
    return ImageTk.PhotoImage(img)


class TkBoard(object):
  def __init__(self, game=None):
    self.game = None
    game = Game() if game is None else game
    self.bind(game)
    self.filename = None

    self.form = tk.Tk()
    self.grids = {}
    # Images must be generated after an instance of Tk has been created
    self.stones = {1: Images.stone(1), 0: Images.stone(0), -1: Images.stone(-1),
                   2: Images.stone(2), -2: Images.stone(-2)}
    self.positions = {}

    # region: Design form

    # region: Layout

    self.form.title('Gomoku')
    self.form.config(bg='white')
    self.form.bind('<Key>', self.on_key_press)
    self.form.bind('<Control-s>', self.save_game)
    self.form.bind('<Control-l>', self.load_game)
    self.form.resizable(width=False, height=False)

    self.status_bar = tk.Frame(self.form, bg='white')
    self.status_bar.pack(side=tk.TOP, fill=tk.X, padx=5)
    self.chess_board = tk.Frame(self.form, bg='white')
    self.chess_board.pack(side=tk.TOP)
    self.control_center = tk.Frame(self.form, bg='white')
    self.control_center.pack(side=tk.TOP, fill=tk.X)

    # endregion: Layout

    # Status bar
    self.next_stone = tk.Label(self.status_bar, bd=0)
    self.next_stone.pack(side=tk.LEFT, padx=2)
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
          frame, cursor='hand2', relief='flat', overrelief='raised', bd=0,
          highlightthickness=0)
        self.positions[coord].coord = coord
        self.positions[coord].bind('<Button-1>', self.on_board_press)
        self.positions[coord].pack(side=tk.LEFT)

    # Control center
    self.btnRestart = tk.Button(self.control_center, text='Restart',
                                command=self.restart)
    self.btnRestart.pack(side=tk.LEFT, padx=2, pady=2)
    self.btnUndo = tk.Button(self.control_center, text="Undo",
                             command=self.undo)
    self.btnUndo.pack(side=tk.LEFT, padx=2, pady=2)
    self.btnRedo = tk.Button(self.control_center, text="Redo",
                             command=self.redo)
    self.btnRedo.pack(side=tk.LEFT, padx=2, pady=2)
    self.btnAuto = tk.Button(self.control_center, text="Auto")
    self.btnAuto.pack(side=tk.RIGHT, padx=2, pady=2)

    # endregion: Design form

    self.refresh()

  # region: Properties

  @property
  def lastdir(self):
    if self.filename is None:
      return os.getcwd()
    else:
      paths = re.split(r'/|\\]', self.filename)
      return '/'.join(paths[:-1])

  # endregion: Properties

  # region: Public Methods

  def show(self):
    self.form.after(1, self.move_to_center)
    self.form.mainloop()

  # endregion: Public Methods

  # region: Private Methods

  def move_to_center(self):
    sh = self.form.winfo_screenheight()
    sw = self.form.winfo_screenwidth()
    h, w = self.form.winfo_height(), self.form.winfo_width()
    x = sw // 2 - w // 2
    y = sh // 2 - h // 2
    self.form.geometry('{}x{}+{}+{}'.format(w, h, x, y))

  def restart(self):
    self.filename = None
    self.game.restart()
    self.refresh()

  def bind(self, game):
    assert isinstance(game, Game)
    self.game = game

  def set_image(self, coord, color=None, factor=1):
    color = self.game[coord] if color is None else color

    if color:
      # If color is not 0, place stone
      self.positions[coord].config(image=self.stones[color*factor])
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
    if len(self.game.records) > 0:
      self.set_image(self.game.records[-1], factor=2)
    # Refresh control center
    self.update_control_center()
    # Update title
    self.update_title()

  def update_title(self):
    filename = 'New Game'
    if self.filename is not None:
      # Hide directory information
      paths = re.split(r'/|\\]', self.filename)
      filename = paths[-1]
      # Hide extension 'cause it provides no information
      filename = filename[:-4]
    title = 'Gomoku - {}'.format(filename)
    self.form.title(title)

  def update_status(self):
    stat = self.game.status
    if stat == 0:
      color = self.game.next_stone
      self.next_stone.config(image=self.stones[color])
      self.status.config(
        text="{}'s turn".format("Black" if color == 1 else "White"))
    elif stat in [-1, 1]:
      self.next_stone.config(image=self.stones[stat*2])
      self.status.config(
        text="{} wins!".format("Black" if stat == 1 else "White"))
    else:
      self.next_stone.config(image=self.stones[0])
      self.status.config(text='Draw!')

  def update_control_center(self):
    # Disable button auto
    self.btnAuto.config(state=tk.DISABLED)
    # Restart and Undo
    state = tk.NORMAL if len(self.game.records) > 0 else tk.DISABLED
    self.btnRestart.config(state=state)
    self.btnUndo.config(state=state)
    # Undo
    state = tk.NORMAL if len(self.game.redos) > 0 else tk.DISABLED
    self.btnRedo.config(state=state)

  def save_game(self, _):
    filename = filedialog.asksaveasfilename(
      initialdir=self.lastdir, title='Save game',
      filetypes=(("Gomoku files", '*.gmk'),))
    if filename == '':
      return
    if filename[-4:] != '.gmk':
      filename = '{}.gmk'.format(filename)

    self.game.save(filename)
    # Print status
    self.filename = filename
    print(">> Game file saved to '{}'".format(filename))
    self.update_title()

  def load_game(self, _):
    filename = filedialog.askopenfilename(
      initialdir=self.lastdir, title='Load game',
      filetypes=(("Gomoku files", '*.gmk'),))
    if filename == '':
      return

    self.filename = filename
    self.bind(Game.load(filename))
    self.refresh()
    # Print status
    print(">> Loaded game file '{}'".format(filename))

  # endregion: Private Methods

  # region: Events

  def undo(self):
    if self.game.undo():
      self.refresh()

  def redo(self):
    if self.game.redo():
      self.refresh()

  def on_key_press(self, event):
    assert isinstance(event, tk.Event)

    flag = False
    if event.keysym == 'Escape':
      self.form.quit()
    elif event.keysym in ['j', 'Right']:
      self.redo()
    elif event.keysym in ['k', 'Left']:
      self.undo()
    elif event.keysym in ['h', 'Home']:
      flag = self.game.home()
    elif event.keysym in ['l', 'End']:
      flag = self.game.end()

    if flag:
      self.refresh()

  def on_board_press(self, event):
    button = event.widget
    coord = button.coord
    if not self.game[coord] and not self.game.status:
      flag = self.game.place_stone(*coord)
      if flag:
        self.refresh()

  # endregion: Events

  '''For some reason, do not remove this line'''


if __name__ == "__main__":
  TkBoard().show()

