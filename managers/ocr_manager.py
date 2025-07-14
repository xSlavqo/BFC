# managers/ocr_manager.py
import time
import numpy as np
import easyocr
from spellchecker import SpellChecker
from utils.mouse_actions import click as mouse_click

class OcrManager:
    CACHE_MARGIN = 15

    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.spell_en = SpellChecker(language='en')
        self.text_cache = {}
        # self.remote_client = bot.remote_client # Już niepotrzebne bezpośrednio
        self.logger.warning("Menedżer OCR z pamięcią podręczną i opcją klikania został zainicjowany (tylko EN).")

    def _get_cached_search_region(self, bbox):
        x_coords = [p[0] for p in bbox]
        y_coords = [p[1] for p in bbox]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        return (min_x - self.CACHE_MARGIN, min_y - self.CACHE_MARGIN, max_x + self.CACHE_MARGIN, max_y + self.CACHE_MARGIN)

    def _get_center_of_bbox(self, bbox):
        x_coords = [p[0] for p in bbox]
        y_coords = [p[1] for p in bbox]
        center_x = sum(x_coords) / 4
        center_y = sum(y_coords) / 4
        return (int(center_x), int(center_y))

    def _find_word_in_results(self, results, target_word):
        for (bbox, text, prob) in results:
            found_word = text.lower()
            
            if found_word == target_word:
                return bbox
            
            if self.spell_en.correction(found_word) == target_word:
                return bbox
        return None

    def find_text(self, text_to_find, click=False):
        """
        Robi zdalny zrzut ekranu i szuka na nim tekstu lokalnie.

        Args:
            text_to_find (str): Tekst do znalezienia.
            click (bool): Jeśli True, klika w środek znalezionego tekstu.

        Returns:
            tuple: Krotka (x, y) ze środkiem znalezionego tekstu, lub None.
        """
        target_word = text_to_find.lower()
        found_coords = None
        
        # Próba znalezienia w cache i pobranie regionu
        if target_word in self.text_cache:
            region = self.text_cache[target_word]
            for _ in range(2):
                # Używamy ScreenshotGrabber do pobrania zrzutu
                screenshot = self.bot.screenshot_grabber.get_screenshot(bbox=region)
                if screenshot:
                    results = self.reader.readtext(np.array(screenshot))
                    found_bbox = self._find_word_in_results(results, target_word)
                    if found_bbox:
                        absolute_bbox = [[p[0] + region[0], p[1] + region[1]] for p in found_bbox]
                        found_coords = self._get_center_of_bbox(absolute_bbox)
                        break
                if _ == 0:
                    time.sleep(5)
        
        # Jeśli nie znaleziono w cache, przeszukaj cały ekran
        if not found_coords:
            try:
                # Używamy ScreenshotGrabber do pobrania pełnego zrzutu
                full_screenshot = self.bot.screenshot_grabber.get_screenshot()
                if full_screenshot:
                    results = self.reader.readtext(np.array(full_screenshot))
                    found_bbox = self._find_word_in_results(results, target_word)
                    if found_bbox:
                        self.text_cache[target_word] = self._get_cached_search_region(found_bbox)
                        found_coords = self._get_center_of_bbox(found_bbox)
            except Exception as e:
                self.logger.error(f"Wystąpił błąd podczas przetwarzania OCR: {e}")
                return None

        # Obsługa kliknięcia i zwracanie wyniku
        if found_coords:
            self.logger.warning(f"Znaleziono tekst '{text_to_find}' na pozycji {found_coords}.")
            if click:
                self.logger.warning(f"Klikanie w znaleziony tekst '{text_to_find}'.")
                mouse_click(self.bot, found_coords[0], found_coords[1])
            return found_coords
        
        return None
