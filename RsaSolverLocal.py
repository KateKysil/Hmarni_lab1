import time
import random
from multiprocessing import Pool

def rsa_encrypt_chunk(args):
    """Функція шифрування порції даних (виконується у окремому процесі)."""
    e, n, chunk = args
    return [pow(m, e, n) for m in chunk]

def run_benchmark():
    total_elements = 100000
    e = 65537
    n = 32333
    
    # 1. Генерація даних (ідентична до тесту у PARCS)
    random.seed(42)
    data = [random.randint(2, 3000) for _ in range(total_elements)]
    
    print("=== Локальне паралельне тестування RSA (multiprocessing) ===\n")
    
    # 2. Послідовне тестування для N = 1, 2, 3, 4 процесів
    for num_workers in [1, 2, 3, 4]:
        chunk_size = total_elements // num_workers
        chunks = []
        
        # Розбиття на частини (Map phase)
        for i in range(num_workers):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i < num_workers - 1 else total_elements
            chunks.append((e, n, data[start:end]))
        
        start_time = time.time()
        
        # Паралельне виконання в локальному пулі процесів
        with Pool(processes=num_workers) as pool:
            results = pool.map(rsa_encrypt_chunk, chunks)
            
        # Збір результатів (Reduce phase)
        encrypted_data = []
        for res in results:
            encrypted_data.extend(res)
            
        execution_time = time.time() - start_time
        print(f"Workers: {num_workers} | Processed: {len(encrypted_data)} | Execution time: {execution_time:.3f} s")

if __name__ == '__main__':
    run_benchmark()