# bot.py
from utils.logger import Logger
from managers.game_manager import GameManager
from managers.location_manager import LocationManager
from managers.task_manager import TaskManager
from managers.ocr_manager import OcrManager

class Bot:
    def __init__(self):
        """Inicjalizuje wszystkie managery w odpowiedniej kolejności."""
        self.logger = Logger()
        self.location_manager = LocationManager(self)
        self.game_manager = GameManager(self)
        self.ocr_manager = OcrManager(self)
        self.task_manager = TaskManager(self)
        
        self.logger.warning("Bot został zainicjowany. Wszystkie managery gotowe.")

    def run(self):
        """Uruchamia główną pętlę bota."""
        self.logger.warning("Uruchamianie pętli TaskManagera...")
        try:
            self.task_manager.start()
        except KeyboardInterrupt:
            self.logger.warning("Wykryto polecenie zatrzymania (Ctrl+C). Zamykanie...")
            self.task_manager.stop()
        except Exception as e:
            self.logger.error(f"Wystąpił nieoczekiwany błąd na głównym poziomie: {e}")
            self.task_manager.stop()

if __name__ == '__main__':
    bot = Bot()
    bot.run()