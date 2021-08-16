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
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.__currentPlayer = 'w'

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
        seconds = seconds % 60
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
                            nextMoves = self.possibleMovesByPiece(row, col)
                            for (newRow, newCol) in nextMoves:
                                self.highlightSquare(newRow, newCol)
                        else:
                            sqList.clear()
                            continue
                    elif len(sqList) == 1:
                        # i have 1 square of a piece
                        # if there is a piece and has the same color as the current player
                        sqList.append(sqSelected)
                        if sqSelected in nextMoves:
                            # the the move             # presupun ca a apasat in ordinea care trebuie
                            self.__board[sqList[1][0]][sqList[1][1]] = self.__board[sqList[0][0]][sqList[0][1]]
                            self.__board[sqList[0][0]][sqList[0][1]] = "--"
                            self.__currentPlayer = 'b' if self.__currentPlayer == 'w' else 'w'

                            # a apasat pe altcv care nu e nextMove  -> alta piesa
                            #                                        -> o piesa de acceasi culoare
                            # am apasat altundeva  piesa inamica, piesa mea, alta miscare

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
            pygame.display.flip()
            if self.__currentPlayer == 'w':
                clockPlayerOne.tick(60)
            else:
                clockPlayerTwo.tick(60)
            pygame.display.update()

                                    # allMoves mutable but changes weren't shown
    def leaveKingUnderAttackValidation(self, pieceMoves, currentRow, currentCol, currentPiece):
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
                                pieceMoves = [elems for elems in pieceMoves if elems != (newRow, newCol)] # list comperhensions works better at removing
            else:
                for i in range(8):  # we can format this part
                    for j in range(8):
                        if self.__board[i][j][0] == 'w':
                            attackerMove = Move(self.__board[i][j], i, j, self.__getWhiteKing(), self.__getBlackKing(),
                                                self.__board)
                            if self.__getBlackKing() in attackerMove.getAllMoves():
                                pieceMoves = [elems for elems in pieceMoves if elems != (newRow, newCol)]
            #undo the move
            self.__board[newRow][newCol], self.__board[currentRow][currentCol] = beforePiece, currentPiece
        return pieceMoves

    def possibleMovesByPiece(self, row, col):
        currentPiece = self.__board[row][col]
        move = Move(currentPiece, row, col, self.__getWhiteKing(), self.__getBlackKing(), self.__board)
        pieceMoves = move.getAllMoves()
        # from these moves i have to exclude the ones that puts currentPlay's king in check
        # executing a move -> board[allMoves[i][0][allMoves[i][1] = currentPiece
        #                     board[row][col] = --

        # check if after moving a piece the king is under attack
        pieceMoves = self.leaveKingUnderAttackValidation(pieceMoves, row, col, currentPiece)
        return pieceMoves

    def __getWhiteKing(self):
        for i in range(8):
            for j in range(8):
                if self.__board[i][j] == "wK":
                    return i, j
        raise Exception()

    def __getBlackKing(self):
        for i in range(8):
            for j in range(8):
                if self.__board[i][j] == "bK":
                    return i, j
        raise Exception()
