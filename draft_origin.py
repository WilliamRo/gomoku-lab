from gomoku.game import Game

from tkboard import TkBoard


game = Game()
game.place_stone(7, 7)
game.place_stone(7, 8)

board = TkBoard(game)
board.show()






