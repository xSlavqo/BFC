# managers/location_manager.py
import pyautogui
import time
from utils.locate import locate
from utils.mouse_actions import click as mouse_click

class LocationManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.build_menu_path = r"png/city/build_menu.png"
        self.find_menu_path = r"png/map/find_menu.png"

    def _click_bottom_right_corner(self):
        screen_width, screen_height = pyautogui.size()
        target_x = screen_width - 25
        target_y = screen_height - 25
        self.logger.warning(f"Klikanie w prawy dolny róg ({target_x}, {target_y}) w celu zmiany widoku.")
        mouse_click(target_x, target_y)
        time.sleep(3)

    def is_in_city(self):
        if locate(self.bot, self.build_menu_path, threshold=0.999, perform_click=False):
            return True
        return False

    def is_on_map(self):
        if locate(self.bot, self.find_menu_path, threshold=0.999, perform_click=False):
            return True
        return False

    def get_current_location(self):
        if self.is_in_city():
            return "city"
        if self.is_on_map():
            return "map"

        self.logger.warning("Nie znaleziono żadnego punktu odniesienia. Próba powrotu przez 'ESC'.")
        pyautogui.press('esc')
        time.sleep(2)

        if self.is_in_city():
            return "city"
        if self.is_on_map():
            return "map"
            
        self.logger.error("Nie udało się określić lokalizacji po ponownej próbie.")
        return None

    def navigate_to_city(self):
        self.logger.warning("Nawigacja do miasta...")
        for _ in range(3):
            if self.is_in_city():
                self.logger.warning("Jestem już w mieście.")
                return True
            
            if self.is_on_map():
                self.logger.warning("Jestem na mapie, próba powrotu do miasta...")
                self._click_bottom_right_corner()
                if self.is_in_city():
                    self.logger.warning("Pomyślnie nawigowano do miasta.")
                    return True
            
            self.logger.warning("Nieznany stan, próba powrotu przez 'ESC'.")
            pyautogui.press('esc')
            time.sleep(2)

        self.logger.error("Nie udało się nawigować do miasta.")
        return False

    def navigate_to_map(self):
        self.logger.warning("Nawigacja do mapy...")
        for _ in range(3):
            if self.is_on_map():
                self.logger.warning("Jestem już na mapie.")
                return True

            if self.is_in_city():
                self.logger.warning("Jestem w mieście, próba przejścia do mapy...")
                self._click_bottom_right_corner()
                if self.is_on_map():
                    self.logger.warning("Pomyślnie nawigowano do mapy.")
                    return True
            
            self.logger.warning("Nieznany stan, próba powrotu przez 'ESC'.")
            pyautogui.press('esc')
            time.sleep(2)
            
        self.logger.error("Nie udało się nawigować do mapy.")
        return False

    def navigate_to_main_screen(self):
        return self.navigate_to_city()
