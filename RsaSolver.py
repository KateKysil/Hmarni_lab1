import time
import random
from Pyro4 import expose

class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers if workers else []

    def solve(self):
        print("RSA Job Started")
        print("Workers count: %d" % len(self.workers))
        
        # 1. Читаємо кількість елементів з вхідного файлу
        total_elements = self.read_input()
        
        # 2. Параметри RSA
        e = 65537
        n = 32333
        
        # Генерація даних
        random.seed(42)
        data = [random.randint(2, 3000) for _ in range(total_elements)]
        
        num_workers = len(self.workers) if len(self.workers) > 0 else 1
        step = total_elements // num_workers
        
        start_time = time.time()
        
        # MAP PHASE: розсилка фрагментів масиву на воркери
        mapped = []
        for i in range(num_workers):
            start_idx = i * step
            end_idx = (i + 1) * step if i < num_workers - 1 else total_elements
            chunk = data[start_idx:end_idx]
            mapped.append(self.workers[i].mymap(e, n, chunk))
            
        print("Map dispatched to %d workers..." % num_workers)
        
        # REDUCE PHASE: збір результатів через Pyro-проксі (.value)
        reduced = self.myreduce(mapped)
        
        execution_time = time.time() - start_time
        print("RSA Execution finished in {:.3f} s. Processed items: {}".format(execution_time, len(reduced)))
        
        # Запис результату
        self.write_output("Processed: {}\nExecution time: {:.3f} s".format(len(reduced), execution_time))
        print("RSA Job Finished")

    @staticmethod
    @expose
    def mymap(e, n, chunk):
        return [pow(m, e, n) for m in chunk]

    @staticmethod
    @expose
    def myreduce(mapped):
        output = []
        for x in mapped:
            res = x.value if hasattr(x, 'value') else x
            if isinstance(res, list):
                output.extend(res)
        return output

    def read_input(self):
        with open(self.input_file_name, 'r') as f:
            line = f.readline().strip()
            return int(line) if line else 150000

    def write_output(self, output):
        with open(self.output_file_name, 'w') as f:
            f.write(str(output) + '\n')