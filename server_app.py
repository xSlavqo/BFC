# server_app.py (na laptopie - POPRAWIONY IMPORT)
import socket
import json
import pyautogui
import time
import psutil
import pygetwindow as gw
from PIL import ImageGrab
import io
import base64
import subprocess
import struct

# WAŻNA ZMIANA: Importuj funkcję click z nowego pliku utils/server_mouse_actions.py
from utils.server_mouse_actions import click as local_mouse_click 

# Zaimplementuj prostego Loggera na laptopie
class Logger:
    def __init__(self):
        self.filename = "laptop_bot.log"
    def _write_log(self, level, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        print(log_entry.strip())
    def error(self, message): self._write_log("ERROR", message)
    def warning(self, message): self._write_log("WARNING", message)

logger = Logger()

HOST = '0.0.0.0'
PORT = 65432

# Funkcja pomocnicza do wysyłania pełnej wiadomości
def send_full_message(conn, message_bytes):
    message_length = len(message_bytes)
    conn.sendall(struct.pack('!Q', message_length))
    conn.sendall(message_bytes)

# Funkcja pomocnicza do odbierania pełnej wiadomości
def recv_full_message(conn):
    raw_message_length = conn.recv(8)
    if not raw_message_length:
        return None
    message_length = struct.unpack('!Q', raw_message_length)[0]

    data = b""
    bytes_recd = 0
    while bytes_recd < message_length:
        chunk = conn.recv(min(message_length - bytes_recd, 4096 * 8))
        if not chunk:
            raise RuntimeError("Socket connection broken")
        data += chunk
        bytes_recd += len(chunk)
    return data


def handle_command(command_data):
    command_name = command_data.get('command')
    args = command_data.get('args', [])
    kwargs = command_data.get('kwargs', {})

    try:
        if command_name == 'click':
            local_mouse_click(args[0], args[1]) 
            return {'status': 'success', 'result': True}
        elif command_name == 'move_to':
            pyautogui.moveTo(*args, duration=kwargs.get('duration', 0.1))
            return {'status': 'success', 'result': True}
        elif command_name == 'press':
            pyautogui.press(*args)
            return {'status': 'success', 'result': True}
        elif command_name == 'grab_screenshot':
            bbox = kwargs.get('bbox')
            screenshot_pil = ImageGrab.grab(bbox=bbox)
            
            buffered = io.BytesIO()
            screenshot_pil.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            logger.warning(f"Zrzut ekranu wykonany i zakodowany do Base64 (bbox: {bbox}).")
            return {'status': 'success', 'result': img_str}
            
        elif command_name == 'is_process_running':
            process_name = args[0]
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == process_name.lower():
                    return {'status': 'success', 'result': True}
            return {'status': 'success', 'result': False}
        elif command_name == 'activate_window':
            window_title = args[0]
            try:
                window = gw.getWindowsWithTitle(window_title)[0]
                if window:
                    if window.isMinimized:
                        window.restore()
                    window.activate()
                    time.sleep(1)
                    return {'status': 'success', 'result': True}
            except IndexError:
                logger.warning(f"Nie znaleziono okna o tytule '{window_title}'.")
            return {'status': 'success', 'result': False}
        elif command_name == 'popen':
            subprocess.Popen(args[0])
            return {'status': 'success', 'result': True}
        elif command_name == 'run_command':
            result = subprocess.run(args[0], check=True, capture_output=True, text=True)
            return {'status': 'success', 'result': result.stdout}
        else:
            return {'status': 'error', 'error': 'Unknown command'}
    except Exception as e:
        logger.error(f"Błąd podczas wykonywania komendy '{command_name}': {e}")
        return {'status': 'error', 'error': str(e)}

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        logger.warning(f"Serwer nasłuchuje na {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            with conn:
                logger.warning(f"Połączono z {addr}")
                try:
                    raw_command_data = recv_full_message(conn)
                    if raw_command_data is None:
                        logger.warning(f"Połączenie z {addr} zostało zamknięte przez klienta przed odebraniem komendy.")
                        continue
                    command_data = json.loads(raw_command_data.decode('utf-8'))

                    response = handle_command(command_data)
                    response_bytes = json.dumps(response).encode('utf-8')

                    send_full_message(conn, response_bytes)
                except RuntimeError as e:
                    logger.error(f"Błąd podczas komunikacji z {addr}: {e}")
                except json.JSONDecodeError:
                    logger.error(f"Odebrano nieprawidłowe dane JSON od {addr}.")
                except Exception as e:
                    logger.error(f"Nieoczekiwany błąd w pętli serwera dla {addr}: {e}")

if __name__ == '__main__':
    start_server()
