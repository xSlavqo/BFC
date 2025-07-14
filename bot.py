# bot.py
from utils.logger import Logger
from managers.game_manager import GameManager
from managers.location_manager import LocationManager
from managers.task_manager import TaskManager
from managers.ocr_manager import OcrManager
from utils.remote_control import RemoteClient
from utils.screenshot_grabber import ScreenshotGrabber
from PIL import Image # Potrzebne do obsługi obrazów przez Pillow

class Bot:
    def __init__(self, laptop_ip, port): 
        self.logger = Logger()
        
        # Inicjalizacja klienta zdalnego sterowania
        self.remote_client = RemoteClient(laptop_ip=laptop_ip, port=port)
        self.remote_client.set_logger(self.logger)
        
        # Inicjalizacja ScreenshotGrabber, który używa remote_client
        self.screenshot_grabber = ScreenshotGrabber(self)

        # Inicjalizacja wszystkich managerów, przekazując instancję bota
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
    # Użyj rzeczywistego IP laptopa i portu
    # UPEWNIJ SIĘ, ŻE TO JEST PRAWIDŁOWY ADRES IP TWOJEGO LAPTOPA
    LAPTOP_IP_ADDRESS = '192.168.1.11' 
    SERVER_PORT = 65432

    bot = Bot(laptop_ip=LAPTOP_IP_ADDRESS, port=SERVER_PORT) 
    bot.run()
