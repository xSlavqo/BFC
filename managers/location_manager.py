# managers/location_manager.py
# import pyautogui # Usunięto, bo akcje klawiatury będą zdalne
import time
from utils.locate import locate
from utils.mouse_actions import click as mouse_click

class LocationManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.remote_client = bot.remote_client # Dostęp do klienta zdalnego sterowania
        self.build_menu_path = r"png/city/build_menu.png"
        self.find_menu_path = r"png/map/find_menu.png"

    def _click_bottom_right_corner(self):
        """
        Klikanie w prawy dolny róg w celu zmiany widoku.
        Pobiera rozmiar ekranu zdalnie i używa zdalnego kliknięcia.
        """
        # Możesz dodać komendę do remote_client, która zwraca rozmiar ekranu laptopa
        # Na razie zakładamy, że pełny zrzut ekranu zwróci rozmiar.
        # Lepszym rozwiązaniem byłoby dodanie komendy 'get_screen_size' do serwera.
        # Na potrzeby tego przykładu, pobierzemy pełny zrzut ekranu, aby uzyskać jego rozmiar.
        full_screenshot = self.remote_client.grab_screenshot_remote()
        if full_screenshot:
            screen_width, screen_height = full_screenshot.size
        else:
            self.logger.error("Nie udało się pobrać rozmiaru ekranu z laptopa. Używam domyślnych wartości.")
            screen_width, screen_height = 1920, 1080 # Domyślne wartości, jeśli nie uda się pobrać

        target_x = screen_width - 25
        target_y = screen_height - 25
        self.logger.warning(f"Klikanie w prawy dolny róg ({target_x}, {target_y}) na laptopie w celu zmiany widoku.")
        # Używamy zdalnej funkcji click, przekazując instancję bota
        mouse_click(self.bot, target_x, target_y)
        time.sleep(3)

    def is_in_city(self):
        """Sprawdza, czy jesteśmy w widoku miasta, używając zdalnego locate."""
        if locate(self.bot, self.build_menu_path, threshold=0.999, perform_click=False):
            return True
        return False

    def is_on_map(self):
        """Sprawdza, czy jesteśmy w widoku mapy, używając zdalnego locate."""
        if locate(self.bot, self.find_menu_path, threshold=0.999, perform_click=False):
            return True
        return False

    def get_current_location(self):
        """
        Określa bieżącą lokalizację.
        Używa zdalnego locate i zdalnego naciśnięcia klawisza.
        """
        if self.is_in_city():
            return "city"
        if self.is_on_map():
            return "map"

        self.logger.warning("Nie znaleziono żadnego punktu odniesienia. Próba powrotu przez 'ESC' na laptopie.")
        # Używamy remote_client do naciśnięcia klawisza ESC na laptopie
        self.remote_client.press_remote('esc')
        time.sleep(2)

        if self.is_in_city():
            return "city"
        if self.is_on_map():
            return "map"
            
        self.logger.error("Nie udało się określić lokalizacji po ponownej próbie.")
        return None

    def navigate_to_city(self):
        """
        Nawigacja do widoku miasta.
        Używa zdalnego locate, zdalnego kliknięcia i zdalnego naciśnięcia klawisza.
        """
        self.logger.warning("Nawigacja do miasta na laptopie...")
        for _ in range(3):
            if self.is_in_city():
                self.logger.warning("Jestem już w mieście.")
                return True
            
            if self.is_on_map():
                self.logger.warning("Jestem na mapie, próba powrotu do miasta...")
                self._click_bottom_right_corner() # Ta funkcja już używa zdalnego kliknięcia
                if self.is_in_city():
                    self.logger.warning("Pomyślnie nawigowano do miasta.")
                    return True
            
            self.logger.warning("Nieznany stan, próba powrotu przez 'ESC' na laptopie.")
            # Używamy remote_client do naciśnięcia klawisza ESC na laptopie
            self.remote_client.press_remote('esc')
            time.sleep(2)

        self.logger.error("Nie udało się nawigować do miasta.")
        return False

    def navigate_to_map(self):
        """
        Nawigacja do widoku mapy.
        Używa zdalnego locate, zdalnego kliknięcia i zdalnego naciśnięcia klawisza.
        """
        self.logger.warning("Nawigacja do mapy na laptopie...")
        for _ in range(3):
            if self.is_on_map():
                self.logger.warning("Jestem już na mapie.")
                return True

            if self.is_in_city():
                self.logger.warning("Jestem w mieście, próba przejścia do mapy...")
                self._click_bottom_right_corner() # Ta funkcja już używa zdalnego kliknięcia
                if self.is_on_map():
                    self.logger.warning("Pomyślnie nawigowano do mapy.")
                    return True
            
            self.logger.warning("Nieznany stan, próba powrotu przez 'ESC' na laptopie.")
            # Używamy remote_client do naciśnięcia klawisza ESC na laptopie
            self.remote_client.press_remote('esc')
            time.sleep(2)
            
        self.logger.error("Nie udało się nawigować do mapy.")
        return False

    def navigate_to_main_screen(self):
        """Nawiguje do głównego ekranu (miasta)."""
        return self.navigate_to_city()
