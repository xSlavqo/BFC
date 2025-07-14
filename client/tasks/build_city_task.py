# client/tasks/build_city_task.py
import time
from client.tasks.base_task import BaseTask

class BuildCityTask(BaseTask):
    def __init__(self, bot):
        super().__init__(bot)
        self.png_locator = bot.png_locator
        self.town_hall_coords = (550, 270)

    def _enter_main_building_menu(self):
        self.bot.click(*self.town_hall_coords)
        time.sleep(1)
        if not self.png_locator.find("png/build/enter_upgrade_menu", perform_click=True):
            self.logger.error("Nie znaleziono przycisku wejścia do menu ulepszeń.")
            return False
        return True

    def _find_and_start_task(self):
        max_search_loops = 10
        for i in range(max_search_loops):
            if self.png_locator.find(r"png/build/upgrade.png", perform_click=True):
                time.sleep(1)
                
                # --- POCZĄTEK PRZYWRÓCONEJ LOGIKI ---
                # Wykonuje dodatkowe kliknięcie, aby zamknąć okna po ulepszeniu
                if i == 0:
                    self.bot.click(*self.town_hall_coords)
                else:
                    screenshot = self.bot.screenshot_grabber.get_screenshot()
                    if screenshot:
                        center_x = screenshot.size[0] / 2
                        center_y = screenshot.size[1] / 2
                        self.bot.click(center_x, center_y)
                # --- KONIEC PRZYWRÓCONEJ LOGIKI ---

                self.location_manager.navigate_to_map()
                return True
            
            if not self.png_locator.find(r"png/build/go_button", perform_click=True):
                self.logger.error("Nie znaleziono przycisku 'Go', aby przejść do następnego budynku.")
                return False
            
            time.sleep(2)

            if self.png_locator.find(r"png/build/enter_upgrade_menu", perform_click=True):
                continue
            elif self.png_locator.find(r"png/build/is_new_building", perform_click=False):
                self.bot.click(210, 570)
                time.sleep(1)
                if self.png_locator.find(r"png/build/start_new_building", perform_click=True):
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
            return False

        if not self.ocr_manager.find_text("build"):
            return True

        if not self._enter_main_building_menu():
            return False

        if self._find_and_start_task():
            return True
        else:
            self.location_manager.navigate_to_map()
            return False
