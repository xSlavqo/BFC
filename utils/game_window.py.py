# utils/game_window.py
import pygetwindow as gw
import time

class GameWindow:
    def __init__(self):
        self.window_title = 'Call of Dragons'
        self._window_obj = self._find_exact_window()
        
        if not self._window_obj:
            raise Exception(f"Nie znaleziono okna o dokładnym tytule: '{self.window_title}'")

    def _find_exact_window(self):
        all_windows = gw.getWindowsWithTitle(self.window_title)
        for window in all_windows:
            if window.title == self.window_title:
                return window
        return None

    @property
    def window(self):
        if self.window_title not in gw.getAllTitles():
            self._window_obj = self._find_exact_window()
            if not self._window_obj:
                raise Exception("Utracono połączenie z oknem gry.")
        return self._window_obj

    @property
    def x(self):
        return self.window.left

    @property
    def y(self):
        return self.window.top

    @property
    def width(self):
        return self.window.width

    @property
    def height(self):
        return self.window.height
