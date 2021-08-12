import pygame


# Press the green button in the gutter to run the script.
from GameEngine.gameEngine import Game

if __name__ == '__main__':
    pygame.init()
    pygame.display.init()
    myGame = Game()
    myGame.run()
