# client/managers/game_manager.py (dawniej managers/game_manager.py)
import os
import time

class GameManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.location_manager = bot.location_manager
        self.remote_client = bot.remote_client
        self.png_locator = bot.png_locator

        self.launcher_path = r"C:\Program Files (x86)\Call of Dragons\Launcher.exe"
        self.start_button_path = r"png/launcher/start.png"

        self.game_window_title = "Call of Dragons"
        self.launcher_window_title = "Launcher_COD"
        self.game_process_name = "CALLOFDRAGONS.exe"
        self.launcher_process_name = "Launcher.exe"

    def _is_process_running(self, process_name):
        return self.remote_client.is_process_running_remote(process_name)

    def _activate_window(self, window_title):
        return self.remote_client.activate_window_remote(window_title)

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
            try:
                self.remote_client.popen_remote([self.launcher_path])
                time.sleep(10)
                if not self.is_launcher_running():
                    self.logger.error("Nie udało się uruchomić launchera w wyznaczonym czasie.")
                    return False
            except Exception as e:
                self.logger.error(f"Nie udało się uruchomić launchera zdalnie: {e}")
                return False

        if not self.png_locator.find(self.start_button_path, perform_click=True):
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
            self.remote_client.run_command_remote(["taskkill", "/F", "/IM", self.game_process_name])
            return True
        except Exception as e:
            self.logger.error(f"Nie udało się zamknąć procesu gry zdalnie: {e}")
            return False
