# tasks/build_city_task.py
import time
from tasks.base_task import BaseTask
from utils.mouse_actions import click as mouse_click
# Usunięto import locate, bo używamy self.bot.locator

class BuildCityTask(BaseTask):
    def __init__(self, bot):
        super().__init__(bot)
        self.locator = bot.locator # Dostęp do instancji Locator'a
        self.town_hall_coords = (550, 270)

    def _enter_main_building_menu(self):
        th_x, th_y = self.town_hall_coords
        mouse_click(self.bot, th_x, th_y)
        if not self.locator.find("png/build/enter_upgrade_menu", perform_click=True):
            self.logger.error("Nie znaleziono przycisku wejścia do menu ulepszeń.")
            return False
        return True

    def _find_and_start_task(self):
        max_search_loops = 10
        for i in range(max_search_loops):
            if self.locator.find(r"png/build/upgrade.png", perform_click=True):
                time.sleep(1)

                if i == 0:
                    mouse_click(self.bot, *self.town_hall_coords)
                else:
                    screenshot_size = self.bot.screenshot_grabber.get_screenshot().size
                    center_x = screenshot_size[0] / 2
                    center_y = screenshot_size[1] / 2
                    mouse_click(self.bot, center_x, center_y)

                self.location_manager.navigate_to_map()
                return True
            
            # Użycie locator.find z regionem
            if not self.locator.find(r"png/build/go_button", perform_click=True):
                self.logger.error("Nie znaleziono przycisku 'Go', aby przejść do następnego budynku.")
                return False

            if self.locator.find(r"png/build/enter_upgrade_menu", perform_click=True):
                continue
            elif self.locator.find(r"png/build/is_new_building", perform_click=False):
                mouse_click(self.bot, 210, 570)
                if self.locator.find(r"png/build/start_new_building", perform_click=True):
                    self.location_manager.navigate_to_map()
                    return True
                else:
                    self.logger.error("Znaleziono ikonę nowego budynku, ale nie przycisk startu budowy.")
                    return False
            else:
                self.logger.error("Po kliknięciu 'Go' nie znaleziono ani menu ulepszeń, ani nowego budynku.")
                return False

        self.logger.error(f"Przeszukano {max_search_loops} budynków i nie znaleziono nic do zrobienia.")
        return False

    def run(self):
        if not self.location_manager.navigate_to_city():
            self.logger.error("Nie udało się nawigować do miasta.")
            return False

        if not self.ocr_manager.find_text("build"):
            return True

        if not self._enter_main_building_menu():
            return False

        return self._find_and_start_task()