# utils/mouse_actions.py
import pyautogui
import random
import time
import pytweening

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

if __name__ == '__main__':
    time.sleep(3)

    screen_width, screen_height = pyautogui.size()
    center_x = screen_width / 2
    center_y = screen_height / 2
    
    print(f"Wykonuję kliknięcie w pobliżu ({int(center_x)}, {int(center_y)})")
    click(center_x, center_y)
