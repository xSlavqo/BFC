# shared/remote_control.py
import socket
import json
import base64
from PIL import Image
import io
import numpy as np
import struct

class RemoteClient:
    def __init__(self, laptop_ip, port):
        self.laptop_ip = laptop_ip
        self.port = port
        self.logger = None 
        self.timeout = 60

    def set_logger(self, logger):
        self.logger = logger

    def _send_full_message(self, s, message_bytes):
        message_length = len(message_bytes)
        s.sendall(struct.pack('!Q', message_length))
        s.sendall(message_bytes)

    def _recv_full_message(self, s):
        raw_message_length = s.recv(8)
        if not raw_message_length:
            return None
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
        try:
            # --- POCZĄTEK POPRAWKI ---
            # Rozszerzona logika czyszczenia argumentów przed serializacją do JSON.
            # Konwertuje typy NumPy na standardowe typy Pythona.
            cleaned_kwargs = {}
            for k, v in kwargs.items():
                if k == 'bbox' and v is not None:
                    # Jawnie konwertuj każdy element krotki bbox na int
                    cleaned_kwargs[k] = tuple(int(x) for x in v)
                elif isinstance(v, np.integer):
                    cleaned_kwargs[k] = int(v)
                else:
                    cleaned_kwargs[k] = v
            
            cleaned_args = [int(arg) if isinstance(arg, np.integer) else arg for arg in args]
            # --- KONIEC POPRAWKI ---
            
            message = {'command': command_name, 'args': cleaned_args, 'kwargs': cleaned_kwargs}
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((self.laptop_ip, self.port))
                
                self._send_full_message(s, json.dumps(message).encode('utf-8'))
                raw_response_data = self._recv_full_message(s)
                
                if raw_response_data is None:
                    if self.logger: self.logger.error(f"Brak odpowiedzi od laptopa dla komendy '{command_name}'.")
                    return None

                response = json.loads(raw_response_data.decode('utf-8'))
                
                if response.get('status') == 'success':
                    return response.get('result')
                else:
                    if self.logger: self.logger.error(f"Błąd z laptopa dla komendy '{command_name}': {response.get('error')}")
                    return None
        except Exception as e:
            if self.logger: self.logger.error(f"Błąd komunikacji z laptopem dla komendy '{command_name}': {e}")
            return None

    def click_remote(self, x, y):
        return self.send_command('click', x, y)

    def move_to_remote(self, x, y, duration=0.1):
        return self.send_command('move_to', x, y, duration=duration)

    def press_remote(self, key):
        return self.send_command('press', key)
    
    def grab_screenshot_remote(self, bbox=None):
        # Przekazujemy bbox do send_command, które teraz go oczyści
        encoded_image = self.send_command('grab_screenshot', bbox=bbox)
        if encoded_image:
            try:
                decoded_image = base64.b64decode(encoded_image)
                image_stream = io.BytesIO(decoded_image)
                return Image.open(image_stream)
            except Exception as e:
                if self.logger: self.logger.error(f"Błąd dekodowania zrzutu ekranu: {e}")
                return None
        return None

    def is_process_running_remote(self, process_name):
        return self.send_command('is_process_running', process_name)

    def activate_window_remote(self, window_title):
        return self.send_command('activate_window', window_title)

    def popen_remote(self, command_list):
        return self.send_command('popen', command_list)

    def run_command_remote(self, command_list):
        return self.send_command('run_command', command_list)
