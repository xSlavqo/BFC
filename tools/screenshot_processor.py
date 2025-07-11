# tools/screenshot_processor.py
import time
import keyboard
import numpy as np
from PIL import Image, ImageGrab

def capture_static_scene(interval_seconds=1, output_filename="wynik.png"):
    screenshots = []
    print(f"Rozpoczynam przechwytywanie ekranu co {interval_seconds} sek.")
    print("Naciśnij i przytrzymaj 'q', aby zatrzymać i przetworzyć obrazy.")
    
    print("Start za 5 sekund...")
    time.sleep(5)

    try:
        while True:
            if keyboard.is_pressed('q'):
                print("\nZatrzymano przechwytywanie.")
                break

            screenshot = ImageGrab.grab()
            screenshots.append(screenshot)
            print(f"Zrobiono zrzut ekranu nr {len(screenshots)}...")
            
            time.sleep(interval_seconds)

    except Exception as e:
        print(f"Wystąpił błąd podczas przechwytywania: {e}")
        return

    if not screenshots:
        print("Nie zrobiono żadnych zrzutów ekranu. Zamykanie.")
        return

    print(f"\nRozpoczynam przetwarzanie {len(screenshots)} obrazów. To może chwilę potrwać...")

    first_image_size = screenshots[0].size
    np_images = [np.array(img.resize(first_image_size)) for img in screenshots]

    stacked_images = np.stack(np_images, axis=0)

    static_mask_per_channel = np.all(stacked_images == stacked_images[0], axis=0)
    
    static_mask_2d = np.all(static_mask_per_channel, axis=2)

    base_image_rgba = screenshots[0].convert("RGBA")
    base_data = np.array(base_image_rgba)

    height, width = static_mask_2d.shape
    output_data = np.zeros((height, width, 4), dtype=np.uint8)

    output_data[static_mask_2d] = base_data[static_mask_2d]

    final_image = Image.fromarray(output_data, 'RGBA')

    try:
        final_image.save(output_filename)
        print(f"\nPrzetwarzanie zakończone. Obraz zapisano jako '{output_filename}'")
    except Exception as e:
        print(f"Nie udało się zapisać pliku: {e}")


if __name__ == '__main__':
    capture_static_scene()
