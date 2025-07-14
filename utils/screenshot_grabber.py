# utils/screenshot_grabber.py
from PIL import Image # Potrzebne do zwracania obiektu Image

class ScreenshotGrabber:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.logger = bot_instance.logger
        self.remote_client = bot_instance.remote_client

    def get_screenshot(self, bbox=None):
        """
        Pobiera zrzut ekranu ze zdalnego laptopa za pośrednictwem remote_client.
        Zwraca obiekt PIL.Image.
        """
        self.logger.warning(f"Pobieram zrzut ekranu z laptopa (bbox: {bbox}).")
        screenshot = self.remote_client.grab_screenshot_remote(bbox=bbox)
        if screenshot:
            self.logger.warning("Zrzut ekranu pomyślnie pobrany.")
            return screenshot
        else:
            self.logger.error("Nie udało się pobrać zrzutu ekranu z laptopa.")
            return None