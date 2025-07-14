# utils/mouse_actions.py (NA GŁÓWNYM PC - WERSJA DLA KLIENTA)
import random
import time
# Nie importujemy pyautogui ani pytweening tutaj, bo akcje są zdalne.

# Funkcja click na głównym PC przyjmuje 'bot_instance' jako pierwszy argument
def click(bot_instance, target_x, target_y):
    PIXEL_OFFSET = 10
    MOVE_DURATION_RANGE = (0.2, 0.6)
    CLICK_DURATION_RANGE = (0.05, 0.15)

    offset_x = random.randint(-PIXEL_OFFSET, PIXEL_OFFSET)
    offset_y = random.randint(-PIXEL_OFFSET, PIXEL_OFFSET)
    final_x = target_x + offset_x
    final_y = target_y + offset_y

    move_duration = random.uniform(MOVE_DURATION_RANGE[0], MOVE_DURATION_RANGE[1])

    # Używamy remote_client do przesunięcia myszy na laptopie
    bot_instance.remote_client.move_to_remote(
        final_x,
        final_y,
        duration=move_duration
    )

    # Wysyłamy komendę kliknięcia do laptopa
    # Serwer na laptopie będzie używał pyautogui.mouseDown/mouseUp zgodnie ze swoją wersją mouse_actions.py
    bot_instance.remote_client.click_remote(final_x, final_y)
    # Czas po kliknięciu jest już obsługiwany przez serwer,
    # więc nie potrzebujemy tu dodatkowego time.sleep() po kliknięciu.
    # Jeśli chcesz, aby po kliknięciu był dodatkowy opóźnienie w tej funkcji,
    # możesz je dodać, ale ruch już ma duration.
