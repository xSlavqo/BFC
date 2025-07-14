# tools/region_selector_tool.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
# Poprawione importy, aby wskazywały na katalog shared
from shared.remote_control import RemoteClient
from shared.logger import Logger

class RegionSelectorApp:
    def __init__(self, master, laptop_ip, port):
        self.master = master
        master.title("Wybór Regionu Ekranu z Laptopa")

        # Inicjalizacja loggera i klienta
        self.logger = Logger(filename="region_selector_tool.log")
        self.remote_client = RemoteClient(laptop_ip, port)
        self.remote_client.set_logger(self.logger)

        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.selected_region = None

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
        self.logger.warning("Pobieram zrzut ekranu z laptopa...")
        screenshot = self.remote_client.grab_screenshot_remote()
        if screenshot:
            self.original_image = screenshot
            self.tk_image = ImageTk.PhotoImage(self.original_image)
            
            self.canvas.delete("all")
            self.canvas.config(width=self.original_image.width, height=self.original_image.height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.master.geometry(f"{self.original_image.width}x{self.original_image.height + 60}")
            self.logger.warning("Zrzut ekranu załadowany.")
            self.label_coords.config(text="Zaznacz region na obrazie.")
            self.selected_region = None
        else:
            messagebox.showerror("Błąd", "Nie udało się pobrać zrzutu ekranu z laptopa.")
            self.logger.error("Nie udało się załadować zrzutu ekranu.")

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_mouse_drag(self, event):
        cur_x, cur_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        x1 = min(self.start_x, self.canvas.canvasx(event.x))
        y1 = min(self.start_y, self.canvas.canvasy(event.y))
        x2 = max(self.start_x, self.canvas.canvasx(event.x))
        y2 = max(self.start_y, self.canvas.canvasy(event.y))
        self.selected_region = (int(x1), int(y1), int(x2), int(y2))
        self.label_coords.config(text=f"Wybrany region: {self.selected_region}")
        self.logger.warning(f"Wybrany region: {self.selected_region}")

    def confirm_selection(self):
        if self.selected_region:
            messagebox.showinfo("Potwierdzono", f"Wybrane współrzędne: {self.selected_region}")
            self.master.destroy()
        else:
            messagebox.showwarning("Brak wyboru", "Proszę najpierw zaznaczyć region.")

if __name__ == '__main__':
    LAPTOP_IP = '192.168.1.11'
    PORT = 65432
    root = tk.Tk()
    app = RegionSelectorApp(root, LAPTOP_IP, PORT)
    root.mainloop()
