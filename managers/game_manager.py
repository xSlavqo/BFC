# managers/game_manager.py (na głównym PC - ZMODYFIKOWANY)
import os
import time
# Usunięto importy psutil, subprocess, pygetwindow, bo będą obsługiwane zdalnie
# import psutil
# import subprocess
# import pygetwindow as gw
from utils.locate import locate # locate będzie teraz używać remote_client

class GameManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.location_manager = bot.location_manager
        self.remote_client = bot.remote_client # Dostęp do klienta zdalnego sterowania
        
        # Ścieżka do launchera na LAPTOPIE
        self.launcher_path = r"C:\Program Files (x86)\Call of Dragons\Launcher.exe"
        # Ścieżka do obrazu przycisku Start na GŁÓWNYM PC (dla locate)
        self.start_button_path = r"png/launcher/start.png" 
        
        self.game_window_title = "Call of Dragons"
        self.launcher_window_title = "Launcher_COD"
        self.game_process_name = "CALLOFDRAGONS.exe" 
        self.launcher_process_name = "Launcher.exe"

    def _is_process_running(self, process_name):
        """Sprawdza, czy proces jest uruchomiony na zdalnym komputerze."""
        return self.remote_client.is_process_running_remote(process_name)

    def _activate_window(self, window_title):
        """Aktywuje okno na zdalnym komputerze."""
        return self.remote_client.activate_window_remote(window_title)

    def is_game_running(self):
        """Sprawdza, czy gra działa i aktywuje jej okno na zdalnym komputerze."""
        if self._is_process_running(self.game_process_name):
            return self._activate_window(self.game_window_title)
        return False

    def is_launcher_running(self):
        """Sprawdza, czy launcher działa i aktywuje jego okno na zdalnym komputerze."""
        if self._is_process_running(self.launcher_process_name):
            return self._activate_window(self.launcher_window_title)
        return False

    def ensure_game_running(self):
        """
        Zapewnia, że gra jest uruchomiona i widoczny jest widok miasta.
        Wszystkie operacje są wykonywane zdalnie.
        """
        self.logger.warning("Sprawdzam, czy gra jest uruchomiona...")
        if self.is_game_running():
            self.logger.warning("Gra już działa.")
            # Sprawdź, czy jesteśmy w mieście po uruchomieniu gry
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
            # Uruchomienie launchera zdalnie
            if not os.path.exists(self.launcher_path):
                self.logger.error(f"Ścieżka do launchera jest nieprawidłowa na laptopie: {self.launcher_path}")
                return False
            try:
                # Użyj remote_client do uruchomienia procesu na laptopie
                self.remote_client.popen_remote([self.launcher_path])
                self.logger.warning(f"Wysłano komendę uruchomienia launchera: {self.launcher_path}. Czekam 10 sekund...")
                time.sleep(10) # Daj czas na uruchomienie launchera
                if not self.is_launcher_running():
                    self.logger.error("Nie udało się uruchomić launchera w wyznaczonym czasie.")
                    return False
            except Exception as e:
                self.logger.error(f"Nie udało się uruchomić launchera zdalnie: {e}")
                return False
        else:
            self.logger.warning("Launcher już działa.")

        self.logger.warning("Szukam przycisku 'Start' w launcherze...")
        # locate teraz pobiera zrzut ekranu zdalnie i analizuje lokalnie
        if not locate(self.bot, self.start_button_path, perform_click=True):
            self.logger.error("Nie znaleziono przycisku 'Start' w launcherze lub nie udało się w niego kliknąć.")
            return False

        self.logger.warning("Kliknięto 'Start'. Czekam na uruchomienie gry i widok miasta (max 60 sekund)...")
        for _ in range(12): # 12 prób * 5 sekund = 60 sekund
            time.sleep(5)
            if self.is_game_running() and self.location_manager.is_in_city():
                self.logger.warning("Gra uruchomiona i widok miasta załadowany.")
                return True
            
        self.logger.error("Nie udało się załadować widoku miasta w wyznaczonym czasie.")
        return False

    def close_game(self):
        """Zamyka proces gry na zdalnym komputerze."""
        if not self._is_process_running(self.game_process_name):
            self.logger.warning("Proces gry nie działa, nie ma potrzeby zamykania.")
            return True

        self.logger.warning(f"Próbuję zamknąć proces gry '{self.game_process_name}' na laptopie.")
        try:
            # Użyj remote_client do wykonania taskkill na laptopie
            self.remote_client.run_command_remote(["taskkill", "/F", "/IM", self.game_process_name])
            self.logger.warning("Proces gry został pomyślnie zamknięty.")
            return True
        except Exception as e:
            self.logger.error(f"Nie udało się zamknąć procesu gry zdalnie za pomocą taskkill: {e}")
            # Opcjonalnie: możesz dodać tutaj logikę do zabicia procesu przez psutil na laptopie,
            # jeśli taskkill zawiedzie, ale wymagałoby to kolejnej komendy do serwera.
        
        return False