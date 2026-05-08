from prefect import task, flow
import time
import random

# ==========================================
# 1. 定义原子任务 (@task)
# ==========================================

@task(name="下载全市场日线数据", retries=2, retry_delay_seconds=1)
def download_data():
    print("\n[任务 1] 📥 正在连接交易所 API 下载数据...")
    time.sleep(1.5)
    
    # 我们加个小彩蛋：模拟 20% 的概率网络下载失败
    if random.random() < 0.2:
        raise ConnectionError("网络抖动，下载失败！(不用担心，调度器会自动重试)")
        
    print("[任务 1] ✅ 数据下载完成！文件: raw_data.csv")
    return "raw_data.csv"

@task(name="计算动量因子")
def calc_momentum(data_path):
    print(f"\n[任务 2] 📈 读取 {data_path}，开始向量化计算动量因子...")
    time.sleep(1)
    print("[任务 2] ✅ 动量因子计算完毕！")
    return "momentum_factor"

@task(name="计算波动率因子")
def calc_volatility(data_path):
    print(f"\n[任务 3] 📉 读取 {data_path}，开始计算波动率因子...")
    time.sleep(1)
    print("[任务 3] ✅ 波动率因子计算完毕！")
    return "volatility_factor"

@task(name="生成最终交易信号")
def generate_signals(mom_data, vol_data):
    print(f"\n[任务 4] 🎯 正在聚合 {mom_data} 和 {vol_data}...")
    time.sleep(0.5)
    print("[任务 4] 🚀 今日交易信号生成完毕，准备推送到交易柜台！")
    return "final_signals.csv"


# ==========================================
# 2. 定义调度流水线与依赖关系 (@flow)
# ==========================================

@flow(name="Daily_Quant_Pipeline")
def daily_quant_pipeline():
    print("========== ⏱️ 量化流水线启动 ==========")
    
    # 依赖声明：Prefect 会自动根据输入输出参数识别 DAG 依赖！
    # 比如：calc_momentum 必须要等 download_data 返回结果后才会执行
    
    data = download_data()
    
    # 这两个任务会自动发现它们都依赖 data，且彼此互不依赖，
    # 在高级配置下它们会自动并行运行。
    mom = calc_momentum(data)
    vol = calc_volatility(data)
    
    # 必须等 mom 和 vol 都计算完，才能生成信号
    generate_signals(mom, vol)
    
    print("\n========== 🎉 流水线全部顺利结束 ==========")

if __name__ == "__main__":
    # 执行流水线
    daily_quant_pipeline()