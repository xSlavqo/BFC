# managers/game_manager.py (na głównym PC - ZMODYFIKOWANY)
import os
import time
from utils.locate import Locator # Zmiana importu

class GameManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.location_manager = bot.location_manager
        self.remote_client = bot.remote_client
        self.locator = bot.locator # Dostęp do instancji Locator'a

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
        self.logger.warning("Sprawdzam, czy gra jest uruchomiona...")
        if self.is_game_running():
            self.logger.warning("Gra już działa.")
            if self.location_manager.is_in_city():
                self.logger.warning("Gra działa i jesteśmy w mieście.")
                return True
            else:
                self.logger.warning("Gra działa, ale nie jesteśmy w mieście. Próbuję nawigować.")
                if self.location_manager.navigate_to_city():
                    return True
                else:
                    self.logger.error("Nie udało się nawigować do miasta po uruchomieniu gry.")
                    return False

        self.logger.warning("Gra nie działa. Sprawdzam launcher...")
        if not self.is_launcher_running():
            self.logger.warning("Launcher nie działa. Próbuję uruchomić launcher...")
            if not os.path.exists(self.launcher_path):
                self.logger.error(f"Ścieżka do launchera jest nieprawidłowa na laptopie: {self.launcher_path}")
                return False
            try:
                self.remote_client.popen_remote([self.launcher_path])
                self.logger.warning(f"Wysłano komendę uruchomienia launchera: {self.launcher_path}. Czekam 10 sekund...")
                time.sleep(10)
                if not self.is_launcher_running():
                    self.logger.error("Nie udało się uruchomić launchera w wyznaczonym czasie.")
                    return False
            except Exception as e:
                self.logger.error(f"Nie udało się uruchomić launchera zdalnie: {e}")
                return False
        else:
            self.logger.warning("Launcher już działa.")

        self.logger.warning("Szukam przycisku 'Start' w launcherze...")
        # Użycie locator.find
        if not self.locator.find(self.start_button_path, perform_click=True):
            self.logger.error("Nie znaleziono przycisku 'Start' w launcherze lub nie udało się w niego kliknąć.")
            return False

        self.logger.warning("Kliknięto 'Start'. Czekam na uruchomienie gry i widok miasta (max 60 sekund)...")
        for _ in range(12):
            time.sleep(5)
            if self.is_game_running() and self.location_manager.is_in_city():
                self.logger.warning("Gra uruchomiona i widok miasta załadowany.")
                return True

        self.logger.error("Nie udało się załadować widoku miasta w wyznaczonym czasie.")
        return False

    def close_game(self):
        if not self._is_process_running(self.game_process_name):
            self.logger.warning("Proces gry nie działa, nie ma potrzeby zamykania.")
            return True

        self.logger.warning(f"Próbuję zamknąć proces gry '{self.game_process_name}' na laptopie.")
        try:
            self.remote_client.run_command_remote(["taskkill", "/F", "/IM", self.game_process_name])
            self.logger.warning("Proces gry został pomyślnie zamknięty.")
            return True
        except Exception as e:
            self.logger.error(f"Nie udało się zamknąć procesu gry zdalnie za pomocą taskkill: {e}")
        return False