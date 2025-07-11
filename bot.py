# bot.py
from utils.logger import Logger
from managers.game_manager import GameManager
from managers.location_manager import LocationManager

class Bot:
    def __init__(self):
        self.logger = Logger()
        self.location_manager = LocationManager(self)
        self.game_manager = GameManager(self)

if __name__ == '__main__':
    bot = Bot()
    bot.logger.warning("Inicjalizacja bota zakończona.")