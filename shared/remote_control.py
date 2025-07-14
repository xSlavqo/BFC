# server_app.py
import socket
import json
import time
import struct
from shared.logger import Logger
# --- PRZYWRÓCONO POPRZEDNI IMPORT ---
import server.remote_actions as remote_actions

logger = Logger(filename="server.log")
HOST = '0.0.0.0'
PORT = 65432

# Mapa komend do funkcji - przywrócono oryginalny zapis
COMMAND_HANDLERS = {
    'click': remote_actions.click,
    'move_to': remote_actions.move_to,
    'press': remote_actions.press,
    'grab_screenshot': remote_actions.grab_screenshot,
    'is_process_running': remote_actions.is_process_running,
    'activate_window': remote_actions.activate_window,
    'popen': remote_actions.popen,
    'run_command': remote_actions.run_command,
}

def send_full_message(conn, message_bytes):
    message_length = len(message_bytes)
    conn.sendall(struct.pack('!Q', message_length))
    conn.sendall(message_bytes)

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

def handle_connection(conn, addr):
    logger.warning(f"Połączono z {addr}")
    try:
        raw_command_data = recv_full_message(conn)
        if raw_command_data is None:
            logger.warning(f"Połączenie z {addr} zostało zamknięte przed odebraniem komendy.")
            return

        command_data = json.loads(raw_command_data.decode('utf-8'))
        command_name = command_data.get('command')
        args = command_data.get('args', [])
        kwargs = command_data.get('kwargs', {})

        handler = COMMAND_HANDLERS.get(command_name)
        if handler:
            result = handler(*args, **kwargs)
            response = {'status': 'success', 'result': result}
        else:
            response = {'status': 'error', 'error': f'Unknown command: {command_name}'}

    except Exception as e:
        logger.error(f"Błąd podczas obsługi komendy od {addr}: {e}")
        response = {'status': 'error', 'error': str(e)}

    response_bytes = json.dumps(response).encode('utf-8')
    send_full_message(conn, response_bytes)

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        logger.warning(f"Serwer nasłuchuje na {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            with conn:
                handle_connection(conn, addr)

if __name__ == '__main__':
    start_server()
