import numpy as np
import pandas as pd
from multiprocessing import Pool
from loky import get_reusable_executor
from concurrent.futures import ThreadPoolExecutor
from timer_test import time_it
import time

# 模拟一个非常耗时的量化计算任务
def heavy_quant_task(data_chunk):
    # 模拟复杂的数学运算
    result = np.exp(data_chunk).rolling(window=10).mean() * np.sqrt(np.abs(data_chunk))
    return result

# 生成大规模数据 (100万行)
print("生成大规模模拟数据...")
data = pd.Series(np.random.randn(1000000))
# 将数据切成 10 份，准备发给不同核心
chunks = [data.iloc[i:i+100000] for i in range(0, 1000000, 100000)]

@time_it
def run_serial():
    print("开始串行计算...")
    return [heavy_quant_task(c) for c in chunks]

@time_it
def run_threads():
    print("开始多线程计算 (Threading)...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(heavy_quant_task, chunks))

@time_it
def run_multiprocessing():
    print("开始多进程计算 (Multiprocessing)...")
    with Pool(processes=4) as pool:
        return pool.map(heavy_quant_task, chunks)

@time_it
def run_loky():
    print("开始 Loky 并行计算...")
    executor = get_reusable_executor(max_workers=4)
    return list(executor.map(heavy_quant_task, chunks))

if __name__ == "__main__":
    run_serial()
    run_threads()
    run_multiprocessing()
    run_loky()