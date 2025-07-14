# utils/locate.py
import cv2
import numpy as np
import os
import time
from utils.mouse_actions import click as mouse_click

class Locator:
    CACHE_MARGIN = 20

    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.pattern_cache = {}

    def _get_cached_search_region(self, location, dimensions):
        x, y = location
        w, h = dimensions
        return (
            max(0, x - self.CACHE_MARGIN),
            max(0, y - self.CACHE_MARGIN),
            x + w + self.CACHE_MARGIN,
            y + h + self.CACHE_MARGIN
        )

    def _prepare_patterns(self, pattern_path):
        if os.path.isdir(pattern_path):
            pattern_files = [os.path.join(pattern_path, f) for f in os.listdir(pattern_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        elif os.path.isfile(pattern_path):
            pattern_files = [pattern_path]
        else:
            self.logger.error(f"Ścieżka wzorca nie istnieje: {pattern_path}")
            return []

        prepared = []
        for p_file in pattern_files:
            template_rgba = cv2.imread(p_file, cv2.IMREAD_UNCHANGED)
            if template_rgba is None or template_rgba.size == 0:
                continue

            template_gray = cv2.cvtColor(template_rgba[:,:,:3], cv2.COLOR_BGR2GRAY) if len(template_rgba.shape) == 3 else template_rgba
            mask = template_rgba[:,:,3] if len(template_rgba.shape) == 3 and template_rgba.shape[2] == 4 else None
            h, w = template_gray.shape
            prepared.append({'template': template_gray, 'mask': mask, 'dims': (w, h), 'name': p_file})
        return prepared

    def _safe_match_template(self, screenshot_gray, template, mask=None):
        """
        Bezpieczna wersja matchTemplate, która ręcznie filtruje wyniki,
        aby uniknąć nieskończonych lub nieprawidłowych wartości.
        """
        res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED, mask=mask)
        
        best_val = -1
        best_loc = None
        
        # Ręczne przeszukiwanie wyników z pominięciem inf/NaN
        for y in range(res.shape[0]):
            for x in range(res.shape[1]):
                val = res[y, x]
                if not np.isinf(val) and not np.isnan(val) and val > best_val:
                    best_val = val
                    best_loc = (x, y)
        
        return best_val, best_loc

    def _search_on_screenshot(self, screenshot_pil, patterns_to_check):
        """Przeszukuje podany zrzut ekranu w poszukiwaniu wzorców."""
        if not screenshot_pil:
            return None, None, None

        screenshot_np = np.array(screenshot_pil.convert('L'))

        best_val, best_loc, best_dims = -1, None, None

        for pattern in patterns_to_check:
            template = pattern['template']
            if template.shape[0] > screenshot_np.shape[0] or template.shape[1] > screenshot_np.shape[1]:
                continue

            # **KLUCZOWA ZMIANA: Użycie bezpiecznej funkcji wyszukiwania**
            max_val, max_loc = self._safe_match_template(screenshot_np, template, pattern['mask'])

            if max_val is not None and max_val > best_val:
                best_val = max_val
                best_loc = max_loc
                best_dims = pattern['dims']

        return best_val, best_loc, best_dims

    def find(self, pattern_path, threshold=0.95, perform_click=True):
        """Główna metoda do znajdowania wzorca z logiką cache."""
        patterns = self._prepare_patterns(pattern_path)
        if not patterns:
            return None

        # Wyszukiwanie w cache
        if pattern_path in self.pattern_cache:
            cached_region = self.pattern_cache[pattern_path]
            for _ in range(2):
                screenshot = self.bot.screenshot_grabber.get_screenshot(bbox=cached_region)
                val, loc, dims = self._search_on_screenshot(screenshot, patterns)

                if val is not None and val >= threshold:
                    abs_x, abs_y = loc[0] + cached_region[0], loc[1] + cached_region[1]
                    if perform_click:
                        center_x, center_y = abs_x + dims[0] / 2, abs_y + dims[1] / 2
                        mouse_click(self.bot, center_x, center_y)
                    return (abs_x, abs_y, dims[0], dims[1])
                
                time.sleep(5)

        # Wyszukiwanie na pełnym ekranie
        screenshot = self.bot.screenshot_grabber.get_screenshot()
        val, loc, dims = self._search_on_screenshot(screenshot, patterns)

        if val is not None and val >= threshold:
            self.pattern_cache[pattern_path] = self._get_cached_search_region(loc, dims)
            if perform_click:
                center_x, center_y = loc[0] + dims[0] / 2, loc[1] + dims[1] / 2
                mouse_click(self.bot, center_x, center_y)
            return (loc[0], loc[1], dims[0], dims[1])

        return None