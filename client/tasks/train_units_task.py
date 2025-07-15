# client/tasks/train_units_task.py
import time
from client.tasks.base_task import BaseTask

class TrainUnitsTask(BaseTask):
    def __init__(self, bot):
        super().__init__(bot)
        self.png_locator = bot.png_locator
        self.units_done_path = r"png/train/units_done"
        self.enter_training_path = r"png/train/enter_training"

    def _collect_and_enter_menu(self):
        location = self.png_locator.find(self.units_done_path, perform_click=False)
        if not location:
            return False

        center_x = location[0] + location[2] / 2
        center_y = location[1] + location[3] / 2
        click_x = center_x
        click_y = center_y + 40  # przesunięcie w dół o 40 pikseli
        
        self.bot.click(click_x, click_y)
        time.sleep(0.3)
        self.bot.click(click_x, click_y)

        if not self.png_locator.find(self.enter_training_path, perform_click=True):
            self.logger.error("Nie znaleziono przycisku wejścia do menu szkolenia.")
            return False
        time.sleep(1)
        return True

    def _start_training(self):
        if not self.png_locator.find(r"png\train\start_train.png", perform_click=True):
            self.logger.error("Nie znaleziono przycisku 'Start Training'.")
            return False
        time.sleep(1)  # Czekamy na reakcję gry po kliknięciu
        self.bot.remote_client.press_remote('esc')
        return True
        

        

    def run(self):
        if not self.location_manager.navigate_to_city():
            return False

        if self._collect_and_enter_menu():
            if not self._start_training():
                self.logger.error("Nie udało się rozpocząć nowego szkolenia.")
                self.location_manager.navigate_to_map()
                return False
        return True