# tasks/example_task.py
import random
from tasks.base_task import BaseTask

class ExampleTask(BaseTask):
    def __init__(self, bot):
        super().__init__(bot)
        self.counter = 0

    def run(self):
        self.counter += 1
        self.logger.warning(f"Wykonuję ExampleTask po raz {self.counter}.")
        
        roll = random.randint(1, 4)
        if roll == 1:
            return True
        elif roll == 2:
            return False
        elif roll == 3:
            return ('pause', 20)
        else:
            self.logger.warning("ExampleTask: Symulacja nawigacji do miasta.")
            self.location_manager.navigate_to_city()
            return True