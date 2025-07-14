# client/tasks/base_task.py (dawniej tasks/base_task.py)
class BaseTask:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.location_manager = bot.location_manager
        self.game_manager = bot.game_manager
        self.ocr_manager = bot.ocr_manager

    def run(self):
        raise NotImplementedError("Ta metoda musi zostać zaimplementowana w klasie dziedziczącej.")
