# tools/screenshot_processor.py
import time
import keyboard
import numpy as np
from PIL import Image, ImageGrab

def capture_static_scene(interval_seconds=3, output_filename="wynik.png"):
    """
    Wykonuje zrzuty ekranu w określonych odstępach czasu, a po przerwaniu
    przez użytkownika (klawisz 'q') analizuje je i tworzy obraz wynikowy
    zawierający tylko niezmienne piksele.

    Args:
        interval_seconds (int): Czas w sekundach pomiędzy kolejnymi zrzutami ekranu.
        output_filename (str): Nazwa pliku, do którego zostanie zapisany wynikowy obraz.
    """
    screenshots = []
    print(f"Rozpoczynam przechwytywanie ekranu co {interval_seconds} sek.")
    print("Naciśnij i przytrzymaj 'q', aby zatrzymać i przetworzyć obrazy.")

    try:
        while True:
            # Sprawdzanie, czy użytkownik chce zakończyć
            if keyboard.is_pressed('q'):
                print("\nZatrzymano przechwytywanie.")
                break

            # Wykonanie zrzutu ekranu
            screenshot = ImageGrab.grab()
            screenshots.append(screenshot)
            print(f"Zrobiono zrzut ekranu nr {len(screenshots)}...")
            
            # Oczekiwanie przez określony czas
            time.sleep(interval_seconds)

    except Exception as e:
        print(f"Wystąpił błąd podczas przechwytywania: {e}")
        return

    if not screenshots:
        print("Nie zrobiono żadnych zrzutów ekranu. Zamykanie.")
        return

    print(f"\nRozpoczynam przetwarzanie {len(screenshots)} obrazów. To może chwilę potrwać...")

    # Konwersja obrazów PIL do tablic NumPy dla wydajnych obliczeń
    # Upewniamy się, że wszystkie obrazy mają ten sam rozmiar
    first_image_size = screenshots[0].size
    np_images = [np.array(img.resize(first_image_size)) for img in screenshots]

    # Stworzenie jednej dużej tablicy ze wszystkich obrazów
    stacked_images = np.stack(np_images, axis=0)

    # Porównanie każdego obrazu z pierwszym, aby znaleźć identyczne piksele
    # Tworzymy maskę logiczną (True/False) dla pikseli, które są takie same we wszystkich obrazach
    # np.all(..., axis=0) sprawdza, czy wartości są takie same wzdłuż osi "czasu" (obrazów)
    static_mask_per_channel = np.all(stacked_images == stacked_images[0], axis=0)
    
    # Redukujemy maskę do 2D - piksel jest statyczny tylko, jeśli wszystkie jego kanały (R,G,B) są statyczne
    static_mask_2d = np.all(static_mask_per_channel, axis=2)

    # Pobranie danych pikseli z pierwszego zrzutu (w formacie RGBA dla przezroczystości)
    base_image_rgba = screenshots[0].convert("RGBA")
    base_data = np.array(base_image_rgba)

    # Stworzenie nowej, całkowicie przezroczystej tablicy na obraz wynikowy
    height, width = static_mask_2d.shape
    output_data = np.zeros((height, width, 4), dtype=np.uint8)

    # Użycie maski do skopiowania tylko statycznych pikseli z obrazu bazowego do obrazu wynikowego
    output_data[static_mask_2d] = base_data[static_mask_2d]

    # Konwersja tablicy NumPy z powrotem na obraz PIL
    final_image = Image.fromarray(output_data, 'RGBA')

    # Zapisanie obrazu do pliku
    try:
        final_image.save(output_filename)
        print(f"\nPrzetwarzanie zakończone. Obraz zapisano jako '{output_filename}'")
    except Exception as e:
        print(f"Nie udało się zapisać pliku: {e}")


if __name__ == '__main__':
    # Uwaga: Uruchomienie tego skryptu może wymagać uprawnień administratora
    # ze względu na monitorowanie klawiatury przez bibliotekę 'keyboard'.
    capture_static_scene()
