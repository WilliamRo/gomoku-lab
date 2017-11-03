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
from tframe.models.rl.interfaces import Player


stone_size = 21
mid = (stone_size - 1) // 2
WIN_BG = {-1: [92, 186, 249], 1: [243, 60, 28]}
WIN_BG_TK = {1: 'OrangeRed2', -1: 'SteelBlue1'}
TIE_BG = [206, 237, 77]
TIE_BG_TK = 'chartreuse2'


class Images:

  rad = (stone_size - 1) / 2
  scale = np.arange(stone_size) - rad
  X = np.vstack((scale.reshape(1, stone_size),) * stone_size)
  Y = np.hstack((scale.reshape(stone_size, 1),) * stone_size)
  D = np.round(np.sqrt(X ** 2 + Y ** 2))
  D = np.stack([D] * 3, axis=2)

  @staticmethod
  def grid(i, j, bgcolor=None, emphasize=False, emcolor=None,
            with_arr=False):
    assert 0 <= i < 15 and 0 <= j < 15
    bgcolor = [255, 255, 255] if bgcolor is None else bgcolor
    emcolor = [255, 0, 0] if emcolor is None else emcolor

    arr = np.ones([stone_size, stone_size, 3], dtype=np.uint8)
    for k in range(3):
      arr[:, :, k] = bgcolor[k]
    mask = Images.D > Images.rad - 3
    arr[mask] = 255

    # Vertical
    if i == 0:
      arr[mid:, mid, :] = 0
    elif i == 14:
      arr[:mid+1, mid, :] = 0
    else:
      arr[:, mid, :] = 0
    # Horizontal
    if j == 0:
      arr[mid, mid:, :] = 0
    elif j == 14:
      arr[mid, :mid+1, :] = 0
    else:
      arr[mid, :, :] = 0
    # Special position
    r = 2
    if (i, j) in [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]:
      arr[mid-r:mid+r+1, mid-r:mid+r+1, :] = 0
    # Emphasize
    if emphasize:
      arr[mid, mid, :] = emcolor
      for di, dj in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
        for m in range(1, 4):
          arr[mid + m * di, mid + m * dj] = emcolor

    img = Image_.fromarray(arr, 'RGB')
    if with_arr:
      return ImageTk.PhotoImage(img), arr
    else:
      return ImageTk.PhotoImage(img)

  @staticmethod
  def stone(color, bgarr=None):
    '''
    Generate a binary image for stone
    :param color: integer in {-1, 1}, -1 for white, 1 for black, 0 for draw
                                       -2/2 for highlighted white/black
    :return: An instance of ImageTk.PhotoImage
    '''
    if color not in [3, -3, 0]:
      bgcolor = [255, 255, 255]
    elif color == 0:
      bgcolor = TIE_BG
    else:
      bgcolor = WIN_BG[color / 3]

    if bgarr is not None:
      assert isinstance(bgarr, np.ndarray)
      arr = bgarr.copy()
    else:
      arr = np.zeros([stone_size, stone_size, 3], dtype=np.uint8)
      for k in range(3):
        arr[:, :, k] = bgcolor[k]

    # Calculate distance to origin for each pixel
    rad = Images.rad
    D = Images.D

    # Generate images
    rad = rad - 1
    if color in [-1, 1, -2, 2, -3, 3]:
      mask = D < rad
      arr[mask] = 255
      mask = D <= rad if color > 0 else D == rad
      arr[mask] = 0
      if color in [-2, 2, -3, 3]:
        brush = 255 if color > 0 else 0
        half = int(np.round(rad / 2))
        r = half
        arr[mid-1:mid+2, mid-r+1:mid+r, :] = brush
        arr[mid-r+1:mid+r, mid-1:mid+2, :] = brush

        rs = 0  # keep it
        arr[mid, mid-r+1-rs:mid+r+rs, :] = brush
        arr[mid-r+1-rs:mid+r+rs, mid, :] = brush
    else:
      mask = D <= rad
      arr[mask] = 0
      mask = D <= np.round(rad / 2)
      arr[mask] = 255

    # Convert array to PhotoImage
    img = Image_.fromarray(arr, 'RGB')
    return ImageTk.PhotoImage(img)


class TkBoard(object):
  def __init__(self, game=None, player=None):
    self.game = None
    game = Game() if game is None else game
    self.bind(game)
    self.filename = None

    self.form = tk.Tk()
    self.grids = {}
    self.grids_arr = {}
    self.highlight_grids = {}
    # Images must be generated after an instance of Tk has been created
    self.stones = {1: Images.stone(1), 0: Images.stone(0), -1: Images.stone(-1),
                   2: Images.stone(2), -2: Images.stone(-2),
                   3: Images.stone(3), -3: Images.stone(-3)}
    self.positions = {}

    self.tips = True
    self.reasonable_moves = None
    self.coords_with_level = None
    self.tip_side = 1
    self.shelter = []

    self.auto_policy = self.default_policy
    self.player = player
    if player is not None:
      if not isinstance(player, Player):
        raise TypeError('player must be an instance of Player')

    # region: Design form

    # region: Layout

    self.form.title('Gomoku')
    self.form.config(bg='white')
    self.form.bind('<Key>', self.on_key_press)
    self.form.bind('<Control-s>', self.save_game)
    self.form.bind('<Control-l>', self.load_game)
    self.form.resizable(width=False, height=False)

    padx = 8
    self.status_bar = tk.Frame(self.form, bg='white')
    self.status_bar.pack(side=tk.TOP, fill=tk.X, padx=padx)
    self.chess_board = tk.Frame(self.form, bg='white')
    self.chess_board.pack(side=tk.TOP)
    self.control_center = tk.Frame(self.form, bg='white')
    self.control_center.pack(side=tk.TOP, fill=tk.X, padx=padx)

    # endregion: Layout

    # Status bar
    self.next_stone = tk.Label(self.status_bar, bd=0)
    self.next_stone.pack(side=tk.LEFT, padx=2)
    self.status = tk.Label(self.status_bar, text='Status bar', bg='white')
    self.status.pack(side=tk.LEFT, padx=0)
    self.moves = tk.Label(self.status_bar, text='', bg='white')
    self.moves.pack(side=tk.RIGHT, padx=1)

    # Chess board
    for i in range(15):
      frame = tk.Frame(self.chess_board, bg='white')
      frame.pack(side=tk.TOP)
      for j in range(15):
        coord = (i, j)
        img, arr = Images.grid(i, j, with_arr=True)
        self.grids[coord] = img
        self.grids_arr[coord] = arr
        self.highlight_grids[coord] = Images.grid(i, j, emphasize=True)
        self.positions[coord] = tk.Button(
          frame, cursor='hand2', relief='flat', overrelief='raised', bd=0,
          highlightthickness=0)
        self.positions[coord].coord = coord
        self.positions[coord].bind('<Button-1>', self.on_board_press)
        self.positions[coord].bind('<Button-3>', self.on_board_right_click)
        self.positions[coord].pack(side=tk.LEFT)

    # Control center
    pady = 5
    self.btnRestart = tk.Button(self.control_center, text='Restart',
                                command=self.restart)
    self.btnRestart.pack(side=tk.LEFT, padx=2, pady=pady)
    self.btnUndo = tk.Button(self.control_center, text="Undo",
                             command=self.undo)
    self.btnUndo.pack(side=tk.LEFT, padx=2, pady=pady)
    self.btnRedo = tk.Button(self.control_center, text="Redo",
                             command=self.redo)
    self.btnRedo.pack(side=tk.LEFT, padx=2, pady=pady)
    self.btnAuto = tk.Button(self.control_center, text="Auto",
                             command=self.auto)
    self.btnAuto.pack(side=tk.RIGHT, padx=2, pady=pady)

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

  # region : Refresh

  def refresh(self):
    assert isinstance(self.game, Game)
    self.shelter.clear()
    self.reasonable_moves = None
    self.coords_with_level = None
    if self.tips and self.game.status == self.game.NONTERMINAL:
      self.reasonable_moves = self.game.recommended_moves
      self.coords_with_level = self.game.coords_with_color(
        self.game.next_stone * self.tip_side)

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
    bgcolor = 'white'
    if stat == Game.NONTERMINAL:
      color = self.game.next_stone
      self.next_stone.config(image=self.stones[color])
      self.status.config(
        text="{}'s turn".format("Black" if color == 1 else "White"))
    elif stat in [-1, 1]:
      self.next_stone.config(image=self.stones[stat * 3])
      self.status.config(
        text="{} wins!".format("Black" if stat == 1 else "White"))
      bgcolor = WIN_BG_TK[stat]
    else:
      self.next_stone.config(image=self.stones[0])
      self.status.config(text='Draw!')
      bgcolor = TIE_BG_TK

    self.moves.config(text='{} moves'.format(self.game.moves))
    self.status.config(bg=bgcolor)
    self.moves.config(bg=bgcolor)
    self.status_bar.config(bg=bgcolor)

  # endregion : Refresh

  def auto(self):
    if self.game.status != Game.NONTERMINAL:
      return
    if self.player is None:
      next_position = self.auto_policy()
      flag = self.game.place_stone(int(next_position[0]), int(next_position[1]))
      if flag:
        self.refresh()
    else:
      self.player.next_step(self.game)
      self.refresh()

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

  def set_image(self, coord, token=None, factor=1):
    token = self.game[coord] if token is None else token

    if token:
      # If color is not 0, place stone
      image = Images.stone(token * factor, self.grids_arr[coord])
      self.shelter.append(image)
      self.positions[coord].config(image=image)
    else:
      # Else show grid
      image = self.grids[coord]
      if self.tips:
        if (self.coords_with_level is not None
            and coord in self.coords_with_level.keys()):
          pct = self.coords_with_level[coord] / (
            max(self.coords_with_level.values()) + 1)
          bgcolor = [255 - int((255 - c) * pct) for c in WIN_BG[
            self.game.next_stone * self.tip_side]]

          image = Images.grid(coord[0], coord[1], bgcolor)
          self.shelter.append(image)

        if (self.reasonable_moves is not None
            and coord in self.reasonable_moves):
          image = self.highlight_grids[coord]
      self.positions[coord].config(image=image)

  def update_control_center(self):
    # Disable button auto
    self.btnAuto.config(state=tk.DISABLED if self.game.status else tk.ACTIVE)
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
    elif event.keysym in ['a']:
      self.auto()
    elif event.keysym in ['t']:
      self.tips = not self.tips
      flag = True
    elif event.keysym in ['r']:
      self.tip_side *= -1
      flag = True
    elif event.keysym in ['d']:
      situation = self.game.situation
      flag = False

    if flag:
      self.refresh()

  def on_board_press(self, event):
    button = event.widget
    coord = button.coord
    if not self.game[coord] and not self.game.status:
      flag = self.game.place_stone(*coord)
      if flag:
        self.refresh()

  def on_board_right_click(self, event):
    coord = event.widget.coord
    print('>> Position {}'.format(coord))

  # endregion: Events

  # region : Other Methods

  def default_policy(self):
    moves = self.game.recommended_moves
    if moves is None:
      moves = self.game.legal_moves
    index = np.random.randint(0, len(moves))
    return moves[index]

  # endregion : Other Methods

  '''For some reason, do not remove this line'''


if __name__ == "__main__":
  TkBoard().show()

