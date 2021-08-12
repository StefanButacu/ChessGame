import pygame

from GameEngine.movements import Move

darkColor = (184, 139, 74)
lightColor = (227, 193, 111)
activeColor = (225, 120, 98)
futureColor = (234, 161, 145)


class Game:
    def __init__(self):
        self.width = 800
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
        self.__whiteLostPieces = []
        self.__blackLostPieces = []



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

    def run(self):
        self.drowGrid()
        sqList = []
        nextMoves = []
        while True:
            for event in pygame.event.get():
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
                    sqSelected = (row, col)
                    if len(sqList) == 0:
                        # highlight current square
                        if self.__board[row][col][0] == self.__currentPlayer and self.__board[row][col] != '--':
                            self.highlightSquare(row, col)
                            sqList.append(sqSelected)
                            nextMoves = self.possibleMoves(row, col)
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
                            if self.__board[sqList[1][0]][sqList[1][1]] != '--': # we land on a piece
                                if self.__currentPlayer == 'b':                   # magic numbers = BAD
                                    self.__whiteLostPieces.append(self.__board[sqList[1][0]][sqList[1][1]])
                                else:
                                    self.__blackLostPieces.append(self.__board[sqList[1][0]][sqList[1][1]])
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
            pygame.display.update()

    def possibleMoves(self, row, col):
        currentPiece = self.__board[row][col]
        move = Move(currentPiece, row, col,self.__getWhiteKing(), self.__getBlackKing(), self.__board)
        allMoves = move.getAllMoves()
        # from these moves i have to exclude the ones that puts currentPlay's king in check
        # executing a move -> board[allMoves[i][0][allMoves[i][1] = currentPiece
        #                     board[row][col] = --
        return allMoves

    def __getWhiteKing(self):
        for i in range(8):
            for j in range(8):
                if self.__board[i][j] == "wK":
                    return (i,j)
        raise Exception()

    def __getBlackKing(self):
        for i in range(8):
            for j in range(8):
                if self.__board[i][j] == "bK":
                    return (i, j)
        raise Exception()

