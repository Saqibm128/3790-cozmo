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
                maybeWinner = self.boards[self.length - 1][0]
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


class UltimateBoard(Winnable):
    def __init__(self, length=3):
        super().__init__(length)
        self.length = length
        self.boards = []
        self.currentBoard = (-1, -1)  # If -1, -1 then any board is possible (player needs to choose)
        self.isDone = False

        for i in range(length):
            self.boards.append([])
            for j in range(length):
                self.boards[i].append(Board(length))

    """
    If first move or we end up going to board which goes to complete board, return true
    """
    def needToPickNextBoard(self):
        return self.currentBoard == (-1,-1)

    def play(self, x, y):
        if (self.currentBoard == (-1, -1)):
            raise Exception("Pick 3 by 3 sub-board first!")
        if (self.isDone):
            raise Exception("Game is already finished")
        x_sup, y_sup = self.currentBoard[0], self.currentBoard[1]
        result = self.boards[x_sup][y_sup].play(x, y)
        if result != Tile.EMPTY:
            raise Exception("Board tile is already occupied")
        else:
            self.changeCurrentPlayer()
            self.changeBoardsCurrentPlayer(self.currentPlayer)
            if (self.boards[x][y].isDone):
                self.currentBoard = (-1, -1)
            else:
                self.currentBoard = (x, y)
        self.winner() #updates isdone

    def changeBoardsCurrentPlayer(tile):
        for x in range(length):
            for y in range(length):
                self.boards[x][y].currentPlayer = tile;


    """
    Will only work if we can choose a board, otherwise we get back an error
    newBoard should be a tuple
    """
    def chooseBoard(self, newBoard):
        if not self.needToPickNextBoard():
            raise Exception("Should not pick a new board!")
        else:
            self.currentBoard = newBoard

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

class CPUGame():
    def __init__(self, board=None):
        if board is None:
            self.board = Board()
        else:
            self.board = board
    def nextMove(self):
        valid = list()
        for x in range(3):
            toAppend = ""
            for y in range(3):
                toAppend += "|" + self.board.boards[x][y].value + "|"
            print(toAppend+"\n")
            print("____________"+"\n")

        for x in range(3):
            for y in range(3):
                if self.board.boards[x][y] == Tile.EMPTY:
                    tempBoard = copy.deepcopy(self.board)
                    # try to win!
                    tempBoard.play(x, y)
                    if self.board.winner() != Tile.EMPTY or self.board.winner() == Tile.NO_WIN:
                        return (x, y)
                    tempBoard = copy.deepcopy(self.board)
                    #avoid letting other player win by beating him to the spot
                    tempBoard.changeCurrentPlayer() #think as other player
                    tempBoard.play(x, y)
                    if self.board.winner() != Tile.EMPTY or self.board.winner() == Tile.NO_WIN:
                        return (x, y)
                    valid.append((x,y))
        return valid[randint(0, len(valid - 1))]



if __name__ == "__main__":
    print("")
    board = Board()
    game = CPUGame(board=board)
    while not board.isDone:
        x = int(input("x"))
        y = int(input("y"))
        board.play(x, y)
        print("{}".format(board.currentPlayer))
        x, y = game.nextMove()
        if not board.isDone:
            board.play(x, y)
        print(board.boards)
