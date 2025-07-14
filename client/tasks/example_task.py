# client/tasks/example_task.py (dawniej tasks/example_task.py)
import random
from client.tasks.base_task import BaseTask

class ExampleTask(BaseTask):
    def __init__(self, bot):
        super().__init__(bot)
        self.counter = 0

    def run(self):
        self.counter += 1
        self.logger.warning(f"Wykonuję ExampleTask po raz {self.counter}.")
        
        roll = random.randint(1, 4)
        if roll == 1:
            self.logger.warning("ExampleTask: Zwracam True.")
            return True
        elif roll == 2:
            self.logger.warning("ExampleTask: Zwracam False.")
            return False
        elif roll == 3:
            self.logger.warning("ExampleTask: Zwracam pauzę na 20s.")
            return ('pause', 20)
        else:
            self.logger.warning("ExampleTask: Symulacja nawigacji do miasta.")
            self.location_manager.navigate_to_city()
            return True
