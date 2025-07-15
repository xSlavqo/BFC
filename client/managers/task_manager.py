# client/managers/task_manager.py
import time
from client.tasks.build_city_task import BuildCityTask
from client.tasks.example_task import ExampleTask
from client.tasks.train_units_task import TrainUnitsTask

class TaskManager:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.tasks = []
        self.disabled_tasks = set()
        self.running = False

    def _initialize_tasks(self):
        self.tasks = [
            {
                "name": "build_city",
                "task_object": BuildCityTask(self.bot),
                "interval": 120, # Uruchom niemal od razu po poprzednim
                "last_run": 0,
                "retries_on_fail": 0,
                "paused_until": 0
            },
            {
                "name": "train_units",
                "task_object": TrainUnitsTask(self.bot),
                "interval": 30, # Co 30 sekund
                "last_run": 0,
                "retries_on_fail": 0,
                "paused_until": 0
            },
            # Możesz dodać więcej zadań, np. ExampleTask
            # {
            #     "name": "example_task",
            #     "task_object": ExampleTask(self.bot),
            #     "interval": 60, # Co 60 sekund
            #     "last_run": 0,
            #     "retries_on_fail": 0,
            #     "paused_until": 0
            # },
        ]
        self.logger.warning("Zadania zostały zainicjowane.")

    def start(self):
        self.running = True
        self.logger.warning("Task Manager został uruchomiony.")
        self._initialize_tasks()
        self._run_loop()

    def stop(self):
        self.running = False
        self.logger.warning("Task Manager został zatrzymany.")

    def _is_task_ready(self, task_def, now):
        is_disabled = task_def["name"] in self.disabled_tasks
        is_paused = now < task_def.get("paused_until", 0)
        interval_passed = (now - task_def.get("last_run", 0)) >= task_def.get("interval", 0)
        return not is_disabled and not is_paused and interval_passed

    def _handle_result(self, task_def, result, now):
        task_name = task_def["name"]
        if result is True:
            self.logger.warning(f"Zadanie '{task_name}' zakończone pomyślnie.")
            task_def['last_run'] = now
            task_def['retries_on_fail'] = 0
        elif isinstance(result, tuple) and result[0] == 'pause':
            pause_duration = result[1]
            task_def['paused_until'] = now + pause_duration
            task_def['last_run'] = now
            self.logger.warning(f"Zadanie '{task_name}' wstrzymane na {pause_duration} sekund.")
        elif result is False:
            task_def['retries_on_fail'] += 1
            if task_def['retries_on_fail'] == 1:
                self.logger.warning(f"Zadanie '{task_name}' zawiodło. Próba restartu gry i ponowienia zadania.")
                if self.bot.game_manager.close_game():
                    self.logger.warning("Gra została zamknięta. Czekam 10 sekund przed ponowieniem.")
                    time.sleep(10)
                else:
                    self.logger.error("Nie udało się zamknąć gry. Zadanie zostanie wyłączone.")
                    self.disabled_tasks.add(task_name)
            else:
                self.logger.error(f"Zadanie '{task_name}' ponownie zawiodło po restarcie. Wyłączam.")
                self.disabled_tasks.add(task_name)

    def _execute_task(self, task_def, now):
        task_object = task_def["task_object"]
        task_name = task_def["name"]
        try:
            self.logger.warning(f"Rozpoczynam zadanie: {task_name}")
            result = task_object.run()
            self._handle_result(task_def, result, now)
        except Exception as e:
            self.logger.error(f"Krytyczny błąd w zadaniu '{task_name}': {e}")
            self.disabled_tasks.add(task_name)

    def _run_loop(self):
        while self.running:
            now = time.time()
            task_to_run = next((task for task in self.tasks if self._is_task_ready(task, now)), None)

            if task_to_run:
                self.logger.warning("Sprawdzanie stanu gry przed uruchomieniem zadania...")
                if not self.bot.game_manager.ensure_game_running():
                    self.logger.error("Nie udało się uruchomić gry. Wstrzymuję zadania na 60 sekund.")
                    time.sleep(60)
                    continue
                
                self._execute_task(task_to_run, now)
            
            time.sleep(1)