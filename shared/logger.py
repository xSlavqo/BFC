# shared/logger.py (dawniej utils/logger.py)
from datetime import datetime

class Logger:
    def __init__(self, filename="bot.log"):
        self.filename = filename

    def _write_log(self, level, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Wypisanie na konsolę
        print(log_entry.strip())
        
        # Zapis do pliku
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def error(self, message):
        self._write_log("ERROR", message)

    def warning(self, message):
        self._write_log("WARNING", message)
