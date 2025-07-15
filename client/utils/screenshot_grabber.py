# client/utils/screenshot_grabber.py
import io
from PIL import Image

class ScreenshotGrabber:
    def __init__(self, bot):
        # Pobiera remote_client z instancji bota
        self.remote_client = bot.remote_client

    def get_screenshot(self, bbox=None):
        """Pobiera zrzut ekranu z serwera."""
        try:
            pil_image = self.remote_client.grab_screenshot_remote(bbox=bbox)
            if pil_image:
                return pil_image
        except Exception as e:
            # W przyszłości można dodać logowanie
            print(f"Błąd podczas pobierania zrzutu ekranu: {e}")
            return None