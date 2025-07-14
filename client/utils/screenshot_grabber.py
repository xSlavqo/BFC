from PIL import Image

class ScreenshotGrabber:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.logger = bot_instance.logger
        self.remote_client = bot_instance.remote_client

    def get_screenshot(self, bbox=None):
        """Pobiera zrzut ekranu ze zdalnego laptopa."""
        try:
            screenshot = self.remote_client.grab_screenshot_remote(bbox=bbox)
            if screenshot:
                return screenshot
            else:
                self.logger.error("Nie udało się pobrać zrzutu ekranu z laptopa.")
                return None
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania zrzutu ekranu: {e}")
            return None
