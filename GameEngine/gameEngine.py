import pygame

from GameEngine.movements import Move

darkColor = (184, 139, 74)
lightColor = (227, 193, 111)
activeColor = (225, 120, 98)
futureColor = (234, 161, 145)
white = (255, 255, 255)


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
            ["bp", "wp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "bp", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "wp", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "--", "--", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.__currentPlayer = 'w'
        self.__blackCheck = False
        self.__whiteCheck = False
        self.__stalemate = False

    def drowGrid(self):

        for x in range(8):
            for y in range(8):
                rect = pygame.Rect(x * 100, y * 100, 100, 100)
                if (x + y) % 2 == 0:
                    pygame.draw.rect(self.screen, lightColor, rect)
                else:
                    pygame.draw.rect(self.screen, darkColor, rect)
        self.placePieces()

    def placePieces(self):
        for x in range(8):
            for y in range(8):
                if self.__board[x][y] != "--":
                    image = pygame.image.load("./images/" + self.__board[x][y] + ".png").convert_alpha()
                    rect = image.get_rect()
                    rect.center = ((2 * y + 1) * 50, (2 * x + 1) * 50)
                    self.screen.blit(image, rect)

    def getColorFromIndex(self, row, col):
        return lightColor if (row + col) % 2 == 0 else darkColor

    def unHighlightSquare(self, row, col):
        pygame.draw.rect(self.screen, self.getColorFromIndex(row, col), pygame.Rect(col * 100, row * 100, 100, 100))

    def highlightSquare(self, row, col):
        pygame.draw.rect(self.screen, activeColor, pygame.Rect(col * 100, row * 100, 100, 100), 5, 5, 5, 5)

    def getStrTimeFromSecond(self, seconds):
        mins = seconds // 60
        seconds %= 60
        if seconds == 0:
            return "{}:00".format(mins)
        return "{}:{}".format(mins, seconds)

    def run(self):
        sqList = []
        nextMoves = []

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
                        print(end='\n')

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
                            nextMoves = self.possibleMovesByPiece(row,
                                                                  col)  ### you cant move the king in a square attacked by a piece
                            if self.__board[row][col][1] == "K":
                                # remove from nextMoves squares that are attacked by opponent's pieces
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
                            if self.__whiteCheck == True:
                                if self.__hasLegalMoves():
                                    self.__whiteCheckCheck = False

                        else:
                            if self.__blackCheck == True:
                                if self.__hasLegalMoves():
                                    self.__blackCheck = False


                        # do the move
                        if sqSelected in nextMoves:
                            # the the move if is not in check
                            self.__board[sqList[1][0]][sqList[1][1]] = self.__board[sqList[0][0]][
                                sqList[0][1]]  # "magical number" should had encapsulated this
                            self.__board[sqList[0][0]][sqList[0][1]] = "--"
                            # check for pawn promotion
                            if self.__checkPawnPromotion(sqList[1][0],sqList[1][1]):
                                self.__board[sqList[1][0]][sqList[1][1]] = "--"
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
                                            if not (col <= col2 < col + 1 and row <= row2 < row +1 ) :
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
                                    print("white check") # ??
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
                        self.placePieces()
                        sqList.clear()
            self.screen.blit(font.render(textPlayerOne, True, white, (0, 0, 0)), (950, 650))
            self.screen.blit(font.render(textPlayerTwo, True, white, (0, 0, 0)), (950, 250))
           # pygame.display.flip()
            if self.__currentPlayer == 'w':
                clockPlayerOne.tick(60)
            else:
                clockPlayerTwo.tick(60)
            if self.__isStalemate():
                gameOver = True
                print(self.__currentPlayer, " lost by stalemate ")
                # return
            elif self.__isCheckmate():
                print(self.__currentPlayer, " lost by checkmate ")
                # return
            # check Stalemate. When a player whose turn it is has no legal moves by any of his/her pieces, but is not in check.
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

    def __squareUnderAttack(self, square, enemyPiece):
        """

        :param square: (int, int) the coordonates of the square ( row, column)
        :param enemyPiece: b/w
        :return: True if the square is attacked by any enemy piece
                False otherwise
        """
        row, col = square

        # check by pawm

        if enemyPiece == "w":
            directions = [(-1,-1), (-1, 1)]
        else:
            directions = [(1,1), (1, -1)]
        for i, j in directions:
            newRow = row + i
            newCol = col + j
            if 0 <= newRow < 8 and 0 <= newCol < 8:
                if self.__board[newRow][newCol][0] == enemyPiece and self.__board[newRow][newCol][1] == "p":
                    # enemy piece                                               # is a pawn
                    return True
        # check by knight
        directions = [(1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1)]
        for i, j in directions:
            newRow = row + i
            newCol = col + j
            if 0 <= newRow < 8 and 0 <= newCol < 8:
                if self.__board[newRow][newCol][0] == enemyPiece and self.__board[newRow][newCol][1] == "N":
                    # enemy piece                                               # is a knight
                    return True

        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for i, j in directions:
            for k in range(1, 8):
                newRow = row + i * k
                newCol = col + j * k
                if 0 <= newRow < 8 and 0 <= newCol < 8:
                    if self.__board[newRow][newCol][0] == enemyPiece:
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
                    if self.__board[newRow][newCol][0] == enemyPiece:
                        if self.__board[newRow][newCol][1] == "Q" or self.__board[newRow][newCol][1] == "B":
                            return True
                        if k == 1 and self.__board[newRow][newCol][1] == "p":  # can be attacked by pawn depeding on color
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
                if self.__board[newRow][newCol][0] == enemyPiece:
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
            elif self.__currentPlayer =="b" and row == 7:
                return True
        return False


## if one of current moves blocks the check
