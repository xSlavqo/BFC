# tools/region_selector_tool.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import os

# Dodaje główny katalog projektu do ścieżki Pythona, aby znaleźć moduł 'shared'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.remote_control import RemoteClient
from shared.logger import Logger

class RegionSelectorApp:
    def __init__(self, master, laptop_ip, port):
        self.master = master
        master.title("Wybór Regionu Ekranu z Laptopa")

        self.logger = Logger(filename="region_selector_tool.log")
        self.remote_client = RemoteClient(laptop_ip, port)
        self.remote_client.set_logger(self.logger)

        self.start_x = None
        self.start_y = None
        self.current_rect_id = None
        self.selected_regions = []
        self.rect_ids = []

        self.original_image = None
        self.tk_image = None
        self.zoom_level = 1.0
        self.pan_start_x = 0
        self.pan_start_y = 0

        # Frame for canvas
        self.canvas_frame = tk.Frame(master)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, cursor="cross")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame for buttons
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(fill=tk.X, pady=5)

        self.label_coords = tk.Label(self.button_frame, text="Zaznacz region(y) na obrazie.")
        self.label_coords.pack(side=tk.LEFT, padx=5)

        self.button_refresh = tk.Button(self.button_frame, text="Odśwież", command=self.load_screenshot)
        self.button_refresh.pack(side=tk.LEFT, padx=5)

        self.button_clear = tk.Button(self.button_frame, text="Wyczyść zaznaczenie", command=self.clear_selections)
        self.button_clear.pack(side=tk.LEFT, padx=5)

        self.button_reset_zoom = tk.Button(self.button_frame, text="Resetuj widok", command=self.reset_view)
        self.button_reset_zoom.pack(side=tk.LEFT, padx=5)

        self.button_confirm = tk.Button(self.button_frame, text="Potwierdź", command=self.confirm_selection)
        self.button_confirm.pack(side=tk.RIGHT, padx=5)

        # Bindings
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel) # Windows
        self.canvas.bind("<Button-4>", self.on_mouse_wheel) # Linux
        self.canvas.bind("<Button-5>", self.on_mouse_wheel) # Linux
        self.canvas.bind("<Button-3>", self.on_pan_start) # Prawy przycisk myszy
        self.canvas.bind("<B3-Motion>", self.on_pan_move)

        self.load_screenshot()

    def load_screenshot(self):
        self.logger.warning("Pobieram zrzut ekranu z laptopa...")
        screenshot = self.remote_client.grab_screenshot_remote()
        if screenshot:
            self.original_image = screenshot
            self.master.geometry(f"{self.original_image.width}x{self.original_image.height + 60}")
            self.clear_selections()
            self.reset_view()
            self.logger.warning("Zrzut ekranu załadowany.")
        else:
            messagebox.showerror("Błąd", "Nie udało się pobrać zrzutu ekranu z laptopa.")
            self.logger.error("Nie udało się załadować zrzutu ekranu.")

    def update_canvas_image(self):
        if not self.original_image:
            return

        new_width = int(self.original_image.width * self.zoom_level)
        new_height = int(self.original_image.height * self.zoom_level)
        
        resized_image = self.original_image.resize((new_width, new_height), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized_image)

        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        
        self.redraw_rectangles()

    def redraw_rectangles(self):
        for rect_id in self.rect_ids:
            self.canvas.delete(rect_id)
        self.rect_ids.clear()
        
        for region in self.selected_regions:
            x1, y1, x2, y2 = region
            # Konwersja współrzędnych oryginalnego obrazu na współrzędne przybliżonego płótna
            zx1 = x1 * self.zoom_level
            zy1 = y1 * self.zoom_level
            zx2 = x2 * self.zoom_level
            zy2 = y2 * self.zoom_level
            rect_id = self.canvas.create_rectangle(zx1, zy1, zx2, zy2, outline="red", width=2)
            self.rect_ids.append(rect_id)

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x) / self.zoom_level
        self.start_y = self.canvas.canvasy(event.y) / self.zoom_level
        self.current_rect_id = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="blue", width=2, dash=(4, 2))

    def on_mouse_drag(self, event):
        if self.current_rect_id:
            cur_x, cur_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            start_x_canvas = self.start_x * self.zoom_level
            start_y_canvas = self.start_y * self.zoom_level
            self.canvas.coords(self.current_rect_id, start_x_canvas, start_y_canvas, cur_x, cur_y)

    def on_button_release(self, event):
        if self.current_rect_id:
            self.canvas.delete(self.current_rect_id)
            self.current_rect_id = None

            end_x = self.canvas.canvasx(event.x) / self.zoom_level
            end_y = self.canvas.canvasy(event.y) / self.zoom_level

            x1 = min(self.start_x, end_x)
            y1 = min(self.start_y, end_y)
            x2 = max(self.start_x, end_x)
            y2 = max(self.start_y, end_y)
            
            new_region = (int(x1), int(y1), int(x2), int(y2))
            self.selected_regions.append(new_region)
            self.logger.warning(f"Dodano nowy region: {new_region}")
            self.update_label()
            self.redraw_rectangles()

    def on_mouse_wheel(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if event.delta > 0 or event.num == 4:
            factor = 1.1
        elif event.delta < 0 or event.num == 5:
            factor = 1 / 1.1
        else:
            return

        new_zoom = max(0.1, min(self.zoom_level * factor, 5.0))

        if new_zoom == self.zoom_level:
            return

        old_zoom = self.zoom_level
        self.zoom_level = new_zoom
        
        self.update_canvas_image()

        # Przesunięcie widoku, aby punkt pod kursorem pozostał w tym samym miejscu
        self.canvas.xview_scroll(int((x * (self.zoom_level - old_zoom)) / old_zoom), "units")
        self.canvas.yview_scroll(int((y * (self.zoom_level - old_zoom)) / old_zoom), "units")


    def on_pan_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def on_pan_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def clear_selections(self):
        self.selected_regions.clear()
        for rect_id in self.rect_ids:
            self.canvas.delete(rect_id)
        self.rect_ids.clear()
        if self.current_rect_id:
            self.canvas.delete(self.current_rect_id)
            self.current_rect_id = None
        self.update_label()
        self.logger.warning("Wyczyszczono wszystkie zaznaczenia.")

    def reset_view(self):
        self.zoom_level = 1.0
        self.update_canvas_image()
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.logger.warning("Widok zresetowany.")

    def update_label(self):
        count = len(self.selected_regions)
        self.label_coords.config(text=f"Liczba zaznaczonych regionów: {count}")

    def confirm_selection(self):
        if self.selected_regions:
            regions_str = "\n".join([str(r) for r in self.selected_regions])
            # Zwracanie danych przez zamknięcie i opcjonalne zapisanie do pliku/konsoli
            print("Selected Regions:", regions_str) 
            messagebox.showinfo("Potwierdzono", f"Wybrane regiony:\n{regions_str}")
            self.master.destroy()
        else:
            messagebox.showwarning("Brak wyboru", "Proszę najpierw zaznaczyć przynajmniej jeden region.")

if __name__ == '__main__':
    LAPTOP_IP = '192.168.1.11' # Pamiętaj, aby ustawić prawidłowy adres IP
    PORT = 65432
    root = tk.Tk()
    app = RegionSelectorApp(root, LAPTOP_IP, PORT)
    root.mainloop()
