# utils/locate.py
import cv2
import numpy as np
from PIL import ImageGrab
import os
import time
from utils.mouse_actions import click as mouse_click

DEFAULT_ATTEMPTS = 3
DEFAULT_DELAY = 1

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

            if len(template_rgba.shape) == 3 and template_rgba.shape[2] == 4:
                bgr_channels = template_rgba[:, :, :3]
                alpha_channel = template_rgba[:, :, 3]
                template_gray = cv2.cvtColor(bgr_channels, cv2.COLOR_BGR2GRAY)
                mask = alpha_channel
            else:
                template_gray = cv2.cvtColor(template_rgba, cv2.COLOR_BGR2GRAY)
                mask = None
            
            h, w = template_gray.shape
            prepared_patterns.append({'template': template_gray, 'mask': mask, 'dims': (w, h)})
        except Exception as e:
            logger.error(f"Wystąpił błąd podczas przygotowywania wzorca {pattern_file}: {e}")
            continue
    
    if not prepared_patterns:
        logger.error("Żaden ze wzorców nie mógł zostać poprawnie przygotowany.")
        return None

    for attempt in range(DEFAULT_ATTEMPTS):
        try:
            bbox = region if region else None
            screenshot_pil = ImageGrab.grab(bbox=bbox)
            screenshot_np = np.array(screenshot_pil)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            screenshot_gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            logger.error(f"Błąd podczas przechwytywania lub przetwarzania zrzutu ekranu: {e}")
            if attempt < DEFAULT_ATTEMPTS - 1:
                time.sleep(DEFAULT_DELAY)
            continue

        best_match_value = -1
        best_match_location = None
        best_match_dimensions = None

        for pattern in prepared_patterns:
            result = cv2.matchTemplate(screenshot_gray, pattern['template'], cv2.TM_CCOEFF_NORMED, mask=pattern['mask'])
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > best_match_value:
                best_match_value = max_val
                best_match_location = max_loc
                best_match_dimensions = pattern['dims']

        if best_match_value >= threshold:
            top_left_x, top_left_y = best_match_location
            width, height = best_match_dimensions
            
            if region:
                top_left_x += region[0]
                top_left_y += region[1]

            if perform_click:
                center_x = top_left_x + width / 2
                center_y = top_left_y + height / 2
                mouse_click(center_x, center_y)

            return (top_left_x, top_left_y, width, height)
        
        if attempt < DEFAULT_ATTEMPTS - 1:
            time.sleep(DEFAULT_DELAY)

    return None
