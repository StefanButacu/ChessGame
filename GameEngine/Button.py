from pygame import Rect

"""
Class for Buttons ( Draw/ Play)
"""
white = (255, 255, 255)
black = (0, 0, 0)
buttonPressedColor = (58, 125, 68)


class Button:
    """
    Creates a button that changes his background color when is clicked
    """

    def __init__(self, screen, position, font, text):
        self.screen = screen

        self.width, self.height = 80, 40
        self.buttonColor = white
        self.textColor = black
        self.font = font

        self.rect = Rect(0, 0, self.width, self.height)
        self.rect.center = position
        self.text = text
        self.prepText()

    def prepText(self):
        self.textImage = self.font.render(self.text, True, self.textColor, self.buttonColor)
        self.textImageRect = self.textImage.get_rect()
        self.textImageRect.center = self.rect.center

    def showButton(self):
        self.screen.fill(self.buttonColor, self.rect)
        self.screen.blit(self.textImage, self.textImageRect)

    def changeBackground(self):
        self.buttonColor = buttonPressedColor
        self.prepText()
        self.showButton()
