import os
import time
import threading
import multiprocessing
import shutil

from faker import Faker

# Search keywords
def search_keywords(files, keywords, queue, thread_id, multiprocess):  
    if multiprocess:
        results = {}
    else:
       results = queue  
        
    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                for keyword in keywords:
                    if keyword in content:
                        if keyword not in results:
                            results[keyword] = []
                        results[keyword].append(file)
        except Exception as e:
            print(f"Помилка в потоці {thread_id} при обробці файлу {file}: {e}")
    if multiprocess:
        queue.put(results)
 
        
# multithreaded
def multithreaded_search(files, keywords, num_threads=4):
    chunk_size = len(files) // num_threads
    threads = []
    results = {}
    multiprocess = False
    start_time = time.time()

    for i in range(num_threads):
        file_chunk = files[i * chunk_size:(i + 1) * chunk_size] if i < num_threads - 1 else files[i * chunk_size:]
        thread = threading.Thread(target=search_keywords, args=(file_chunk, keywords, results, i, multiprocess))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    print(f"Час виконання багатопотокової версії: {end_time - start_time:.2f} секунд")

    return results


# multiprocess
def multiprocess_search(files, keywords, num_processes=4):
    chunk_size = len(files) // num_processes
    processes = []
    queue = multiprocessing.Queue()
    multiprocess = True
    start_time = time.time()

    for i in range(num_processes):
        file_chunk = files[i * chunk_size:(i + 1) * chunk_size] if i < num_processes - 1 else files[i * chunk_size:]
        process = multiprocessing.Process(target=search_keywords, args=(file_chunk, keywords, queue, i, multiprocess))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    results = {}
    while not queue.empty():
        result = queue.get()
        for keyword, files in result.items():
            if keyword not in results:
                results[keyword] = []
            results[keyword].extend(files)

    end_time = time.time()
    print(f"Час виконання багатопроцесорної версії: {end_time - start_time:.2f} секунд")

    return results

# Faker
def faker_text(files, keywords):
    fake = Faker()
    for file_name in files:
        if not os.path.exists(file_name):
            with open(file_name, 'w', encoding='utf-8') as f:
                text = fake.text(max_nb_chars=200)  
                text += f" {fake.random_element(keywords)}"
                f.write(text)
    
# Main
if __name__ == "__main__":
    files = ["f1.txt", "f2.txt", "f3.txt", "f4.txt"] 
    keywords = ["computer", "systems"] 
    faker_text(files, keywords)
    
    columns = shutil.get_terminal_size().columns
    
    print("_" * columns)
    results = multithreaded_search(files, keywords)
    print("Результати пошуку multithreaded:", results)
    
    print("_" * columns)
    results = multiprocess_search(files, keywords)
    print("Результати пошуку multiprocess:", results)
    
    print("_" * columns)