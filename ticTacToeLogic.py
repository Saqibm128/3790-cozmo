from enum import Enum
from addict import Dict
import copy
from random import randint


class Tile(Enum):
    X = 'X'
    O = 'O'
    EMPTY = '.'  # Game can still continue
    # Game cannot be continued or is already finished. We assume a full board is this, even if it is already catscratch.
    NO_WIN = 'none'

    def winner(self):
        return self

    def isDone(self):
        return self == Tile.X or self == Tile.O
    # Json form
    def dict(self):
        return {"tile": self.name}

class Winnable:
        def __init__(self, length):
            self.length = length
            self.boards = []
            self.currentPlayer = Tile.X

        def winner(self):
            # did we win horizontally?
            for i in range(self.length):
                maybeWinner = self.boards[i][0].winner()
                for j in range(self.length):
                    if self.boards[i][j].winner() != maybeWinner or self.boards[i][j].winner() == Tile.EMPTY:
                        maybeWinner = Tile.EMPTY
                if maybeWinner != Tile.EMPTY and maybeWinner != Tile.NO_WIN:
                    self.isDone = True
                    return maybeWinner
            # did we win vertically?
            for j in range(self.length):
                maybeWinner = self.boards[0][j].winner()
                for i in range(self.length):
                    if self.boards[i][j].winner() != maybeWinner or self.boards[i][j].winner() == Tile.EMPTY:
                        maybeWinner = Tile.EMPTY
                if maybeWinner != Tile.EMPTY and maybeWinner != Tile.NO_WIN:
                    self.isDone = True
                    return maybeWinner

            # did we win diagonally left to right
            maybeWinner = self.boards[0][0].winner()
            for i in range(self.length):
                maybeWinner = self.boards[0][0]
                if self.boards[i][i].winner() != maybeWinner or self.boards[i][i].winner() == Tile.EMPTY:
                    maybeWinner = Tile.EMPTY
            if maybeWinner != Tile.EMPTY and maybeWinner != Tile.NO_WIN:
                self.isDone = True
                return maybeWinner

            # did we win diagonally right to left
            maybeWinner = self.boards[self.length - 1][0].winner()
            for i in range(self.length):
                if self.boards[self.length - i - 1][i].winner() != maybeWinner or self.boards[self.length - i - 1][i].winner() == Tile.EMPTY:
                    maybeWinner = Tile.EMPTY
            if maybeWinner != Tile.EMPTY and maybeWinner != Tile.NO_WIN:
                self.isDone = True
                return maybeWinner
            if (self.noValidMovesLeft()):
                self.isDone = True
                return Tile.NO_WIN
            return Tile.EMPTY

        def noValidMovesLeft(self):
            for i in range(self.length):
                for j in range(self.length):
                    if self.boards[i][j].winner() == Tile.EMPTY:
                        return False
            return True

        def changeCurrentPlayer(self):
            self.currentPlayer = Tile.O if self.currentPlayer==Tile.X else Tile.X

        def dict(self):
            jsonDict = Dict()
            for i in range(self.length):
                for j in range(self.length):
                    jsonDict[i][j] = self.boards[i][j].dict()
            jsonDict.isDone = self.isDone
            jsonDict.currentPlayer = self.currentPlayer.name
            return jsonDict


class Board(Winnable):
    def __init__(self, length=3):
        super().__init__(length)
        self.length = length
        self.boards = []
        self.isDone = False

        for i in range(length):
            self.boards.append([])
            for j in range(length):
                self.boards[i].append(Tile.EMPTY)
    def __str__(self):
        toAppend = ""

        for x in range(self.length):
            for y in range(self.length):
                toAppend = "|" + self.boards[x][y].value + "|" + toAppend
            toAppend = "\n__________\n"+toAppend
        return toAppend

    def play(self, x, y):
        if (self.isDone):
            raise Exception("Game is already finished")
        if self.boards[x][y] == Tile.EMPTY:
            self.boards[x][y] = self.currentPlayer
            self.changeCurrentPlayer()
            self.winner() #updates isdone
            return Tile.EMPTY
        else:
            return self.boards[x][y]

class CPUOpponent():
    def __init__(self, board=None):
        if board is None:
            self.board = Board()
        else:
            self.board = board
    def nextMove(self):
        valid = list()


        if self.board.boards[1][1] == Tile.EMPTY:
            return (1,1)

        for x in range(3):
            for y in range(3):
                # if self.board.boards[x][y] == Tile.EMPTY:
                tempBoard = copy.deepcopy(self.board)
                # try to win!
                tempBoard.play(x, y)
                if tempBoard.isDone:
                    return (x, y)
                tempBoard = copy.deepcopy(self.board)
                #avoid letting other player win by beating him to the spot
                tempBoard.changeCurrentPlayer() #think as other player
                tempBoard.play(x, y)
                if tempBoard.isDone:
                    return (x, y)
                valid.append((x,y))
        return valid[randint(0, len(valid) - 1)]



if __name__ == "__main__":
    print("")
    board = Board()
    game = CPUOpponent(board=board)
    while not board.isDone:
        x = int(input("x"))
        y = int(input("y"))
        if board.play(x, y) != Tile.EMPTY:
            continue
        if not board.isDone:
            x, y = game.nextMove()
            print(x, y)
            board.play(x, y)
        else:
            print("DONE")
            print(board.winner())
        print(board)
    print("DONE")
    print(board.winner())
