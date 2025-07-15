# client/tasks/gather_resources_task.py
import sys
import os
import cv2
import numpy as np
import re

# Dodanie ścieżki projektu do sys.path, aby umożliwić importy
# przy bezpośrednim uruchamianiu skryptu do celów testowych.
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.append(project_root)

from client.tasks.base_task import BaseTask

class GatherResourcesTask(BaseTask):
    def __init__(self, bot):
        super().__init__(bot)
        self.max_legions = 0
        self.current_legions = 0
        self.least_resource = None
        self.legion_avatars = {}
        self.legion_1_region = (1316, 139, 20, 24)
        self.legion_2_region = (1297, 196, 21, 23)
        self.legion_3_region = (1285, 254, 20, 22)
        self.legion_4_region = (1281, 310, 18, 23)
        self.avatars_region = (1229, 113, 128, 421)

    def check_returned_legions(self):
        if not self.location_manager.navigate_to_city():
            return False #nie udało się przejść do miasta, błąd zadania

        if self.max_legions == 0:
            self.logger.warning("Brak informacji o maksymalnej liczbie legionów, zakładam, że można wysłać jeden.")
            return 1

        legions_that_returned = []
        # Iteracja po kopii, aby móc bezpiecznie usuwać elementy
        for legion_id, avatar_image in list(self.legion_avatars.items()):
            # Konwersja obrazu avatara na ścieżkę pliku tymczasowego
            avatar_path = f"temp_avatar_{legion_id}.png"
            avatar_image.save(avatar_path)
            
            # Użycie PngLocator do sprawdzenia obecności avatara
            if not self.png_locator.find(avatar_path, threshold=0.95, perform_click=False, region=self.avatars_region):
                legions_that_returned.append(legion_id)  # Legion wrócił
            os.remove(avatar_path)
        if legions_that_returned:
            self.logger.warning(f"Wykryto powrót legionów: {legions_that_returned}.")
            for legion_id in legions_that_returned:
                del self.legion_avatars[legion_id]
                self.current_legions -= 1
        return len(legions_that_returned)

    def check_least_resource(self):
        try:
            # Logika sprawdzania, którego surowca jest najmniej
            # i aktualizacja self.least_resource
            pass
        except Exception as e:
            self.logger.error(f"Błąd podczas próby sprawdzenia najmniejszego surowca: {e}")

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
            self.logger.error(f"Błąd podczas próby znalezienia surowców: {e}")
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
                self.logger.warning(f"Odczytano legiony: {self.current_legions}/{self.max_legions}")
                return True
            else:
                numbers = re.findall(r'\d+', text)
                if len(numbers) >= 2:
                    self.current_legions = int(numbers[0])
                    self.max_legions = int(numbers[-1])
                    self.logger.info(f"Odczytano legiony (alternatywnie): {self.current_legions}/{self.max_legions}")
                    return True
                else:
                    self.logger.error(f"Nie udało się sparsować liczby legionów z tekstu OCR: '{text}'")
                    return False
        except Exception as e:
            self.logger.critical(f"Błąd podczas odczytu legionów: {e}")
            return False

    def send_legion_to_gather(self):
        if self.current_legions < self.max_legions:
            if not self.png_locator.click_on_png(r'png\gather_resources\create_legion.png'):
                self.logger.error("Nie można kliknąć przycisku 'Create Legion'.")
                return False
            if not self.png_locator.click_on_png(r'png\gather_resources\march.png'):
                self.logger.error("Nie można kliknąć przycisku 'March'.")
                return False
            self.current_legions += 1
            self.logger.info(f"Legion wysłany do zbierania surowców. Aktualna liczba legionów: {self.current_legions}/{self.max_legions}")
            self.update_avatar_count()
            return True

    def update_avatar_count(self):
        """
        Robi zrzuty ekranu awatarów dla wszystkich aktualnie wysłanych legionów
        i przechowuje je w self.legion_avatars.
        """
        self.logger.warning(f"Aktualizacja awatarów dla {self.current_legions} legionów.")
        self.legion_avatars.clear()

        region_map = {
            1: self.legion_1_region,
            2: self.legion_2_region,
            3: self.legion_3_region,
            4: self.legion_4_region,
        }

        for i in range(1, self.current_legions + 1):
            region = region_map.get(i)
            if not region:
                self.logger.error(f"Brak zdefiniowanego regionu dla legionu nr {i}.")
                continue
            
            try:
                avatar_image = self.bot.screenshot_grabber.get_screenshot(bbox=region)
                if avatar_image:
                    self.legion_avatars[i] = avatar_image
            except Exception as e:
                self.logger.error(f"Wystąpił wyjątek podczas przechwytywania awatara dla legionu {i}: {e}")

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
