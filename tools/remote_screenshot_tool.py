# tools/remote_screenshot_tool.py
import socket
import json
import base64
from PIL import Image
import io
import numpy as np
import time
import struct # Dodano brakujący import

# --- POCZĄTEK POPRAWKI ---

# Funkcje pomocnicze do obsługi protokołu komunikacyjnego z ramkowaniem wiadomości
def _send_full_message(s, message_bytes):
    """Pakuje i wysyła wiadomość z nagłówkiem długości."""
    message_length = len(message_bytes)
    s.sendall(struct.pack('!Q', message_length))
    s.sendall(message_bytes)

def _recv_full_message(s):
    """Odbiera wiadomość z nagłówkiem długości."""
    # Odczytaj 8-bajtowy nagłówek z długością wiadomości
    raw_message_length = s.recv(8)
    if not raw_message_length:
        return None # Połączenie zamknięte
    message_length = struct.unpack('!Q', raw_message_length)[0]

    # Odczytaj dokładnie tyle bajtów, ile wskazuje nagłówek
    data = b""
    bytes_recd = 0
    while bytes_recd < message_length:
        chunk = s.recv(min(message_length - bytes_recd, 4096 * 8))
        if not chunk:
            raise RuntimeError("Socket connection broken")
        data += chunk
        bytes_recd += len(chunk)
    return data

# --- KONIEC POPRAWKI ---


class SimpleRemoteClient:
    def __init__(self, laptop_ip, port):
        self.laptop_ip = laptop_ip
        self.port = port
        self.timeout = 60 # Zwiększono timeout, aby pasował do innych części aplikacji

    def send_command(self, command_name, *args, **kwargs):
        try:
            cleaned_kwargs = {}
            for k, v in kwargs.items():
                if k == 'bbox' and isinstance(v, (tuple, list)):
                    cleaned_kwargs[k] = tuple(int(x) for x in v)
                elif isinstance(v, np.integer):
                    cleaned_kwargs[k] = int(v)
                else:
                    cleaned_kwargs[k] = v
            
            cleaned_args = []
            for arg in args:
                if isinstance(arg, np.integer):
                    cleaned_args.append(int(arg))
                else:
                    cleaned_args.append(arg)

            message = {'command': command_name, 'args': cleaned_args, 'kwargs': cleaned_kwargs}
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((self.laptop_ip, self.port))
                
                # --- POCZĄTEK POPRAWKI ---
                # Użyj funkcji _send_full_message do wysłania komendy
                _send_full_message(s, json.dumps(message).encode('utf-8'))
                
                # Użyj funkcji _recv_full_message do odebrania odpowiedzi
                raw_response_data = _recv_full_message(s)
                
                if raw_response_data is None:
                    print("Błąd: Brak odpowiedzi od serwera.")
                    return None

                response = json.loads(raw_response_data.decode('utf-8'))
                # --- KONIEC POPRAWKI ---
                
                if response.get('status') == 'success':
                    return response.get('result')
                else:
                    print(f"Błąd z serwera: {response.get('error')}")
                    return None

        except ConnectionRefusedError:
            print("Błąd: Połączenie odrzucone. Upewnij się, że serwer na laptopie jest uruchomiony.")
            return None
        except socket.timeout:
            print("Błąd: Przekroczono limit czasu połączenia.")
            return None
        except Exception as e:
            print(f"Błąd komunikacji: {e}")
            return None

    def grab_screenshot_remote(self, bbox=None):
        """Pobiera zdalny zrzut ekranu."""
        encoded_image = self.send_command('grab_screenshot', bbox=bbox)
        if encoded_image:
            try:
                decoded_image = base64.b64decode(encoded_image)
                image_stream = io.BytesIO(decoded_image)
                return Image.open(image_stream)
            except Exception as e:
                print(f"Błąd dekodowania obrazu: {e}")
                return None
        return None

def get_remote_screenshot_tool(laptop_ip, port):
    """Główna funkcja narzędzia do pobierania zrzutu ekranu."""
    client = SimpleRemoteClient(laptop_ip, port)
    screenshot = client.grab_screenshot_remote(bbox=None) # Zawsze cały ekran
    if screenshot:
        print("Zrzut ekranu pomyślnie pobrany.")
        return screenshot
    else:
        print("Nie udało się pobrać zrzutu ekranu.")
        return None

if __name__ == '__main__':
    LAPTOP_IP = '192.168.1.11'
    PORT = 65432

    full_screenshot = get_remote_screenshot_tool(LAPTOP_IP, PORT)
    if full_screenshot:
        try:
            full_screenshot.save("remote_full_screenshot_tool.png")
            print("Zrzut ekranu zapisano jako 'remote_full_screenshot_tool.png'")
        except Exception as e:
            print(f"Błąd podczas zapisywania pliku: {e}")