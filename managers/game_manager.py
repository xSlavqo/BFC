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

    def is_game_running(self):
        return self._is_process_running(self.game_process_name)

    def is_launcher_running(self):
        return self._is_process_running(self.launcher_process_name)

    def ensure_game_running(self):
        if self.location_manager.is_in_city():
            try:
                game_window = gw.getWindowsWithTitle(self.game_window_title)[0]
                if game_window:
                    if game_window.isMinimized:
                        game_window.restore()
                    game_window.activate()
                return True
            except IndexError:
                return False

        if not self.is_launcher_running():
            if not os.path.exists(self.launcher_path):
                self.logger.error(f"Ścieżka do launchera jest nieprawidłowa: {self.launcher_path}")
                return False
            try:
                subprocess.Popen([self.launcher_path])
                time.sleep(10)
            except Exception as e:
                self.logger.error(f"Nie udało się uruchomić launchera: {e}")
                return False

        if not locate(self.bot, self.start_button_path, threshold=0.8, perform_click=True):
            self.logger.error("Nie znaleziono przycisku 'Start' w launcherze lub nie udało się w niego kliknąć.")
            return False

        for _ in range(12):
            if self.location_manager.is_in_city():
                time.sleep(2)
                return True
            time.sleep(5)
            
        self.logger.error("Nie udało się załadować widoku miasta w wyznaczonym czasie.")
        return False

    def close_game(self):
        if not self.is_game_running():
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
