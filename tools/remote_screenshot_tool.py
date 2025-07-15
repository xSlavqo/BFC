# tools/remote_screenshot_tool.py
import sys
import datetime
import os

# Dodaje główny katalog projektu do ścieżki Pythona, aby znaleźć moduł 'shared'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.remote_control import RemoteClient
from shared.logger import Logger

def get_remote_screenshot_tool(laptop_ip, port):
    """Narzędzie do pobierania zdalnego zrzutu ekranu."""
    client = RemoteClient(laptop_ip, port)
    screenshot = client.grab_screenshot_remote()
    
    return screenshot

if __name__ == '__main__':
    LAPTOP_IP = '192.168.1.11'
    PORT = 65432

    full_screenshot = get_remote_screenshot_tool(LAPTOP_IP, PORT)
    if not full_screenshot:
        print("Nie udało się pobrać zrzutu ekranu.")
        exit()

    # Tworzenie podkatalogu, jeśli nie istnieje
    output_dir = "raw_ss"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generowanie nazwy pliku z datą i godziną
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"remote_full_screenshot_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)

    try:
        full_screenshot.save(filepath)
        print(f"Zrzut ekranu zapisano jako '{filepath}'")
    except Exception as e:
        print(f"Błąd podczas zapisywania pliku: {e}")
