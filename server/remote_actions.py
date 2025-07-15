# server/remote_actions.py
import pyautogui
import random
import time
import pytweening
import psutil
import pygetwindow as gw
from PIL import ImageGrab
import io
import base64
import subprocess

def click(target_x, target_y):
    PIXEL_OFFSET = 10
    MOVE_DURATION_RANGE = (0.2, 0.6)
    CLICK_DURATION_RANGE = (0.05, 0.15)

    offset_x = random.randint(-PIXEL_OFFSET, PIXEL_OFFSET)
    offset_y = random.randint(-PIXEL_OFFSET, PIXEL_OFFSET)
    final_x = target_x + offset_x
    final_y = target_y + offset_y

    move_duration = random.uniform(MOVE_DURATION_RANGE[0], MOVE_DURATION_RANGE[1])

    pyautogui.moveTo(
        final_x,
        final_y,
        duration=move_duration,
        tween=pytweening.easeInOutQuad
    )

    click_duration = random.uniform(CLICK_DURATION_RANGE[0], CLICK_DURATION_RANGE[1])
    pyautogui.mouseDown(button='left')
    time.sleep(click_duration)
    pyautogui.mouseUp(button='left')
    return True

def move_to(x, y, duration=0.1):
    pyautogui.moveTo(x, y, duration=duration)
    return True

def press(key):
    pyautogui.press(key)
    return True

def grab_screenshot(bbox=None):
    screenshot_pil = ImageGrab.grab(bbox=bbox)
    buffered = io.BytesIO()
    screenshot_pil.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == process_name.lower():
            return True
    return False

def activate_window(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        if window:
            if window.isMinimized:
                window.restore()
            window.activate()
            time.sleep(1)
            return True
    except IndexError:
        pass
    return False

def popen(command_list):
    subprocess.Popen(command_list)
    return True

def run_command(command_list):
    result = subprocess.run(command_list, check=True, capture_output=True, text=True)
    return result.stdout
