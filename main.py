import time
import psutil
import os
import random

def send_frame(frame, seq_num):
    if random.random() > 0.9:
        return False
    return True

def receive_ack(seq_num):
    if random.random() > 0.9:
        return None
    return seq_num

def send_frame_with_retransmission(frame, seq_num, retransmissions):
    success = False
    while not success:
        if send_frame(frame, seq_num):
            ack = receive_ack(seq_num)
            if ack == seq_num:
                success = True
            else:
                retransmissions[0] += 1
        else:
            retransmissions[0] += 1

def sliding_window(frames, window_size):
    retransmissions = [0]
    delays = []
    start_time = time.time()

    for i in range(0, len(frames), window_size):
        window = frames[i:i + window_size]
        for j, frame in enumerate(window):
            seq_num = i + j
            frame_start_time = time.time()
            send_frame_with_retransmission(frame, seq_num, retransmissions)
            frame_end_time = time.time()
            delays.append(frame_end_time - frame_start_time)

    end_time = time.time()
    execution_time = end_time - start_time

    total_data_transmitted = len(frames)
    throughput = total_data_transmitted / execution_time
    average_delay = sum(delays) / len(delays)

    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / (1024 * 1024)  # MiB

    error_packets = retransmissions[0]
    error_rate = error_packets / total_data_transmitted

    return execution_time, memory_usage, throughput, retransmissions[0], error_rate, average_delay

def go_back_n(frames, window_size):
    retransmissions = [0]
    delays = []
    start_time = time.time()

    base = 0
    next_seq_num = 0
    while base < len(frames):
        window_end = min(next_seq_num, len(frames))
        for i in range(base, window_end):
            seq_num = i
            frame_start_time = time.time()
            send_frame_with_retransmission(frames[i], seq_num, retransmissions)
            frame_end_time = time.time()
            delays.append(frame_end_time - frame_start_time)
            base += 1

        base = next_seq_num
        next_seq_num = min(base + window_size, len(frames))

    end_time = time.time()
    execution_time = end_time - start_time

    total_data_transmitted = len(frames)
    throughput = total_data_transmitted / execution_time
    average_delay = sum(delays) / len(delays)

    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / (1024 * 1024)  # MiB

    error_packets = retransmissions[0]
    error_rate = error_packets / total_data_transmitted

    return execution_time, memory_usage, throughput, retransmissions[0], error_rate, average_delay

def run_experiment(experiment_count, frames, window_size):
    sliding_window_results = {
        'execution_time': [],
        'memory_usage': [],
        'throughput': [],
        'retransmissions': [],
        'error_rate': [],
        'average_delay': []
    }
    
    go_back_n_results = {
        'execution_time': [],
        'memory_usage': [],
        'throughput': [],
        'retransmissions': [],
        'error_rate': [],
        'average_delay': []
    }

    for _ in range(experiment_count):
        sw_results = sliding_window(frames, window_size)
        gbn_results = go_back_n(frames, window_size)
        
        sliding_window_results['execution_time'].append(sw_results[0])
        sliding_window_results['memory_usage'].append(sw_results[1])
        sliding_window_results['throughput'].append(sw_results[2])
        sliding_window_results['retransmissions'].append(sw_results[3])
        sliding_window_results['error_rate'].append(sw_results[4])
        sliding_window_results['average_delay'].append(sw_results[5])

        go_back_n_results['execution_time'].append(gbn_results[0])
        go_back_n_results['memory_usage'].append(gbn_results[1])
        go_back_n_results['throughput'].append(gbn_results[2])
        go_back_n_results['retransmissions'].append(gbn_results[3])
        go_back_n_results['error_rate'].append(gbn_results[4])
        go_back_n_results['average_delay'].append(gbn_results[5])

    def calculate_mean(results):
        return {
            'execution_time': sum(results['execution_time']) / len(results['execution_time']),
            'memory_usage': sum(results['memory_usage']) / len(results['memory_usage']),
            'throughput': sum(results['throughput']) / len(results['throughput']),
            'retransmissions': sum(results['retransmissions']) / len(results['retransmissions']),
            'error_rate': sum(results['error_rate']) / len(results['error_rate']),
            'average_delay': sum(results['average_delay']) / len(results['average_delay'])
        }

    sw_mean = calculate_mean(sliding_window_results)
    gbn_mean = calculate_mean(go_back_n_results)

    print("\n--- Resultados Médios Sliding Window ---")
    print(f"Tempo de execução: {sw_mean['execution_time']:.6f} segundos")
    print(f"Uso de memória: {sw_mean['memory_usage']:.2f} MiB")
    print(f"Throughput: {sw_mean['throughput']:.2f} pacotes/segundo")
    print(f"Número de retransmissões: {sw_mean['retransmissions']:.2f}")
    print(f"Taxa de erro: {sw_mean['error_rate']:.2%}")
    print(f"Atraso médio: {sw_mean['average_delay']:.6f} segundos")

    print("\n--- Resultados Médios Go-Back-N ---")
    print(f"Tempo de execução: {gbn_mean['execution_time']:.6f} segundos")
    print(f"Uso de memória: {gbn_mean['memory_usage']:.2f} MiB")
    print(f"Throughput: {gbn_mean['throughput']:.2f} pacotes/segundo")
    print(f"Número de retransmissões: {gbn_mean['retransmissions']:.2f}")
    print(f"Taxa de erro: {gbn_mean['error_rate']:.2%}")
    print(f"Atraso médio: {gbn_mean['average_delay']:.6f} segundos")

# Parâmetros do experimento
num_experiments = 30
frames = ["Frame 1", "Frame 2", "Frame 3", "Frame 4", "Frame 5"]
window_size = 3

run_experiment(num_experiments, frames, window_size)
