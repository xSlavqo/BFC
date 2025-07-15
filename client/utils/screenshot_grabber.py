# client/utils/screenshot_grabber.py
import io
from PIL import Image

class ScreenshotGrabber:
    def __init__(self, remote_control_instance):
        self.remote_control = remote_control_instance

    def get_screenshot(self, bbox=None):
        """Pobiera zrzut ekranu z serwera."""
        try:
            # Zakładamy, że remote_control ma metodę get_screenshot
            data = self.remote_control.get_screenshot(bbox)
            if data:
                return Image.open(io.BytesIO(data))
        except Exception as e:
            # W przyszłości można dodać logowanie
            print(f"Błąd podczas pobierania zrzutu ekranu: {e}")
            return None
