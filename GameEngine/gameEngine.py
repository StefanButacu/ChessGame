import pygame

from GameEngine.movements import Move

darkColor = (184, 139, 74)
lightColor = (227, 193, 111)
activeColor = (144, 170, 134)
futureColor = (234, 161, 145)
white = (255, 255, 255)
textColor = (188, 57, 8)


class Game:
    def __init__(self):
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill((0, 0, 0))
        pygame.display.set_caption(("Chess"))
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
        :param row: int assume  0 <= row < 7
        :param col: int  assume 0 <= col < 7
        :return:
        """
        pygame.draw.rect(self.screen, self.getColorFromIndex(row, col), pygame.Rect(col * 100, row * 100, 100, 100))

    def highlightSquare(self, row, col):
        # color the margin of square
        # pygame.draw.rect(self.screen, activeColor, pygame.Rect(col * 100, row * 100, 100, 100), 5, 5, 5, 5)

        # Fill the background
        s = pygame.Surface((100, 100))
        s.set_alpha(125)  # transperancy
        s.fill(activeColor)
        self.screen.blit(s, (col * 100, row * 100))

    def getStrTimeFromSecond(self, seconds):
        mins = seconds // 60
        seconds %= 60
        return "{}:{}".format(mins, seconds)

    def run(self):
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
        timePlayerOne, textPlayerOne = 600, self.getStrTimeFromSecond(600)
        #   font = pygame.font.SysFont('Consolas', 30)

        clockPlayerTwo = pygame.time.Clock()
        timePlayerTwo, textPlayerTwo = 600, self.getStrTimeFromSecond(600)

        pygame.time.set_timer(pygame.USEREVENT, 1000)
        while True:
            self.screen.blit(playerOneText, playerOneRect)
            self.screen.blit(playerTwoText, playerTwoRect)
            if self.__isStalemate():
                gameOver = True
                self.__printScreenMessage(" Draw by stalemate ")
            # break
            elif self.__isCheckmate():
                message = "Black" if self.__currentPlayer == "b" else "White"
                self.__printScreenMessage(message + " lost by checkmate ")
                # break

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT:
                    if self.__currentPlayer == 'w':
                        timePlayerOne -= 1
                        textPlayerOne = self.getStrTimeFromSecond(timePlayerOne) if timePlayerOne > 0 else "GAME OVER"
                    else:
                        timePlayerTwo -= 1
                        textPlayerTwo = self.getStrTimeFromSecond(timePlayerTwo) if timePlayerTwo > 0 else "GAME OVER"
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        for row in self.__board:
                            print(row)
                        print()
                        print(self.__rookOrKingMoved)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // 100
                    row = pos[1] // 100
                    if col >= 8 or row >= 8:
                        continue
                    sqSelected = (row, col)
                    if len(sqList) == 0:
                        # highlight current square
                        if self.__board[row][col][0] == self.__currentPlayer and self.__board[row][col] != '--':
                            self.highlightSquare(row, col)
                            sqList.append(sqSelected)
                            nextMoves = self.possibleMovesByPiece(row, col)
                            # if is rook or king add the "Castle Moves"
                            castleMoves.clear()
                            if self.__board[row][col][1] == "K" or self.__board[row][col][1] == "R":
                                kingLocation = self.__getWhiteKing() if self.__currentPlayer == "w" else self.__getBlackKing()
                                if self.__castleValid(kingLocation, "left"):
                                    print("you can castle left")
                                    castleMoves += self.__getCastleMoves("left")
                                    if self.__currentPlayer == "w":
                                        self.highlightSquare(7, 0)   # highlight left white Rook
                                        self.highlightSquare(self.__getWhiteKing()[0], self.__getWhiteKing()[1]) # highlight white King
                                        castleSquare = (7,0) if self.__board[row][col][1] == "K" else kingLocation
                                    else:
                                        self.highlightSquare(0, 0) # highlight left black Rook
                                        self.highlightSquare(self.__getBlackKing()[0], self.__getBlackKing()[1]) # highlight black king
                                        castleSquare = (0,0) if self.__board[row][col][1] == "K" else kingLocation

                                if self.__castleValid(kingLocation, "right"):
                                    castleMoves += self.__getCastleMoves("right")
                                    if self.__currentPlayer == "w":
                                        self.highlightSquare(7, 7)# highlight right white Rook
                                        self.highlightSquare(self.__getWhiteKing()[0], self.__getWhiteKing()[1])# highlight white King
                                        castleSquare = (7,7) if self.__board[row][col][1] == "K" else kingLocation

                                    else:
                                        self.highlightSquare(0, 7)# highlight right black Rook
                                        self.highlightSquare(self.__getBlackKing()[0], self.__getBlackKing()[1]) # highlight black king
                                        castleSquare = (0,7) if self.__board[row][col][1] == "K" else kingLocation

                            if self.__board[row][col][1] == "K":
                                # remove from nextMoves squares that are attacked by opponent's pieces
                                ### you cant move the king in a square attacked by a piece
                                enemyPiece = "b" if self.__currentPlayer == "w" else "w"
                                for i in range(len(nextMoves) - 1, -1, -1):
                                    if self.__squareUnderAttack((nextMoves[i]), enemyPiece):
                                        del nextMoves[i]

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
                        # Castling moves
                        print("casstleMoves = ", castleMoves)
                        # unhighlight the moves
                        for row,col in castleMoves:
                            self.unHighlightSquare(row,col)
                        for row, col in sqList:
                            self.unHighlightSquare(row, col)
                        if sqSelected == castleSquare and self.__board[castleSquare[0]][castleSquare[1]] != "--": # we need to click the king if first is rook, or vice-versa
                            newKingRow, newKingCol = castleMoves[0]
                            newRookRow, newRookCol = castleMoves[1]
                            lastRookRow, lastRookCol = castleMoves[2]
                            lastKingRow, lastKingCol = castleMoves[3]
                            self.__rookOrKingMoved[self.__currentPlayer]["K"] = True
                            if newRookCol < 4:
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
                            print(self.__board[lastRookRow][lastRookCol], lastRookRow, " ", lastRookCol)

                            # BUGS
                            self.__currentPlayer = 'b' if self.__currentPlayer == 'w' else 'w'
                            print("after Castling: ",self.__rookOrKingMoved)
                            castleMoves.clear()
                            self.placePieces()
                            sqList.clear()
                        # do the move
                        elif sqSelected in nextMoves:
                            lastRow, lastCol = sqList[0][0], sqList[0][1]
                            newRow, newCol = sqList[1][0], sqList[1][1]
                            # the the move if is not in check
                            self.__board[newRow][newCol] = self.__board[lastRow][
                                lastCol]  # "magical number" should had encapsulated this
                            self.__board[lastRow][lastCol] = "--"
                            # check if he moved the king/rook => you can no longer do the castle
                            if self.__board[newRow][newCol][1] == "K":
                                self.__rookOrKingMoved[self.__currentPlayer]["K"] = True
                            if self.__board[newRow][newRow][1] == "R":
                                if lastCol < 4:
                                    self.__rookOrKingMoved[self.__currentPlayer]["lR"] = True
                                else:
                                    self.__rookOrKingMoved[self.__currentPlayer]["rR"] = True

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
                                                    self.__board[row][col] = pieces[0]
                                                elif pos[0] % 100 <= 50 and pos[1] % 100 >= 50:
                                                    self.__board[row][col] = pieces[1]
                                                elif pos[0] % 100 >= 50 and pos[1] % 100 <= 50:
                                                    self.__board[row][col] = pieces[2]
                                                elif pos[0] % 100 >= 50 and pos[1] % 100 >= 50:
                                                    self.__board[row][col] = pieces[3]
                                ######### ### might repaint all
                            if self.__currentPlayer == 'b':
                                if self.__squareUnderAttack(self.__getWhiteKing(), "b"):
                                    self.__whiteCheck = True
                                    print("white check")
                            else:
                                if self.__squareUnderAttack(self.__getBlackKing(), "w"):
                                    self.__blackCheck = True
                                    print("black check")
                            self.__currentPlayer = 'b' if self.__currentPlayer == 'w' else 'w'

                        # un-highlight selected squares
                        for row, col in sqList:
                            self.unHighlightSquare(row, col)
                        for (newRow, newCol) in nextMoves:
                            self.unHighlightSquare(newRow, newCol)
                        # un-highlight selected squares
                        sqList.clear()
            self.placePieces()

            self.screen.blit(font.render(textPlayerOne, True, white, (0, 0, 0)), (950, 650))
            self.screen.blit(font.render(textPlayerTwo, True, white, (0, 0, 0)), (950, 250))
            if self.__currentPlayer == 'w':
                clockPlayerOne.tick(60)
            else:
                clockPlayerTwo.tick(60)
            # check both Draw buttons are pressed
            # check if is checkmate ( cant exit check)
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
        move = Move(currentPiece, row, col, self.__getWhiteKing(), self.__getBlackKing(), self.__board)
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
        row, col = square

        # check by pawm
        allyPiece = "b" if enemyColor == "w" else "w"
        if enemyColor == "w":
            directions = [(-1, -1), (-1, 1)]
        else:
            directions = [(1, 1), (1, -1)]
        for i, j in directions:
            newRow = row + i
            newCol = col + j
            if 0 <= newRow < 8 and 0 <= newCol < 8:
                if self.__board[newRow][newCol][0] == enemyColor and self.__board[newRow][newCol][1] == "p":
                    # enemy piece                                               # is a pawn
                    return True
        # check by knight
        directions = [(1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1)]
        for i, j in directions:
            newRow = row + i
            newCol = col + j
            if 0 <= newRow < 8 and 0 <= newCol < 8:
                if self.__board[newRow][newCol][0] == enemyColor and self.__board[newRow][newCol][1] == "N":
                    # enemy piece                                               # is a knight
                    return True

        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for i, j in directions:
            for k in range(1, 8):
                newRow = row + i * k
                newCol = col + j * k
                if 0 <= newRow < 8 and 0 <= newCol < 8:
                    if self.__board[newRow][newCol][0] != allyPiece:
                        if self.__board[newRow][newCol][1] == "Q" or self.__board[newRow][newCol][1] == "R":
                            return True
                    else:  # this path is blocked by an ally piece
                        break
                else:  # exits the board
                    break
        # bishop
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for i, j in directions:
            for k in range(1, 8):
                newRow = row + i * k
                newCol = col + j * k
                if 0 <= newRow < 8 and 0 <= newCol < 8:
                    if self.__board[newRow][newCol][0] != allyPiece:
                        if self.__board[newRow][newCol][1] == "Q" or self.__board[newRow][newCol][1] == "B":
                            return True
                        if k == 1 and self.__board[newRow][newCol][
                            1] == "p":  # can be attacked by pawn depeding on color
                            return True
                    else:  # this path is blocked by an ally piece
                        break
                else:  # exits the board
                    break
        # by king
        direction = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1),
                     (0, -1)]
        for (i, j) in direction:
            newRow = row + i
            newCol = col + j
            if 0 <= newRow < 8 and 0 <= newCol < 8:
                if self.__board[newRow][newCol][0] == enemyColor:
                    if self.__board[newRow][newCol][1] == "K":
                        return True
        return False

    def __computeAttackerSquares(self):
        """

        :return: a list of all attacked squares by the enemy player
        """
        attackerMoves = []
        for i in range(8):
            for j in range(8):
                if self.__board[i][j] != "--" and self.__board[i][j][0] != self.__currentPlayer:
                    attackerMoves += Move(self.__board[i][j], i, j, self.__getWhiteKing(), self.__getBlackKing(),
                                          self.__board).getAllMoves()
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
        rect.center = (550, 600)

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
            if self.__rookOrKingMoved[self.__currentPlayer]["K"] or self.__rookOrKingMoved[self.__currentPlayer]["lR"]:  # if the King or the Rook has already been moved in the game
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

## if one of current moves blocks the check
