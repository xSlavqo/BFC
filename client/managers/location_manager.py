import time

class LocationManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.remote_client = bot.remote_client
        self.png_locator = bot.png_locator
        
        self.build_menu_path = r"png/city/build_menu.png"
        self.find_menu_path = r"png/map/find_menu.png"

    def _switch_view(self):
        """Przełącza widok (miasto/mapa) za pomocą klawisza spacji."""
        self.remote_client.press_remote('space')
        time.sleep(4)

    def is_in_city(self):
        """Sprawdza, czy jesteśmy w widoku miasta."""
        return self.png_locator.find(self.build_menu_path, threshold=0.9, perform_click=False) is not None

    def is_on_map(self):
        """Sprawdza, czy jesteśmy w widoku mapy."""
        return self.png_locator.find(self.find_menu_path, threshold=0.9, perform_click=False) is not None

    def navigate_to_city(self):
        """Nawigacja do widoku miasta."""
        for _ in range(3):
            if self.is_in_city():
                return True
            if self.is_on_map():
                self._switch_view()
                if self.is_in_city():
                    return True
            
            self.remote_client.press_remote('esc')
            time.sleep(2)
        
        self.logger.error("Nie udało się nawigować do miasta.")
        return False

    def navigate_to_map(self):
        """Nawigacja do widoku mapy."""
        for _ in range(3):
            if self.is_on_map():
                return True
            if self.is_in_city():
                self._switch_view()
                if self.is_on_map():
                    return True

            self.remote_client.press_remote('esc')
            time.sleep(2)

        self.logger.error("Nie udało się nawigować do mapy.")
        return False
