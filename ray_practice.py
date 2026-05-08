import pandas as pd
import numpy as np
import ray
import time
from timer_test import time_it

# 1. 初始化本地 Ray 集群
# num_cpus 指定使用的核心数
if not ray.is_initialized():
    ray.init(num_cpus=4)

# 2. 定义远程函数 (Remote Function)
@ray.remote
def process_day_data(date, day_df):
    """
    模拟对某一天全市场数据进行复杂的因子计算
    """
    # 模拟计算开销
    time.sleep(0.01) 
    result = day_df['factor_A'].mean()
    return (date, result)

# 3. 准备数据 (100天，每天500只股票)
print("正在准备数据...")
dates = pd.date_range(start='2023-01-01', periods=100)
symbols = [f'S_{i}' for i in range(500)]
idx = pd.MultiIndex.from_product([dates, symbols], names=['date', 'symbol'])
df = pd.DataFrame(np.random.randn(len(idx), 1), index=idx, columns=['factor_A']).reset_index()

@time_it
def run_with_ray(df):
    print("开始使用 Ray 按天并行计算...")
    # 将数据按天分组
    grouped = df.groupby('date')
    
    # 异步提交所有任务到 Ray 集群
    # .remote() 会立即返回一个 ObjectRef（期票），不会阻塞
    result_refs = [
        process_day_data.remote(date, group) 
        for date, group in grouped
    ]
    
    # 使用 ray.get() 统一回收结果（这里会发生阻塞，直到所有任务完成）
    results = ray.get(result_refs)
    return results

@time_it
def run_serial(df):
    print("开始串行计算...")
    results = []
    for date, group in df.groupby('date'):
        time.sleep(0.01)
        results.append((date, group['factor_A'].mean()))
    return results

if __name__ == "__main__":
    # 运行对比
    res_serial = run_serial(df)
    res_ray = run_with_ray(df)
    
    # 关闭 Ray
    ray.shutdown()