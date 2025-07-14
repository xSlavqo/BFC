# client/managers/ocr_manager.py (dawniej managers/ocr_manager.py)
import time

class OcrManager:
    CACHE_MARGIN = 15

    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.ocr_locator = bot.ocr_locator # Używa instancji OcrLocator
        self.text_cache = {}
        self.logger.warning("Menedżer OCR zainicjowany.")

    def _get_cached_search_region(self, bbox):
        x_coords = [p[0] for p in bbox]
        y_coords = [p[1] for p in bbox]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        return (
            max(0, min_x - self.CACHE_MARGIN), 
            max(0, min_y - self.CACHE_MARGIN), 
            max_x + self.CACHE_MARGIN, 
            max_y + self.CACHE_MARGIN
        )

    def _get_center_of_bbox(self, bbox):
        x_coords = [p[0] for p in bbox]
        y_coords = [p[1] for p in bbox]
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        return (int(center_x), int(center_y))

    def find_text(self, text_to_find, click=False):
        target_word = text_to_find.lower()
        
        # Wyszukiwanie w cache
        if target_word in self.text_cache:
            region = self.text_cache[target_word]
            screenshot = self.bot.screenshot_grabber.get_screenshot(bbox=region)
            if screenshot:
                found_bbox = self.ocr_locator.find_word_in_image(screenshot, target_word)
                if found_bbox:
                    absolute_bbox = [[p[0] + region[0], p[1] + region[1]] for p in found_bbox]
                    center_coords = self._get_center_of_bbox(absolute_bbox)
                    if click: self.bot.click(*center_coords)
                    return center_coords

        # Wyszukiwanie na pełnym ekranie
        full_screenshot = self.bot.screenshot_grabber.get_screenshot()
        if full_screenshot:
            found_bbox = self.ocr_locator.find_word_in_image(full_screenshot, target_word)
            if found_bbox:
                self.text_cache[target_word] = self._get_cached_search_region(found_bbox)
                center_coords = self._get_center_of_bbox(found_bbox)
                if click: self.bot.click(*center_coords)
                return center_coords
        
        return None
