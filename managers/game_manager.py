# managers/game_manager.py
import os
import subprocess
import time
import psutil
import pygetwindow as gw
from utils.locate import locate

class GameManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.location_manager = bot.location_manager
        
        self.launcher_path = r"C:\Program Files (x86)\Call of Dragons\Launcher.exe"
        self.start_button_path = r"png/launcher/start.png"
        self.game_window_title = "Call of Dragons"
        self.launcher_window_title = "Launcher_COD"
        self.game_process_name = "CALLOFDRAGONS.exe" 
        self.launcher_process_name = "Launcher.exe"

    def _is_process_running(self, process_name):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == process_name.lower():
                return True
        return False

    def _activate_window(self, window_title):
        try:
            window = gw.getWindowsWithTitle(window_title)[0]
            if window:
                if window.isMinimized:
                    window.restore()
                window.activate()
                time.sleep(1)
                return True
        except IndexError:
            self.logger.warning(f"Nie znaleziono okna o tytule '{window_title}'.")
        return False

    def is_game_running(self):
        if self._is_process_running(self.game_process_name):
            return self._activate_window(self.game_window_title)
        return False

    def is_launcher_running(self):
        if self._is_process_running(self.launcher_process_name):
            return self._activate_window(self.launcher_window_title)
        return False

    def ensure_game_running(self):
        if self.is_game_running():
            return True

        if not self.is_launcher_running():
            if not os.path.exists(self.launcher_path):
                self.logger.error(f"Ścieżka do launchera jest nieprawidłowa: {self.launcher_path}")
                return False
            try:
                subprocess.Popen([self.launcher_path])
                time.sleep(10)
                if not self.is_launcher_running():
                    self.logger.error("Nie udało się uruchomić launchera w wyznaczonym czasie.")
                    return False
            except Exception as e:
                self.logger.error(f"Nie udało się uruchomić launchera: {e}")
                return False

        if not locate(self.bot, self.start_button_path, perform_click=True):
            self.logger.error("Nie znaleziono przycisku 'Start' w launcherze lub nie udało się w niego kliknąć.")
            return False

        for _ in range(12):
            time.sleep(5)
            if self.is_game_running() and self.location_manager.is_in_city():
                return True
            
        self.logger.error("Nie udało się załadować widoku miasta w wyznaczonym czasie.")
        return False

    def close_game(self):
        if not self._is_process_running(self.game_process_name):
            return True

        try:
            subprocess.run(["taskkill", "/F", "/IM", self.game_process_name], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Nie udało się zamknąć procesu gry za pomocą taskkill: {e.output}")
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == self.game_process_name.lower():
                    proc.kill()
                    return True
        except Exception as e:
            self.logger.error(f"Wystąpił nieoczekiwany błąd podczas zamykania gry: {e}")
        
        return False
