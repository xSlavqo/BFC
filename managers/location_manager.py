# managers/location_manager.py
import time
# Usunięto import 'locate', bo używamy teraz locator'a z instancji bota

class LocationManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.remote_client = bot.remote_client
        self.build_menu_path = r"png/city/build_menu.png"
        self.find_menu_path = r"png/map/find_menu.png"

    def _switch_view(self):
        """Przełącza widok (miasto/mapa) poprzez naciśnięcie spacji na zdalnym komputerze."""
        self.remote_client.press_remote('space')
        time.sleep(3)

    def is_in_city(self):
        """Sprawdza, czy jesteśmy w widoku miasta."""
        if self.bot.locator.find(self.build_menu_path, threshold=0.999, perform_click=False):
            return True
        return False

    def is_on_map(self):
        """Sprawdza, czy jesteśmy w widoku mapy."""
        if self.bot.locator.find(self.find_menu_path, threshold=0.999, perform_click=False):
            return True
        return False

    def get_current_location(self):
        """Określa bieżącą lokalizację."""
        if self.is_in_city():
            return "city"
        if self.is_on_map():
            return "map"

        self.logger.warning("Nie znaleziono żadnego punktu odniesienia. Próba powrotu przez 'ESC' na laptopie.")
        self.remote_client.press_remote('esc')
        time.sleep(2)

        if self.is_in_city():
            return "city"
        if self.is_on_map():
            return "map"

        self.logger.error("Nie udało się określić lokalizacji po ponownej próbie.")
        return None

    def navigate_to_city(self):
        """Nawigacja do widoku miasta."""
        self.logger.warning("Nawigacja do miasta na laptopie...")
        for _ in range(3):
            if self.is_in_city():
                self.logger.warning("Jestem już w mieście.")
                return True

            if self.is_on_map():
                self.logger.warning("Jestem na mapie, próba powrotu do miasta...")
                self._switch_view()
                if self.is_in_city():
                    self.logger.warning("Pomyślnie nawigowano do miasta.")
                    return True

            self.logger.warning("Nieznany stan, próba powrotu przez 'ESC' na laptopie.")
            self.remote_client.press_remote('esc')
            time.sleep(2)

        self.logger.error("Nie udało się nawigować do miasta.")
        return False

    def navigate_to_map(self):
        """Nawigacja do widoku mapy."""
        self.logger.warning("Nawigacja do mapy na laptopie...")
        for _ in range(3):
            if self.is_on_map():
                self.logger.warning("Jestem już na mapie.")
                return True

            if self.is_in_city():
                self.logger.warning("Jestem w mieście, próba przejścia do mapy...")
                self._switch_view()
                if self.is_on_map():
                    self.logger.warning("Pomyślnie nawigowano do mapy.")
                    return True

            self.logger.warning("Nieznany stan, próba powrotu przez 'ESC' na laptopie.")
            self.remote_client.press_remote('esc')
            time.sleep(2)

        self.logger.error("Nie udało się nawigować do mapy.")
        return False

    def navigate_to_main_screen(self):
        """Nawiguje do głównego ekranu (miasta)."""
        return self.navigate_to_city()