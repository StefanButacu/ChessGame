
class Move:
    def __init__(self, piece, row, col, whiteKing, blackKing, board):
        self.__piece = piece
        self.__row = row
        self.__col = col
        self.__player = piece[0]
        self.__board = board
        self.__whiteKing = whiteKing
        self.__blackKing = blackKing
################ YOU CANT MOVE SOMETHING THAT WILL LET YOUR KING IN CHECK
    def getAllMoves(self):
        allPosibleMoves = {
            "p": self.getPawnMoves,
            "K": self.getKingMoves,
            "R": self.getRookMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "N": self.getHorseMoves,
        }
        return allPosibleMoves[self.__piece[1]]()



    def __isInBoard(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def getPawnMoves(self):
        directions = []
        moves = []
        if self.__piece[0] == "b":
            directions.append((1, 0))
            if self.__row == 1:
                directions.append((2, 0))
        else:
            directions.append((-1, 0))
            if self.__row == 6:
                directions.append((-2, 0))
        for (i, j) in directions:
            newRow = self.__row + i
            newCol = self.__col + j
            if self.__isInBoard(newRow, newCol):
                if self.__board[newRow][newCol] == "--":
                    moves.append((newRow, newCol))
        # for destroying enemy piece
        if self.__player == "b":
            if self.__isInBoard(self.__row +1, self.__col -1) and self.__board[self.__row +1][self.__col - 1][0] == 'w':
                moves.append((self.__row +1, self.__col - 1))
            if self.__col  + 1 < 8 and self.__board[self.__row +1][self.__col  + 1][0] == 'w':
                moves.append((self.__row +1, self.__col + 1))
        if self.__player == "w":
            if self.__col - 1 >= 0 and self.__board[self.__row -1][self.__col - 1][0] == 'b':
                moves.append((self.__row -1, self.__col - 1))
            if self.__col  + 1 < 8 and self.__board[self.__row -1][self.__col + 1][0] == 'b':
                moves.append((self.__row -1, self.__col + 1))
        return moves

    def getHorseMoves(self):
        moves = []
        directions = [(1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1)]
        for i, j in directions:
            newRow = self.__row + i
            newCol = self.__col + j
            if self.__isInBoard(newRow, newCol):
                if self.__board[newRow][newCol] == "--":
                    moves.append((newRow, newCol))
                if self.__board[newRow][newCol][0] == 'w' and self.__player == 'b':
                    moves.append((newRow, newCol))
                if self.__board[newRow][newCol][0] == 'b' and self.__player == 'w':
                    moves.append((newRow, newCol))
        return moves

    def getQueenMoves(self):
        return self.getRookMoves() + self.getBishopMoves()

    def getBishopMoves(self):
        moves = []
        # top-left
        newRow = self.__row - 1
        newCol = self.__col - 1
        while self.__isInBoard(newRow, newCol):
            if self.__board[newRow][newCol] == "--":
                moves.append((newRow, newCol))
                newRow -= 1
                newCol -= 1
                continue
            if self.__player == self.__board[newRow][newCol][0]:
                break
            else:
                moves.append((newRow, newCol))
                break

        # top-right
        newRow = self.__row - 1
        newCol = self.__col + 1
        while self.__isInBoard(newRow, newCol):
            if self.__board[newRow][newCol] == "--":
                moves.append((newRow, newCol))
                newRow -= 1
                newCol += 1
                continue
            if self.__player == self.__board[newRow][newCol][0]:
                break
            else:
                moves.append((newRow, newCol))
                break

        # bot-left
        newRow = self.__row + 1
        newCol = self.__col - 1
        while self.__isInBoard(newRow, newCol):
            if self.__board[newRow][newCol] == "--":
                moves.append((newRow, newCol))
                newRow += 1
                newCol -= 1
                continue
            if self.__player == self.__board[newRow][newCol][0]:
                break
            else:
                moves.append((newRow, newCol))
                break

        # bot-right
        newRow = self.__row + 1
        newCol = self.__col + 1
        while self.__isInBoard(newRow, newCol):
            if self.__board[newRow][newCol] == "--":
                moves.append((newRow, newCol))
                newRow += 1
                newCol += 1
                continue
            if self.__player == self.__board[newRow][newCol][0]:
                break
            else:
                moves.append((newRow, newCol))
                break
        return moves

    def getRookMoves(self):
        moves = []
        # you can do this smarter by multiplying the amount of squares that a rook can move
        # can move up to 8 squares: if there is an ally piece you end that direction
        #                           if there is a enemy peice you add that move and then end direction
        #                           if you exit the board before checking the maximum 8 squares
        # up
        newRow = self.__row - 1
        newCol = self.__col
        while self.__isInBoard(newRow, newCol):
            if self.__board[newRow][newCol] == "--":
                moves.append((newRow, newCol))
            if self.__player == 'b' and self.__board[newRow][newCol][0] == 'w':
                moves.append((newRow, newCol))
                break
            if self.__player == 'w' and self.__board[newRow][newCol][0] == 'b':
                moves.append((newRow, newCol))
                break
            if self.__player == self.__board[newRow][newCol][0]:
                break
            newRow -= 1

        # down
        newRow = self.__row + 1
        newCol = self.__col
        while self.__isInBoard(newRow, newCol):
            if self.__board[newRow][newCol] == "--":
                moves.append((newRow, newCol))
            if self.__player == 'b' and self.__board[newRow][newCol][0] == 'w':
                moves.append((newRow, newCol))
                break
            if self.__player == 'w' and self.__board[newRow][newCol][0] == 'b':
                moves.append((newRow, newCol))
                break
            if self.__player == self.__board[newRow][newCol][0]:
                break
            newRow += 1

        # left
        newRow = self.__row
        newCol = self.__col - 1
        while self.__isInBoard(newRow, newCol):
            if self.__board[newRow][newCol] == "--":
                moves.append((newRow, newCol))
            if self.__player == 'b' and self.__board[newRow][newCol][0] == 'w':
                moves.append((newRow, newCol))
                break
            if self.__player == 'w' and self.__board[newRow][newCol][0] == 'b':
                moves.append((newRow, newCol))
                break
            if self.__player == self.__board[newRow][newCol][0]:
                break
            newCol -= 1
        # right
        newRow = self.__row
        newCol = self.__col + 1
        while self.__isInBoard(newRow, newCol):
            if self.__board[newRow][newCol] == "--":
                moves.append((newRow, newCol))
            if self.__player == 'b' and self.__board[newRow][newCol][0] == 'w':
                moves.append((newRow, newCol))
                break
            if self.__player == 'w' and self.__board[newRow][newCol][0] == 'b':
                moves.append((newRow, newCol))
                break
            if self.__player == self.__board[newRow][newCol][0]:
                break
            newCol += 1
        return moves

    def getKingMoves(self):
        moves = []
        direction = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]   # king near king not possible
        for (i ,j) in direction:
            newRow = self.__row + i
            newCol = self.__col + j
            if self.__isInBoard(newRow, newCol):
                if self.__board[newRow][newCol] == "--" or ( self.__board[newRow][newCol][0] != self.__player and self.__board[newRow][newCol][1] != "K"):
                        moves.append((newRow, newCol))

        return moves

    def allValidMoves(self, moves):
        pass
