# utils/remote_control.py (na głównym PC - CRITICAL UPDATE)
import socket
import json
import base64
from PIL import Image
import io
import numpy as np
import struct # Dodany import do pakowania/rozpakowywania długości wiadomości

class RemoteClient:
    def __init__(self, laptop_ip, port):
        self.laptop_ip = laptop_ip
        self.port = port
        self.logger = None 
        self.timeout = 60 # Zwiększony timeout dla operacji sieciowych (sekundy)

    def set_logger(self, logger):
        """Ustawia instancję loggera dla klienta zdalnego."""
        self.logger = logger

    # Funkcja pomocnicza do wysyłania pełnej wiadomości
    def _send_full_message(self, s, message_bytes):
        message_length = len(message_bytes)
        s.sendall(struct.pack('!Q', message_length))
        s.sendall(message_bytes)

    # Funkcja pomocnicza do odbierania pełnej wiadomości
    def _recv_full_message(self, s):
        raw_message_length = s.recv(8)
        if not raw_message_length:
            return None # Połączenie zamknięte przez serwer
        message_length = struct.unpack('!Q', raw_message_length)[0]

        data = b""
        bytes_recd = 0
        while bytes_recd < message_length:
            chunk = s.recv(min(message_length - bytes_recd, 4096 * 8))
            if not chunk:
                raise RuntimeError("Socket connection broken by server")
            data += chunk
            bytes_recd += len(chunk)
        return data


    def send_command(self, command_name, *args, **kwargs):
        """
        Wysyła komendę do serwera na laptopie i odbiera odpowiedź.
        """
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
                
                # Wysyłanie komendy jako JSON z ramką wiadomości
                self._send_full_message(s, json.dumps(message).encode('utf-8'))
                
                # Odbieranie odpowiedzi z ramką wiadomości
                raw_response_data = self._recv_full_message(s)
                
                if raw_response_data is None:
                    if self.logger:
                        self.logger.error(f"Brak odpowiedzi od laptopa (połączenie zamknięte) dla komendy '{command_name}'.")
                    return None

                response = json.loads(raw_response_data.decode('utf-8'))
                
                if response.get('status') == 'success':
                    return response.get('result')
                else:
                    if self.logger:
                        self.logger.error(f"Błąd z laptopa dla komendy '{command_name}': {response.get('error')}")
                    return None
        except ConnectionRefusedError:
            if self.logger:
                self.logger.error(f"Połączenie odrzucone. Upewnij się, że serwer na laptopie jest uruchomiony i dostępny pod IP: {self.laptop_ip}.")
            return None
        except socket.timeout:
            if self.logger:
                self.logger.error(f"Przekroczono limit czasu połączenia z laptopem dla komendy '{command_name}'.")
            return None
        except RuntimeError as e: # Złap błędy z _recv_full_message
            if self.logger:
                self.logger.error(f"Błąd protokołu podczas komunikacji z laptopem dla komendy '{command_name}': {e}")
            return None
        except Exception as e:
            if self.logger:
                self.logger.error(f"Błąd komunikacji z laptopem dla komendy '{command_name}': {e}")
            return None

    def click_remote(self, x, y):
        """Wysyła komendę kliknięcia myszą na zdalnym komputerze."""
        return self.send_command('click', x, y)

    def move_to_remote(self, x, y, duration=0.1):
        """Wysyła komendę przesunięcia myszy na zdalnym komputerze."""
        return self.send_command('move_to', x, y, duration=duration)

    def press_remote(self, key):
        """Wysyła komendę naciśnięcia klawisza na zdalnym komputerze."""
        return self.send_command('press', key)
    
    def grab_screenshot_remote(self, bbox=None):
        """
        Wysyła komendę zrobienia zrzutu ekranu na zdalnym komputerze,
        odbiera go i zwraca jako obiekt PIL.Image.
        """
        encoded_image = self.send_command('grab_screenshot', bbox=bbox)
        if encoded_image:
            try:
                # Dekodowanie obrazu Base64 i konwersja na obiekt PIL Image
                decoded_image = base64.b64decode(encoded_image)
                image_stream = io.BytesIO(decoded_image)
                return Image.open(image_stream)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Błąd dekodowania zrzutu ekranu z laptopa: {e}")
                return None
        return None

    def is_process_running_remote(self, process_name):
        """Sprawdza, czy dany proces jest uruchomiony na zdalnym komputerze."""
        return self.send_command('is_process_running', process_name)

    def activate_window_remote(self, window_title):
        """Aktywuje okno o podanym tytule na zdalnym komputerze."""
        return self.send_command('activate_window', window_title)

    def popen_remote(self, command_list):
        """Uruchamia proces na zdalnym komputerze."""
        return self.send_command('popen', command_list)

    def run_command_remote(self, command_list):
        """Wykonuje komendę systemową na zdalnym komputerze i zwraca jej stdout."""
        return self.send_command('run_command', command_list)