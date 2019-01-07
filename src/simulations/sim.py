import threading
import time
import numpy as np
import random


# One sim runs multiple models at the same time
class Sim:
    def __init__(self):
        self.status = []
        random.seed(42)
        self.threads = []
        self.models_added = 0
        self.models_finished = 0
        self.max_threads = 0

    def __run_model(self, model, sim, iterations):
        for i in range(1, iterations):
            if (i + 1) % 200 == 0:
                self.status[sim] = f"[{sim}]: {i+1}/{iterations}"
            model.tick(i)
        self.status[sim] = f"[{sim}]: finished"

    def dispatch_thread(self, key, model, iterations):
        self.threads[key] = threading.Thread(target=self.__run_model, args=(model, key, iterations,))
        self.threads[key].start()
        self.models_added += 1

    def run(self, models, iterations):
        t_start = time.time()
        models_to_add = len(models)
        if self.max_threads != 0 and models_to_add > self.max_threads:
            models_to_add = self.max_threads
        self.threads = np.empty(models_to_add, dtype=threading.Thread)
        self.status = [""] * models_to_add

        print("Setting up threads")
        for i in range(models_to_add):
            self.dispatch_thread(i, models[self.models_added], iterations)

        is_one_alive = True
        finished_threads = 0
        while is_one_alive:
            out = ""
            for key, thread in enumerate(self.threads):
                if not thread.isAlive():
                    if self.models_added < len(models):
                        self.dispatch_thread(key, models[self.models_added], iterations)
                    else:
                        finished_threads += 1
                        if finished_threads == len(models):
                            is_one_alive = False
                out += self.status[key] + " | "
            print("\r" + out, end="", flush=True)

        print("\nSimulation took:", time.time() - t_start, "s")
