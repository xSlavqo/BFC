# utils/locate.py
import cv2
import numpy as np
import os
import time
from utils.mouse_actions import click as mouse_click

DEFAULT_ATTEMPTS = 3
DEFAULT_DELAY = 1

def safe_match_template(screenshot_gray, template, mask=None):
    """Bezpieczna wersja matchTemplate z ręcznym wyszukiwaniem najlepszego dopasowania"""
    result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED, mask=mask)
    
    best_val = -1
    best_loc = None
    
    # Ręczne przeszukiwanie wyników z pominięciem inf/NaN
    for y in range(result.shape[0]):
        for x in range(result.shape[1]):
            val = result[y, x]
            if not np.isinf(val) and not np.isnan(val) and val > best_val:
                best_val = val
                best_loc = (x, y)
    
    return best_val, best_loc

def locate(bot, pattern_path, threshold=0.95, perform_click=True, region=None):
    logger = bot.logger
    
    if os.path.isdir(pattern_path):
        pattern_files = [os.path.join(pattern_path, f) for f in os.listdir(pattern_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    elif os.path.isfile(pattern_path):
        pattern_files = [pattern_path]
    else:
        logger.error(f"Podana ścieżka nie jest prawidłowym plikiem ani katalogiem: {pattern_path}")
        return None

    if not pattern_files:
        logger.warning(f"Nie znaleziono wzorców obrazów w podanej ścieżce: {pattern_path}")
        return None

    prepared_patterns = []
    for pattern_file in pattern_files:
        try:
            template_rgba = cv2.imread(pattern_file, cv2.IMREAD_UNCHANGED)
            if template_rgba is None:
                logger.warning(f"Nie można odczytać pliku obrazu, pomijanie: {pattern_file}")
                continue

            if template_rgba.size == 0:
                logger.warning(f"Obraz wzorca {pattern_file} jest pusty, pomijanie.")
                continue

            if len(template_rgba.shape) == 3 and template_rgba.shape[2] == 4:
                bgr_channels = template_rgba[:, :, :3]
                alpha_channel = template_rgba[:, :, 3]
                template_gray = cv2.cvtColor(bgr_channels, cv2.COLOR_BGR2GRAY)
                mask = alpha_channel
            else:
                template_gray = cv2.cvtColor(template_rgba, cv2.COLOR_BGR2GRAY)
                mask = None
            
            if template_gray.size == 0:
                logger.warning(f"Szary obraz wzorca {pattern_file} jest pusty po konwersji, pomijanie.")
                continue

            h, w = template_gray.shape
            prepared_patterns.append({
                'template': template_gray, 
                'mask': mask, 
                'dims': (w, h), 
                'name': pattern_file
            })
        except Exception as e:
            logger.error(f"Wystąpił błąd podczas przygotowywania wzorca {pattern_file}: {e}")
            continue
    
    if not prepared_patterns:
        logger.error("Żaden ze wzorców nie mógł zostać poprawnie przygotowany.")
        return None

    for attempt in range(DEFAULT_ATTEMPTS):
        try:
            bbox = region if region else None
            screenshot_pil = bot.screenshot_grabber.get_screenshot(bbox=bbox)
            
            if not screenshot_pil:
                logger.error("Nie udało się pobrać zrzutu ekranu ze zdalnego komputera.")
                if attempt < DEFAULT_ATTEMPTS - 1:
                    time.sleep(DEFAULT_DELAY)
                continue

            screenshot_np = np.array(screenshot_pil)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            screenshot_gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)

            if screenshot_gray.size == 0:
                logger.error("Pobrany zrzut ekranu jest pusty po konwersji na skalę szarości.")
                if attempt < DEFAULT_ATTEMPTS - 1:
                    time.sleep(DEFAULT_DELAY)
                continue

        except Exception as e:
            logger.error(f"Błąd podczas przechwytywania lub przetwarzania zdalnego zrzutu ekranu: {e}")
            if attempt < DEFAULT_ATTEMPTS - 1:
                time.sleep(DEFAULT_DELAY)
            continue

        best_match_value = -1
        best_match_location = None
        best_match_dimensions = None
        best_match_pattern_name = "N/A"

        for pattern in prepared_patterns:
            template = pattern['template']
            
            if template.shape[0] > screenshot_gray.shape[0] or \
               template.shape[1] > screenshot_gray.shape[1]:
                logger.warning(f"Wzorzec '{pattern['name']}' jest większy niż zrzut ekranu. Pomijam dopasowanie.")
                continue

            # Używamy naszej bezpiecznej funkcji dopasowania
            max_val, max_loc = safe_match_template(screenshot_gray, template, pattern['mask'])
            
            if max_val == -1:  # Nie znaleziono żadnych poprawnych wyników
                logger.warning(f"Nie znaleziono poprawnych dopasowań dla wzorca '{pattern['name']}'")
                continue

            logger.warning(f"Dopasowanie wzorca '{pattern['name']}' - Wartość: {max_val:.4f} w pozycji: {max_loc}")

            if max_val > best_match_value:
                best_match_value = max_val
                best_match_location = max_loc
                best_match_dimensions = pattern['dims']
                best_match_pattern_name = pattern['name']

        logger.warning(f"Najlepszy wynik dopasowania: '{best_match_pattern_name}' - {best_match_value:.4f} (Próg: {threshold:.4f})")

        if best_match_value >= threshold:
            top_left_x, top_left_y = best_match_location
            width, height = best_match_dimensions
            
            if region:
                top_left_x += region[0]
                top_left_y += region[1]

            if perform_click:
                center_x = top_left_x + width / 2
                center_y = top_left_y + height / 2
                logger.warning(f"Klikam w znaleziony wzorzec '{best_match_pattern_name}' na pozycji: ({int(center_x)}, {int(center_y)})")
                mouse_click(bot, center_x, center_y)

            return (top_left_x, top_left_y, width, height)
        
        if attempt < DEFAULT_ATTEMPTS - 1:
            time.sleep(DEFAULT_DELAY)

    logger.warning(f"Nie znaleziono wzorca '{pattern_path}' z progiem {threshold:.4f} po {DEFAULT_ATTEMPTS} próbach.")
    return None