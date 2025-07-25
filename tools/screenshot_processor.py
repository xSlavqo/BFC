# tools/screenshot_processor.py
# Ten moduł nie ma zależności od reszty projektu, więc pozostaje bez zmian.
import time
import keyboard
import numpy as np
from PIL import Image, ImageGrab

def capture_static_scene(interval_seconds=1, output_filename="static_scene.png"):
    """
    Przechwytuje serię zrzutów ekranu i tworzy obraz wynikowy
    zawierający tylko statyczne elementy.
    """
    screenshots = []
    print(f"Rozpoczynam przechwytywanie co {interval_seconds} sek.")
    print("Naciśnij i przytrzymaj 'q', aby zatrzymać.")
    
    time.sleep(3)

    try:
        while not keyboard.is_pressed('q'):
            screenshot = ImageGrab.grab()
            screenshots.append(screenshot)
            print(f"Zrobiono zrzut ekranu nr {len(screenshots)}...")
            time.sleep(interval_seconds)
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        return

    if not screenshots:
        print("Nie zrobiono żadnych zrzutów ekranu.")
        return

    print(f"\nPrzetwarzanie {len(screenshots)} obrazów...")

    # Przetwarzanie obrazów
    first_image_size = screenshots[0].size
    np_images = [np.array(img.resize(first_image_size)) for img in screenshots]
    stacked_images = np.stack(np_images, axis=0)
    static_mask_per_channel = np.all(stacked_images == stacked_images[0], axis=0)
    static_mask_2d = np.all(static_mask_per_channel, axis=2)

    base_image_rgba = screenshots[0].convert("RGBA")
    base_data = np.array(base_image_rgba)

    output_data = np.zeros_like(base_data)
    output_data[static_mask_2d] = base_data[static_mask_2d]

    final_image = Image.fromarray(output_data, 'RGBA')
    final_image.save(output_filename)
    print(f"\nObraz zapisano jako '{output_filename}'")

if __name__ == '__main__':
    capture_static_scene()
