# tools/remote_screenshot_tool.py
from shared.remote_control import RemoteClient
from shared.logger import Logger

def get_remote_screenshot_tool(laptop_ip, port):
    """Narzędzie do pobierania zdalnego zrzutu ekranu."""
    logger = Logger(filename="remote_screenshot_tool.log")
    client = RemoteClient(laptop_ip, port)
    client.set_logger(logger)
    
    logger.warning("Pobieranie zdalnego zrzutu ekranu...")
    screenshot = client.grab_screenshot_remote()
    
    if screenshot:
        logger.warning("Zrzut ekranu pomyślnie pobrany.")
        return screenshot
    else:
        logger.error("Nie udało się pobrać zrzutu ekranu.")
        return None

if __name__ == '__main__':
    LAPTOP_IP = '192.168.1.11'
    PORT = 65432

    full_screenshot = get_remote_screenshot_tool(LAPTOP_IP, PORT)
    if full_screenshot:
        try:
            full_screenshot.save("remote_full_screenshot.png")
            print("Zrzut ekranu zapisano jako 'remote_full_screenshot.png'")
        except Exception as e:
            print(f"Błąd podczas zapisywania pliku: {e}")
