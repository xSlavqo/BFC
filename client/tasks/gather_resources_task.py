# client/tasks/gather_resources_task.py
import sys
import os
import re

# Dodanie ścieżki projektu do sys.path, aby umożliwić importy
# przy bezpośrednim uruchamianiu skryptu do celów testowych.
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

from client.tasks.base_task import BaseTask

class GatherResourcesTask(BaseTask):
    def __init__(self, game_manager, task_manager):
        super().__init__(game_manager, task_manager)
        self.max_legions = 0
        self.current_legions = 0
        self.least_resource = None
        self.hero_avatars = 0

    def check_returned_legions(self):
        try:
            self.location_manager.navigate_to_city()
            if self.max_legions == 0:
                return 1
            else:
                # Logika sprawdzania, ile legionów wróciło
                # i zwrócenie tej liczby
                returned_legions = 0
                return returned_legions
        except Exception as e:
            self.logger.critical(f"Error in check_returned_legions: {e}")
            return 0

    def check_least_resource(self):
        try:
            # Logika sprawdzania, którego surowca jest najmniej
            # i aktualizacja self.least_resource
            pass
        except Exception as e:
            self.logger.critical(f"Error in check_least_resource: {e}")

    def find_resource(self):
        try:
            self.location_manager.navigate_to_map()
            self.remote_control.press_key('f')

            if self.least_resource == 'gold':
                self.remote_control.click(530, 720)
            elif self.least_resource == 'wood':
                self.remote_control.click(680, 720)
            elif self.least_resource == 'stone':
                self.remote_control.click(840, 720)
            
            if not self.png_locator.click_on_png(r'png\gather_resources\search.png'):
                return False

            width, height = self.remote_control.get_screen_resolution()
            self.remote_control.click(width // 2, height // 2)

            if self.png_locator.click_on_png(r'png\gather_resources\gather.png'):
                return True
            
            return False
        except Exception as e:
            self.logger.critical(f"Error in find_resource: {e}")
            return False

    def read_legion_count(self):
        try:
            # Współrzędne regionu do odczytu OCR - mogą wymagać dostosowania
            legion_count_region = (1322, 337, 79, 40) # x, y, width, height
            text = self.ocr_locator.read_text_from_screen_region(legion_count_region)
            
            match = re.search(r'(\d+)\s*/\s*(\d+)', text)
            if match:
                self.current_legions = int(match.group(1))
                self.max_legions = int(match.group(2))
                self.logger.info(f"Odczytano legiony: {self.current_legions}/{self.max_legions}")
                return True
            else:
                numbers = re.findall(r'\d+', text)
                if len(numbers) >= 2:
                    self.current_legions = int(numbers[0])
                    self.max_legions = int(numbers[-1])
                    self.logger.info(f"Odczytano legiony (alternatywnie): {self.current_legions}/{self.max_legions}")
                    return True
                else:
                    self.logger.critical(f"Could not parse legion count from OCR text: '{text}'")
                    return False
        except Exception as e:
            self.logger.critical(f"Error in read_legion_count: {e}")
            return False

    def send_legion_to_gather(self):
        try:
            if self.current_legions < self.max_legions:
                # Logika wysyłania legionu
                self.update_avatar_count()
        except Exception as e:
            self.logger.critical(f"Error in send_legion_to_gather: {e}")

    def update_avatar_count(self):
        try:
            # Logika aktualizacji self.hero_avatars
            pass
        except Exception as e:
            self.logger.critical(f"Error in update_avatar_count: {e}")

    def execute(self):
        try:
            returned_legions_count = self.check_returned_legions()
            if returned_legions_count >= 1:
                self.check_least_resource()
                if self.find_resource():
                    if self.read_legion_count():
                        self.send_legion_to_gather()
        except Exception as e:
            self.logger.critical(f"Critical error in GatherResourcesTask execute: {e}")

