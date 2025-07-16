# client/tasks/gather_resources_task.py
import sys
import os
import time
import numpy as np
import re

# Dodanie ścieżki projektu do sys.path
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
        # Usunięto self.remote_client = self.bot.remote_client, będziemy używać self.bot

    def check_returned_legions(self):
        if not self.location_manager.navigate_to_city():
            return False

        if self.max_legions == 0:
            self.logger.warning("Brak informacji o maksymalnej liczbie legionów, zakładam, że można wysłać jeden.")
            return 1

        legions_that_returned = []
        for legion_id, avatar_image in list(self.legion_avatars.items()):
            avatar_path = f"temp_avatar_{legion_id}.png"
            avatar_image.save(avatar_path)
            
            if not self.png_locator.find(avatar_path, threshold=0.95, perform_click=False, region=self.avatars_region):
                legions_that_returned.append(legion_id)
            os.remove(avatar_path)
            
        if legions_that_returned:
            self.logger.warning(f"Wykryto powrót legionów: {legions_that_returned}.")
            for legion_id in legions_that_returned:
                del self.legion_avatars[legion_id]
                self.current_legions -= 1
        return len(legions_that_returned)

    def check_least_resource(self):
        try:
            self.least_resource = "gold"
        except Exception as e:
            self.logger.error(f"Błąd podczas sprawdzania surowców: {e}")

    def find_resource(self):
        try:
            self.check_least_resource()
            self.location_manager.navigate_to_map()
            time.sleep(1)
            self.bot.remote_client.press_remote('f') # press_remote jest w remote_client

            if self.least_resource == 'gold':
                self.bot.click(530, 720) # <--- POPRAWKA
            elif self.least_resource == 'wood':
                self.bot.click(680, 720) # <--- POPRAWKA
            elif self.least_resource == 'stone':
                self.bot.click(840, 720) # <--- POPRAWKA
            
            if not self.png_locator.find(r'png/gather_resources/search.png', perform_click=True):
                 return False

            # Ta część kodu jest prawdopodobnie niekompletna, bo nie ma metody get_screen_resolution
            # Zakładam, że chcesz kliknąć na środku ekranu
            # self.bot.click(width // 2, height // 2) 

            if self.png_locator.find(r'png/gather_resources/gather.png', perform_click=True):
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Błąd podczas szukania surowców: {e}")
            return False

    def read_legion_count(self):
        try:
            legion_count_region = (1322, 337, 79, 40)
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
                    self.logger.error(f"Nie sparsowano liczby legionów z: '{text}'")
                    return False
        except Exception as e:
            self.logger.error(f"Błąd podczas odczytu legionów: {e}")
            return False

    def send_legion_to_gather(self):
        if self.current_legions < self.max_legions:
            if not self.png_locator.find(r'png/gather_resources/create_legion.png', perform_click=True):
                self.logger.error("Nie można kliknąć 'Create Legion'.")
                return False
            if not self.png_locator.find(r'png/gather_resources/march.png', perform_click=True):
                self.logger.error("Nie można kliknąć 'March'.")
                return False
            self.current_legions += 1
            self.logger.info(f"Legion wysłany. Aktualna liczba: {self.current_legions}/{self.max_legions}")
            self.update_avatar_count()
            return True

    def update_avatar_count(self):
        self.logger.warning(f"Aktualizacja awatarów dla {self.current_legions} legionów.")
        self.legion_avatars.clear()
        region_map = {1: self.legion_1_region, 2: self.legion_2_region, 3: self.legion_3_region, 4: self.legion_4_region}
        for i in range(1, self.current_legions + 1):
            region = region_map.get(i)
            if not region:
                self.logger.error(f"Brak regionu dla legionu nr {i}.")
                continue
            try:
                avatar_image = self.bot.screenshot_grabber.get_screenshot(bbox=region)
                if avatar_image:
                    self.legion_avatars[i] = avatar_image
            except Exception as e:
                self.logger.error(f"Wyjątek podczas przechwytywania awatara dla legionu {i}: {e}")

    def run(self):
        returned_count = self.check_returned_legions()
        if returned_count > 0:
            for _ in range(returned_count):
                if self.find_resource():
                    self.send_legion_to_gather()
                    time.sleep(2) # Chwila przerwy między wysyłaniem kolejnych
        
        # Sprawdzenie, czy są bezczynne legiony, których nie wykryto jako powracające
        self.read_legion_count()
        if self.current_legions < self.max_legions:
            available_to_send = self.max_legions - self.current_legions
            self.logger.warning(f"Wykryto {available_to_send} bezczynnych legionów. Próba wysłania.")
            for _ in range(available_to_send):
                 if self.find_resource():
                    self.send_legion_to_gather()
                    time.sleep(2)

        return True # Zadanie zawsze kończy się sukcesem, pętla główna decyduje kiedy je ponowić