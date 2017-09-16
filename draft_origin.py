from gomoku.game import Game

from gomoku import console


game = Game()
game.place_stone(7, 7)

console.clc()
console.print_board(game.board)

x = input('Input: ')
game.place_stone(7, 8)

console.clc()
console.print_board(game.board)




