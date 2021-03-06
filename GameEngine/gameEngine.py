import pygame

from GameEngine.movements import Move
from GameEngine.Button import Button

darkColor = (184, 139, 74)
lightColor = (227, 193, 111)
activeColor = (144, 170, 134)
futureColor = (234, 161, 145)
white = (255, 255, 255)
textColor = (56, 114, 108)


class Game:
    def __init__(self):
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill((0, 0, 0))
        pygame.display.set_caption("Chess")
        pygame.display.flip()
        self.__board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.__currentPlayer = 'w'
        self.__blackCheck = False
        self.__whiteCheck = False
        self.__stalemate = False
        """
        for castling you need for one color leftRookMove, kingMoved, rightRookMoved 
        """
        self.__rookOrKingMoved = {
            "w": {"lR": False,
                  "K": False,
                  "rR": False,
                  },
            "b": {"lR": False,
                  "K": False,
                  "rR": False,
                  },
        }
        self.__whiteDraw = False
        self.__blackDraw = False
        self.__whiteDrawButton = Button(self.screen, (990, 700), pygame.font.SysFont('Consolas', 30), "Draw")
        self.__whiteDrawButton.showButton()
        self.__blackDrawButton = Button(self.screen, (990, 300), pygame.font.SysFont('Consolas', 30), "Draw")
        self.__blackDrawButton.showButton()
        self.__timePlayerOne = 900
        self.__timePlayerTwo = 900
        self.__enPassantSquare = ()

    def drowGrid(self):
        """
        Drows the chess grid
        :return:
        """
        for x in range(8):
            for y in range(8):
                rect = pygame.Rect(x * 100, y * 100, 100, 100)
                if (x + y) % 2 == 0:
                    pygame.draw.rect(self.screen, lightColor, rect)
                else:
                    pygame.draw.rect(self.screen, darkColor, rect)
        self.placePieces()

    def placePieces(self):
        """
        Drows the pieces as images on grid
        :return:
        """
        for x in range(8):
            for y in range(8):

                if self.__board[x][y] != "--":
                    image = pygame.image.load("./images/" + self.__board[x][y] + ".png").convert_alpha()
                    rect = image.get_rect()
                    rect.center = ((2 * y + 1) * 50, (2 * x + 1) * 50)
                    self.screen.blit(image, rect)

    def getColorFromIndex(self, row, col):
        """
        return the default color of the square
        :param row: int
        :param col: int
        :return:
        """
        return lightColor if (row + col) % 2 == 0 else darkColor

    def unHighlightSquare(self, row, col):
        """
        Colors the square determinated by row and col to its default color
        :param row: int assume  0 <= row < 8
        :param col: int  assume 0 <= col < 8
        :return:
        """
        pygame.draw.rect(self.screen, self.getColorFromIndex(row, col), pygame.Rect(col * 100, row * 100, 100, 100))

    def highlightSquare(self, row, col):
        """
        Highlights the square determinated by row, col with activeColor
        :param row: int
        :param col: int
        :return:
        """
        s = pygame.Surface((100, 100))
        s.set_alpha(125)  # transperancy
        s.fill(activeColor)
        self.screen.blit(s, (col * 100, row * 100))

    def getStrTimeFromSecond(self, seconds):
        """
        :param seconds: int
        :return: a formatted string -> minutes : seconds
        """

        mins = seconds // 60
        seconds %= 60
        return str(mins) + ":" + str(seconds)

    def __checkGameOver(self):
        if self.__isStalemate():
            self.__printScreenMessage(" Draw by stalemate ")
            return True
        elif self.__isCheckmate():
            message = "Black" if self.__currentPlayer == "b" else "White"

            self.__printScreenMessage(message + " lost by checkmate ")
            return True
        elif self.__isDraw():
            message = "Draw agreed by both players"
            self.__printScreenMessage(message)
            return True
        elif self.__isOutOfTime("w"):
            message = "Player one run out of time"
            self.__printScreenMessage(message)
            return True
        elif self.__isOutOfTime("b"):
            message = "Player two run out of time"
            self.__printScreenMessage(message)
            return True
        return False

    def __isOutOfTime(self, player):
        """

        :param player: b or w  - the color of the player
        :return: True -if the player has no more seconds
        """
        if player == "w":
            if self.__timePlayerOne == 0:
                return True
        elif player == "b":
            if self.__timePlayerTwo == 0:
                return True
        return False

    def run(self):
        """
        Main loop for game
        :return:
        """

        global arr
        sqList = []
        nextMoves = []
        castleMoves = []
        castleSquare = ()
        self.drowGrid()
        font = pygame.font.SysFont('Consolas', 30)

        playerOneText = font.render("Player 1", True, white)
        playerOneRect = playerOneText.get_rect()
        playerOneRect.center = (1000, 600)

        playerTwoText = font.render("Player 2", True, white)
        playerTwoRect = playerTwoText.get_rect()
        playerTwoRect.center = (1000, 200)

        clockPlayerOne = pygame.time.Clock()
        textPlayerOne = self.getStrTimeFromSecond(self.__timePlayerOne)

        clockPlayerTwo = pygame.time.Clock()
        textPlayerTwo = self.getStrTimeFromSecond(self.__timePlayerTwo)

        self.screen.blit(font.render(textPlayerOne, True, white, (0, 0, 0)), (950, 650))
        self.screen.blit(font.render(textPlayerTwo, True, white, (0, 0, 0)), (950, 250))

        gameOver = False
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        while True:
            self.screen.blit(playerOneText, playerOneRect)

            self.screen.blit(playerTwoText, playerTwoRect)

            gameOver = self.__checkGameOver()

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    if not gameOver:
                        if self.__currentPlayer == 'w':
                            self.__timePlayerOne -= 1
                            textPlayerOne = self.getStrTimeFromSecond(
                                self.__timePlayerOne) if self.__timePlayerOne > 0 else "GAME OVER"
                            # had to mask one 0 character that was exiting the surface
                            self.screen.blit(font.render("------", True, pygame.Color("Black"), pygame.Color("Black")),
                                             (950, 650))
                            self.screen.blit(font.render(textPlayerOne, True, white, (0, 0, 0)), (950, 650))
                            clockPlayerOne.tick(60)
                        else:
                            self.__timePlayerTwo -= 1
                            textPlayerTwo = self.getStrTimeFromSecond(
                                self.__timePlayerTwo) if self.__timePlayerTwo > 0 else "GAME OVER"
                            self.screen.blit(font.render("------", True, pygame.Color("Black"), pygame.Color("Black")),
                                             (950, 250))

                            self.screen.blit(font.render(textPlayerTwo, True, white, (0, 0, 0)), (950, 250))
                            clockPlayerTwo.tick(60)

                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        for row in self.__board:
                            print(row)
                        print(self.__rookOrKingMoved)

                if event.type == pygame.MOUSEBUTTONDOWN and not gameOver:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // 100
                    row = pos[1] // 100
                    if self.__currentPlayer == 'w':
                        self.__checkDrawButton(self.__whiteDrawButton, pygame.mouse.get_pos()[0],
                                               pygame.mouse.get_pos()[1])
                    else:
                        self.__checkDrawButton(self.__blackDrawButton, pygame.mouse.get_pos()[0],
                                               pygame.mouse.get_pos()[1])

                    if col >= 8 or row >= 8:
                        continue
                    sqSelected = (row, col)
                    if len(sqList) == 0:
                        # highlight current square
                        if self.__board[row][col][0] == self.__currentPlayer and self.__board[row][col] != '--':
                            self.highlightSquare(row, col)
                            sqList.append(sqSelected)

                            nextMoves = self.possibleMovesByPiece(row, col)

                            # if is pawn need to prepare the enPassantMove

                            # if is rook or king add the "Castle Moves"
                            # if you click left side of board
                            # else you click right side and do that veirfications

                            # daca apas pe rook - highlightuiesc mutarea specifica rook-ului ( stanga/dreapta)
                            # altfel daca apas pe king (
                            #

                            castleMoves.clear()
                            arr = []  # if both castle are availabele castle squares are 2

                            if self.__board[row][col][1] == "K":
                                # remove from nextMoves squares that are attacked by opponent's pieces
                                enemyPiece = "b" if self.__currentPlayer == "w" else "w"
                                for i in range(len(nextMoves) - 1, -1, -1):
                                    if self.__squareUnderAttack((nextMoves[i]), enemyPiece):
                                        del nextMoves[i]

                                kingLocation = self.__getWhiteKing() if self.__currentPlayer == "w" else self.__getBlackKing() # (row,col)
                                if self.__castleValid(kingLocation, "left"):
                                    castleMoves.append(self.__getCastleMoves("left"))
                                    if self.__currentPlayer == "w":
                                        self.highlightSquare(7,
                                                             0)  # highlight left white Rook if King was tapped - else highlight king
                                        castleSquare = (7, 0) if self.__board[row][col][1] == "K" else kingLocation
                                    else:
                                        self.highlightSquare(0, 0)  # highlight left black Rook
                                        castleSquare = (0, 0) if self.__board[row][col][1] == "K" else kingLocation
                                    arr.append(castleSquare)
                                if self.__castleValid(kingLocation, "right"):
                                    castleMoves.append(self.__getCastleMoves("right"))
                                    if self.__currentPlayer == "w":
                                        self.highlightSquare(7,
                                                             7)
                                        castleSquare = (7, 7)
                                    else:
                                        self.highlightSquare(0, 7)  # highlight left black Rook
                                        castleSquare = (0, 7)
                                    arr.append(castleSquare)

                            elif self.__board[row][col][1] == "R":
                                kingLocation = self.__getWhiteKing() if self.__currentPlayer == "w" else self.__getBlackKing()
                                if (row, col) == (0, 0) or (row, col) == (7, 0): # left rook
                                    if self.__castleValid(kingLocation, "left"):
                                        castleMoves.append(self.__getCastleMoves("left"))
                                        self.highlightSquare(kingLocation[0], kingLocation[1])
                                        castleSquare = kingLocation
                                        arr.append(castleSquare)
                                elif (row, col) == (0, 7) or (row, col) == (7, 7): # right rook
                                    if self.__castleValid(kingLocation, "right"):
                                        castleMoves.append(self.__getCastleMoves("right"))
                                        self.highlightSquare(kingLocation[0], kingLocation[1])
                                        castleSquare = kingLocation
                                        arr.append(castleSquare)

                            for (newRow, newCol) in nextMoves:
                                self.highlightSquare(newRow, newCol)
                        else:
                            sqList.clear()
                            continue
                    elif len(sqList) == 1:
                        sqList.append(sqSelected)

                        if self.__currentPlayer == 'w':
                            if self.__whiteCheck:
                                if self.__hasLegalMoves():
                                    self.__whiteCheck = False

                        else:
                            if self.__blackCheck:
                                if self.__hasLegalMoves():
                                    self.__blackCheck = False
                        ############### # Castling moves ###########

                        # unhighlight the moves
                        for singleCastleMove in castleMoves:
                            for row, col in singleCastleMove:
                                self.unHighlightSquare(row, col)
                        for row, col in sqList:
                            self.unHighlightSquare(row, col)

                        castleDo = False
                        for i in range(len(arr)):
                            if arr[i] == sqSelected and self.__board[arr[i][0]][arr[i][1]] and sqList[0] in castleMoves[
                                i]:
                                castleMoves = castleMoves[i]
                                castleDo = True
                                break

                        if castleDo:  # we need to click the king if first is rook, or vice-versa

                            newKingRow, newKingCol = castleMoves[0]
                            newRookRow, newRookCol = castleMoves[1]
                            lastRookRow, lastRookCol = castleMoves[2]
                            lastKingRow, lastKingCol = castleMoves[3]
                            self.__rookOrKingMoved[self.__currentPlayer]["K"] = True
                            if (lastRookRow, lastRookCol) == (7, 0) or (lastRookRow, lastRookCol) == (0, 0):
                                self.__rookOrKingMoved[self.__currentPlayer]["lR"] = True
                            else:
                                self.__rookOrKingMoved[self.__currentPlayer]["rR"] = True
                            # do the actual castling
                            self.__board[newKingRow][newKingCol] = "wK" if self.__currentPlayer == "w" else "bK"
                            self.__board[newRookRow][newRookCol] = "wR" if self.__currentPlayer == "w" else "bR"
                            self.__rookOrKingMoved[self.__currentPlayer]["K"] = True
                            if lastRookCol < 4:
                                self.__rookOrKingMoved[self.__currentPlayer]["lR"] = True
                            else:
                                self.__rookOrKingMoved[self.__currentPlayer]["rR"] = True
                            # remove the last pieces
                            self.__board[lastKingRow][lastKingCol] = "--"
                            self.__board[lastRookRow][lastRookCol] = "--"
                            self.__currentPlayer = 'b' if self.__currentPlayer == 'w' else 'w'
                            castleMoves.clear()
                            if not gameOver:  # to not overlap Pieces with the GameOver text
                                self.placePieces()
                            sqList.clear()
                        # NORMAL MOVES
                        elif sqSelected in nextMoves:
                            lastRow, lastCol = sqList[0][0], sqList[0][1]
                            newRow, newCol = sqList[1][0], sqList[1][1]
                            # enPassantSquare - you you jump by 2 squares the one in the middle is en passantSquare
                            if self.__board[lastRow][lastCol][1] == 'p' and sqSelected == self.__enPassantSquare:
                                if self.__currentPlayer == 'w':
                                    self.__board[newRow + 1][newCol] = "--"  # you have to eat that pawn

                                    self.unHighlightSquare(newRow+1,newCol)

                                else:
                                    self.__board[newRow - 1][newCol] = "--"
                                    self.unHighlightSquare(newRow-1,newCol)

                            if self.__board[lastRow][lastCol][1] == 'p' and abs(newRow - lastRow) == 2:
                                self.__enPassantSquare = ((newRow + lastRow) // 2, lastCol)
                            else:
                                self.__enPassantSquare = ()

                            # check if he moved the king/rook => you can no longer do the castle
                            if self.__board[lastRow][lastCol][1] == "K":
                                self.__rookOrKingMoved[self.__currentPlayer]["K"] = True
                            elif self.__board[lastRow][lastCol] == "wR" or self.__board[lastRow][lastCol] == "bR":
                                if (lastRow, lastCol) == (7, 0) or (lastRow, lastCol) == (
                                        0, 0):  # the left side specific
                                    self.__rookOrKingMoved[self.__currentPlayer]["lR"] = True
                                else:
                                    self.__rookOrKingMoved[self.__currentPlayer]["rR"] = True

                            # the the move if is not in check
                            self.__board[newRow][newCol] = self.__board[lastRow][
                                lastCol]  # "magical numbers" should had encapsulated this
                            self.__board[lastRow][lastCol] = "--"

                            # check for pawn promotion
                            if self.__checkPawnPromotion(newRow, newCol):
                                self.__board[newRow][newCol] = "--"
                                if self.__currentPlayer == "b":
                                    pieces = ["bQ", "bR", "bB", "bN"]
                                else:
                                    pieces = ["wQ", "wR", "wB", "wN"]
                                transformScale = ([20, 20], [20, 70], (70, 20), (70, 70))
                                rect = pygame.Rect(col * 100, row * 100, 100, 100)
                                if (col + row) % 2 == 0:
                                    pygame.draw.rect(self.screen, lightColor, rect)
                                else:
                                    pygame.draw.rect(self.screen, darkColor, rect)
                                for i in range(len(pieces)):
                                    image = pygame.image.load("./images/" + pieces[i] + ".png").convert_alpha()
                                    rect = image.get_rect()
                                    rect.width = 45
                                    rect.height = 45
                                    rect.center = (col * 100 + transformScale[i][0], row * 100 + transformScale[i][1])
                                    self.screen.blit(image, rect)
                                    pygame.display.update()
                                chosen = False
                                while not chosen:
                                    for event2 in pygame.event.get():
                                        if event2.type == pygame.MOUSEBUTTONDOWN:
                                            pos = pygame.mouse.get_pos()
                                            col2 = pos[0] // 100
                                            row2 = pos[1] // 100
                                            if not (col <= col2 < col + 1 and row <= row2 < row + 1):
                                                continue
                                            else:
                                                chosen = True
                                                if pos[0] % 100 <= 50 and pos[1] % 100 <= 50:
                                                    self.__board[row][col] = pieces[0]  # Queen chosen
                                                elif pos[0] % 100 <= 50 and pos[1] % 100 >= 50:
                                                    self.__board[row][col] = pieces[1]  # Rook chosen
                                                elif pos[0] % 100 >= 50 and pos[1] % 100 <= 50:
                                                    self.__board[row][col] = pieces[2]  # Bishop chonsen
                                                elif pos[0] % 100 >= 50 and pos[1] % 100 >= 50:  # Knight chosen
                                                    self.__board[row][col] = pieces[3]
                                # might repaint all
                            if self.__currentPlayer == 'b':
                                if self.__squareUnderAttack(self.__getWhiteKing(), "b"):
                                    self.__whiteCheck = True
                                   #  print("white check")
                            else:
                                if self.__squareUnderAttack(self.__getBlackKing(), "w"):
                                    self.__blackCheck = True
                                    # print("black check")
                            self.__currentPlayer = 'b' if self.__currentPlayer == 'w' else 'w'

                        # un-highlight selected squares
                        for row, col in sqList:
                            self.unHighlightSquare(row, col)
                        for (newRow, newCol) in nextMoves:
                            self.unHighlightSquare(newRow, newCol)
                        # un-highlight selected squares
                        sqList.clear()
            if not gameOver:  # to not overlap Pieces with the GameOver text
                self.placePieces()

            pygame.display.update()

    def leaveKingUnderAttackValidation(self, pieceMoves, currentRow, currentCol, currentPiece):
        """

        :param pieceMoves: an array of (int,int) which represents posible moves of pieces
        :param currentRow: int
        :param currentCol: int
        :param currentPiece: string, the piece
        :return: an array of (int,int) but with the moves that are valid, meaning that you cant move a piece
        and let your king to be under attack
        """
        for (newRow, newCol) in pieceMoves:
            # hipotetically do the move
            beforePiece = self.__board[newRow][newCol]
            self.__board[newRow][newCol] = currentPiece
            self.__board[currentRow][currentCol] = "--"
            # self.__board[newRow][newCol], self.__board[row][col] = self.__board[row][col], "--"
            # let s see if any enemy piece attaks the other king
            if self.__currentPlayer == 'w':
                # check for black pieces
                for i in range(8):  # we can format this part
                    for j in range(8):
                        if self.__board[i][j][0] == 'b':
                            attackerMove = Move(self.__board[i][j], i, j, self.__getWhiteKing(), self.__getBlackKing(),
                                                self.__board)
                            if self.__getWhiteKing() in attackerMove.getAllMoves():
                                pieceMoves = [elems for elems in pieceMoves if
                                              elems != (newRow, newCol)]  # list comperhensions works better at removing
            else:
                for i in range(8):  # we can format this part
                    for j in range(8):
                        if self.__board[i][j][0] == 'w':
                            attackerMove = Move(self.__board[i][j], i, j, self.__getWhiteKing(), self.__getBlackKing(),
                                                self.__board)
                            if self.__getBlackKing() in attackerMove.getAllMoves():
                                pieceMoves = [elems for elems in pieceMoves if elems != (newRow, newCol)]
            # undo the move
            self.__board[newRow][newCol], self.__board[currentRow][currentCol] = beforePiece, currentPiece
        return pieceMoves

    def possibleMovesByPiece(self, row, col):
        """

        :param row: int
        :param col: int
        :return: an array of (int,int) which represent the possible moves that could be done by the piece from the coordonates row,col
        """
        currentPiece = self.__board[row][col]
        move = Move(currentPiece, row, col, self.__getWhiteKing(), self.__getBlackKing(), self.__board,
                    self.__enPassantSquare)
        pieceMoves = move.getAllMoves()

        # check if after moving a piece the king is under attack
        pieceMoves = self.leaveKingUnderAttackValidation(pieceMoves, row, col, currentPiece)
        return pieceMoves

    def __getWhiteKing(self):
        """

        :return: (int,int) = coordonates of white king
        """
        for i in range(8):
            for j in range(8):
                if self.__board[i][j] == "wK":
                    return i, j
        raise Exception()

    # could be only one function which can do both, by giving the parameter color getColorKing(self,color)
    def __getBlackKing(self):
        """
        :return: (int,int) = coordonates of black king
        """
        for i in range(8):
            for j in range(8):
                if self.__board[i][j] == "bK":
                    return i, j
        raise Exception()

    def __hasLegalMoves(self):
        nrMoves = 0
        for i in range(8):
            for j in range(8):
                if self.__board[i][j][0] == self.__currentPlayer:
                    # see moves by this piece and add them to a contor
                    nrMoves += len(self.possibleMovesByPiece(i, j))
        if nrMoves == 0:  # no valid moves
            return False
        return True

    def __isStalemate(self):
        if self.__currentPlayer == 'w':
            if self.__whiteCheck == False and not self.__hasLegalMoves():
                return True
        elif self.__currentPlayer == 'b':
            if self.__blackCheck == False and not self.__hasLegalMoves():
                return True
        else:
            return False

    def __isCheckmate(self):
        if self.__currentPlayer == 'w':
            if self.__whiteCheck and not self.__hasLegalMoves():
                return True
        elif self.__currentPlayer == 'b':
            if self.__blackCheck and not self.__hasLegalMoves():
                return True
        else:
            return False

    def __squareUnderAttack(self, square, enemyColor):
        """

        :param square: (int, int) the coordonates of the square ( row, column)
        :param enemyColor: b/w
        :return: True if the square is attacked by any enemy piece
                False otherwise
        """
        if square in self.__computeAttackerSquares(enemyColor):
            return True
        return False

    def __computeAttackerSquares(self, attacker):
        """
        attacker - "b/w" - the attacker
        :return: a list of all attacked squares by the enemy player
        """
        attackerMoves = []

        for i in range(8):
            for j in range(8):
                if self.__board[i][j] != "--" and self.__board[i][j][0] == attacker:
                    if self.__board[i][j][1] == "p": # the only piece that attacks different that its moves
                        pawnMoves = Move(self.__board[i][j], i, j, self.__getWhiteKing(), self.__getBlackKing(),
                                              self.__board).getAllMoves() # moving and attacking
                        # from here i have to remove the moving squares
                        for k in range(len(pawnMoves)-1, -1, -1):

                            if pawnMoves[k][1] == j:  # if the next move is on the same column as my pawn means is a move
                                                    # not an attack
                                del pawnMoves[k]
                        attackerMoves += pawnMoves

                    else:
                        attackerMoves += Move(self.__board[i][j], i, j, self.__getWhiteKing(), self.__getBlackKing(),
                                              self.__board).getAllMoves()
                    # if its a pawn i have to remove the +1/-1 moves

        return attackerMoves

    def __checkPawnPromotion(self, row, col):
        """
        Check if a pawn cand be promoted and promotes it to a piece
        :param row: int
        :param col: int
        :return:
        """
        if self.__board[row][col][1] == 'p':
            if self.__currentPlayer == "w" and row == 0:
                return True
            elif self.__currentPlayer == "b" and row == 7:
                return True
        return False

    def __printScreenMessage(self, message):
        """
        Show the message on screen
        :param message:
        :return:
        """
        font = pygame.font.SysFont('Consolas', 30)
        font.set_bold(True)
        text = font.render(message, False, textColor)
        rect = pygame.Rect(300, 300, 500, 500)
        rect.center = (400, 600)

        textLocation = rect

        self.screen.blit(text, textLocation)

    def __castleValid(self, kingLocation, side):
        """
        Validates the castle movement
        You cannot castle:
            if the King or the Rook has already been moved in the game
            if the King is in check
            if there is a piece between the Rook and the King
            if the King is in check after castling
            if the square through which the King passes is under attack

        :param kingLocation: (int,int)
                side = the direction you want to castle, "left" or "right"
        :return: True - you can castle
                False - you cant castle
        """
        enemyColor = "b" if self.__currentPlayer == "w" else "w"

        if self.__squareUnderAttack(kingLocation, enemyColor):  # if the King is in check
            return False
        # check for left castle
        if side == "left":
            if self.__rookOrKingMoved[self.__currentPlayer]["K"] or self.__rookOrKingMoved[self.__currentPlayer][
                "lR"]:  # if the King or the Rook has already been moved in the game
                return False
            row, col = kingLocation
            newCol = col - 2
            col -= 1
            while col >= 1:
                if self.__board[row][col] != "--":  # if there is a piece between the Rook and the King
                    return False
                if col > 1 and self.__squareUnderAttack((row, col),
                                                        enemyColor):  # if the square through which the King passes is under attack
                    return False
                col -= 1
            if self.__squareUnderAttack((row, newCol), enemyColor):
                return False
            return True
        elif side == "right":
            if self.__rookOrKingMoved[self.__currentPlayer]["K"] or self.__rookOrKingMoved[self.__currentPlayer][
                "rR"]:  # if the King or the Rook has already been moved in the game
                return False
            row, col = kingLocation
            newCol = col + 2
            col += 1
            while col < 7:
                if self.__board[row][col] != "--":  # if there is a piece between the Rook and the King
                    return False
                if col < 6 and self.__squareUnderAttack((row, col),
                                                        enemyColor):  # if the square through which the King passes is under attack
                    return False
                col += 1
            if self.__squareUnderAttack((row, newCol), enemyColor):
                return False
            return True
        return False

    def __getCastleMoves(self, side):
        """

        :param side: "left/right"
                #NextKingPosition, nextRookPosition lastRookPosition
        :return: an array [(int,int), (int,int), (int, int), (int, int)]: on first position -> new king position
                                                : on second position -> new rook position
                                                : on third -> last rookPosition
                                                : on forth -> last kingPosition
        """

        # The King moves two squares in the direction of the Rook,
        # the Rook jumps over the King and lands on the square next to it.
        newPositions = []
        if self.__currentPlayer == "w":
            lastKingPosition = self.__getWhiteKing()
        else:
            lastKingPosition = self.__getBlackKing()
        if side == "left":

            nextKingPosition = (lastKingPosition[0], lastKingPosition[1] - 2)
            newPositions.append(nextKingPosition)
            nextRookPosition = (lastKingPosition[0], lastKingPosition[1] - 1)
            newPositions.append(nextRookPosition)
            if self.__currentPlayer == "w":
                newPositions.append((7, 0))
            else:
                newPositions.append((0, 0))

        elif side == "right":

            nextKingPosition = (lastKingPosition[0], lastKingPosition[1] + 2)
            newPositions.append(nextKingPosition)
            nextRookPosition = (lastKingPosition[0], lastKingPosition[1] + 1)
            newPositions.append(nextRookPosition)
            if self.__currentPlayer == "w":
                newPositions.append((7, 7))
            else:
                newPositions.append((0, 7))
        newPositions.append(lastKingPosition)
        return newPositions

    def __checkDrawButton(self, drawButton, mouseX, mouseY):
        if drawButton.rect.collidepoint(mouseX, mouseY):
            if self.__currentPlayer == 'w':
                self.__whiteDraw = True
            else:
                self.__blackDraw = True
            drawButton.changeBackground()

    def __isDraw(self):
        return self.__whiteDraw and self.__blackDraw

## if one of current moves blocks the check
