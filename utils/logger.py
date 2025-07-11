# utils/logger.py
from datetime import datetime

class Logger:
    def __init__(self):
        self.filename = "bot.log"

    def _write_log(self, level, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def error(self, message):
        self._write_log("ERROR", message)

    def warning(self, message):
        self._write_log("WARNING", message)

if __name__ == '__main__':
    logger = Logger()
    logger.error("To jest przykładowy błąd.")
    logger.warning("To jest przykładowe ostrzeżenie.")
    print(f"Zapisano logi do pliku: {logger.filename}")
