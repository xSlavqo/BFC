# bot.py
from utils.game_window import GameWindow
from utils.logger import Logger

class Bot:
    def __init__(self):
        self.logger = Logger()
        self.game_window = GameWindow()
