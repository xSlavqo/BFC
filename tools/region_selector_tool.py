# tools/region_selector_tool.py
import socket
import json
import base64
from PIL import Image, ImageTk
import io
import numpy as np
import time
import tkinter as tk
from tkinter import messagebox
import struct # Dodano import modułu struct

# Prosty logger dla tego narzędzia
class ToolLogger:
    def __init__(self):
        self.filename = "region_selector_tool.log"
    def _write_log(self, level, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        print(log_entry.strip())
    def error(self, message): self._write_log("ERROR", message)
    def warning(self, message): self._write_log("WARNING", message)

tool_logger = ToolLogger()

# Funkcja pomocnicza do pakowania/rozpakowywania długości wiadomości (skopiowana z serwera/klienta)
def _send_full_message(s, message_bytes):
    message_length = len(message_bytes)
    s.sendall(struct.pack('!Q', message_length))
    s.sendall(message_bytes)

def _recv_full_message(s):
    raw_message_length = s.recv(8)
    if not raw_message_length:
        return None
    message_length = struct.unpack('!Q', raw_message_length)[0]

    data = b""
    bytes_recd = 0
    while bytes_recd < message_length:
        chunk = s.recv(min(message_length - bytes_recd, 4096 * 8))
        if not chunk:
            raise RuntimeError("Socket connection broken")
        data += chunk
        bytes_recd += len(chunk)
    return data

class SimpleRemoteClient:
    """
    Uproszczony klient zdalnego sterowania do użytku w niezależnych narzędziach.
    """
    def __init__(self, laptop_ip, port):
        self.laptop_ip = laptop_ip
        self.port = port
        self.timeout = 60 # Zwiększony timeout dla operacji sieciowych (sekundy)

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
                
                _send_full_message(s, json.dumps(message).encode('utf-8'))
                
                raw_response_data = _recv_full_message(s)
                
                if raw_response_data is None:
                    tool_logger.error(f"Brak odpowiedzi od laptopa (połączenie zamknięte) dla komendy '{command_name}'.")
                    return None

                response = json.loads(raw_response_data.decode('utf-8'))
                
                if response.get('status') == 'success':
                    return response.get('result')
                else:
                    tool_logger.error(f"Błąd z laptopa dla komendy '{command_name}': {response.get('error')}")
                    return None
        except ConnectionRefusedError:
            tool_logger.error(f"Połączenie odrzucone. Upewnij się, że serwer na laptopie jest uruchomiony i dostępny pod IP: {self.laptop_ip}.")
            return None
        except socket.timeout:
            tool_logger.error(f"Przekroczono limit czasu połączenia z laptopem dla komendy '{command_name}'.")
            return None
        except RuntimeError as e:
            tool_logger.error(f"Błąd protokołu podczas komunikacji z laptopem dla komendy '{command_name}': {e}")
            return None
        except Exception as e:
            tool_logger.error(f"Błąd komunikacji z laptopem dla komendy '{command_name}': {e}")
            return None

    def grab_screenshot_remote(self, bbox=None):
        encoded_image = self.send_command('grab_screenshot', bbox=bbox)
        if encoded_image:
            try:
                decoded_image = base64.b64decode(encoded_image)
                image_stream = io.BytesIO(decoded_image)
                return Image.open(image_stream)
            except Exception as e:
                tool_logger.error(f"Błąd dekodowania zrzutu ekranu z laptopa: {e}")
                return None
        return None

class RegionSelectorApp:
    def __init__(self, master, laptop_ip, port):
        self.master = master
        master.title("Wybór Regionu Ekranu z Laptopa")

        self.laptop_ip = laptop_ip
        self.port = port
        self.remote_client = SimpleRemoteClient(self.laptop_ip, self.port)

        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.selected_region = None # (x1, y1, x2, y2)

        self.original_image = None
        self.tk_image = None

        self.canvas = tk.Canvas(master, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.label_coords = tk.Label(master, text="Zaznacz region na obrazie.")
        self.label_coords.pack()

        self.button_refresh = tk.Button(master, text="Odśwież zrzut ekranu", command=self.load_screenshot)
        self.button_refresh.pack(side=tk.LEFT, padx=5, pady=5)

        self.button_confirm = tk.Button(master, text="Potwierdź wybór", command=self.confirm_selection)
        self.button_confirm.pack(side=tk.RIGHT, padx=5, pady=5)

        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.load_screenshot()

    def load_screenshot(self):
        tool_logger.warning("Pobieram zrzut ekranu z laptopa...")
        screenshot = self.remote_client.grab_screenshot_remote()
        if screenshot:
            self.original_image = screenshot
            self.tk_image = ImageTk.PhotoImage(self.original_image)
            
            self.canvas.delete("all")
            self.canvas.config(width=self.original_image.width, height=self.original_image.height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.master.geometry(f"{self.original_image.width}x{self.original_image.height + 60}") # Dopasuj rozmiar okna
            tool_logger.warning("Zrzut ekranu załadowany.")
            self.label_coords.config(text="Zaznacz region na obrazie.")
            self.selected_region = None
        else:
            messagebox.showerror("Błąd", "Nie udało się pobrać zrzutu ekranu z laptopa. Upewnij się, że serwer jest uruchomiony.")
            tool_logger.error("Nie udało się załadować zrzutu ekranu.")

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)
        self.selected_region = None

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        # Upewnij się, że x1 <= x2 i y1 <= y2
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        self.selected_region = (int(x1), int(y1), int(x2), int(y2))
        self.label_coords.config(text=f"Wybrany region: {self.selected_region}")
        tool_logger.warning(f"Wybrany region: {self.selected_region}")

    def confirm_selection(self):
        if self.selected_region:
            messagebox.showinfo("Potwierdzono", f"Wybrane współrzędne: {self.selected_region}\nMożesz ich użyć w locate(..., region={self.selected_region})")
            self.master.destroy() # Zamknij okno po potwierdzeniu
        else:
            messagebox.showwarning("Brak wyboru", "Proszę najpierw zaznaczyć region na obrazie.")

if __name__ == '__main__':
    # --- PRZYKŁAD UŻYCIA TEGO NARZĘDZIA ---
    LAPTOP_IP = '192.168.1.11'  # <--- ZMIEŃ NA RZECZYWISTY ADRES IP LAPTOPA
    PORT = 65432

    root = tk.Tk()
    app = RegionSelectorApp(root, LAPTOP_IP, PORT)
    root.mainloop()
