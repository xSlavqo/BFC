import random
import time
from shared.logger import Logger
from client.managers.game_manager import GameManager
from client.managers.location_manager import LocationManager
from client.managers.task_manager import TaskManager
from client.managers.ocr_manager import OcrManager
from shared.remote_control import RemoteClient
from client.utils.screenshot_grabber import ScreenshotGrabber
from client.processing.png_locator import PngLocator
from client.processing.ocr_locator import OcrLocator

class Bot:
    def __init__(self, laptop_ip, port):
        self.logger = Logger()

        try:
            self.remote_client = RemoteClient(laptop_ip=laptop_ip, port=port)
            self.remote_client.set_logger(self.logger)

            self.screenshot_grabber = ScreenshotGrabber(self)
            self.png_locator = PngLocator(self)
            self.ocr_locator = OcrLocator()

            self.location_manager = LocationManager(self)
            self.game_manager = GameManager(self)
            self.ocr_manager = OcrManager(self)
            self.task_manager = TaskManager(self)

        except Exception as e:
            self.logger.error(f"Błąd podczas inicjalizacji bota: {e}")
            raise

    def click(self, target_x, target_y):
        """
        Centralna metoda do wykonywania kliknięć.
        """
        try:
            PIXEL_OFFSET = 5
            MOVE_DURATION_RANGE = (0.2, 0.6)

            offset_x = random.randint(-PIXEL_OFFSET, PIXEL_OFFSET)
            offset_y = random.randint(-PIXEL_OFFSET, PIXEL_OFFSET)
            final_x = target_x + offset_x
            final_y = target_y + offset_y

            move_duration = random.uniform(*MOVE_DURATION_RANGE)

            self.remote_client.move_to_remote(final_x, final_y, duration=move_duration)
            self.remote_client.click_remote(final_x, final_y)

        except Exception as e:
            self.logger.error(f"Błąd podczas kliknięcia w ({target_x}, {target_y}): {e}")

    def run(self):
        """Uruchamia główną pętlę bota."""
        try:
            self.task_manager.start()
        except KeyboardInterrupt:
            self.task_manager.stop()
        except Exception as e:
            self.logger.error(f"Wystąpił nieoczekiwany błąd na głównym poziomie: {e}")
            self.task_manager.stop()

if __name__ == '__main__':
    LAPTOP_IP_ADDRESS = '192.168.1.11'
    SERVER_PORT = 65432

    try:
        bot = Bot(laptop_ip=LAPTOP_IP_ADDRESS, port=SERVER_PORT)
        bot.run()
    except Exception as e:
        Logger().error(f"Błąd krytyczny przy uruchamianiu bota: {e}")
