# utils/locate.py
import cv2
import numpy as np
from PIL import ImageGrab
import os
from utils.mouse_actions import click as mouse_click

def locate(bot, pattern_path, threshold=0.95, perform_click=True):
    bot = bot.logger
    try:
        screenshot_pil = ImageGrab.grab()
        screenshot_np = np.array(screenshot_pil)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        screenshot_gray = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
    except Exception:
        return None

    if os.path.isdir(pattern_path):
        patterns = [os.path.join(pattern_path, f) for f in os.listdir(pattern_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    elif os.path.isfile(pattern_path):
        patterns = [pattern_path]
    else:
        return None

    if not patterns:
        return None

    best_match_value = -1
    best_match_location = None
    best_match_dimensions = None

    for pattern_file in patterns:
        try:
            template_rgba = cv2.imread(pattern_file, cv2.IMREAD_UNCHANGED)
            if template_rgba is None:
                continue

            if len(template_rgba.shape) == 3 and template_rgba.shape[2] == 4:
                bgr_channels = template_rgba[:, :, :3]
                alpha_channel_mask = template_rgba[:, :, 3]
                template_gray = cv2.cvtColor(bgr_channels, cv2.COLOR_BGR2GRAY)
                mask = alpha_channel_mask
            else:
                template_gray = cv2.cvtColor(template_rgba, cv2.COLOR_BGR2GRAY)
                mask = None
            
            h, w = template_gray.shape
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED, mask=mask)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > best_match_value:
                best_match_value = max_val
                best_match_location = max_loc
                best_match_dimensions = (w, h)
        except Exception:
            continue

    if best_match_value >= threshold:
        top_left_x, top_left_y = best_match_location
        width, height = best_match_dimensions
        
        if perform_click:
            center_x = top_left_x + width / 2
            center_y = top_left_y + height / 2
            mouse_click(center_x, center_y)

        return (top_left_x, top_left_y, width, height)

    return None
