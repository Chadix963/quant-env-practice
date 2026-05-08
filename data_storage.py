import pandas as pd
import numpy as np
import os
from timer_test import time_it # 继续用我们的秒表

print("正在生成待存储的数据...")
# 我们重新生成一份数据，直接用最快的 ffill 跑出干净的结果
dates = pd.date_range(start='2020-01-01', periods=1000)
symbols = [f'TICKER_{i:02d}' for i in range(50)]
multi_idx = pd.MultiIndex.from_product([dates, symbols], names=['date', 'symbol'])
df = pd.DataFrame(np.random.randn(len(multi_idx), 2), index=multi_idx, columns=['factor_A', 'factor_B'])

# 模拟缺失并用原生向量化填充
drop_indices = np.random.choice(len(df), size=int(len(df) * 0.1), replace=False)
df_missing = df.drop(df.index[drop_indices]).sort_index()
df_final = df_missing.reindex(multi_idx).groupby(level='symbol').ffill()

# ==========================================
# 核心操作：为“分片 (Sharding)”做准备
# ==========================================
# 在存入数据库或 Parquet 时，通常要把 MultiIndex 释放成普通的列，
# 这样底层引擎才能按这些列进行切割。
df_to_save = df_final.reset_index()

# 创建一个存放数据的文件夹
os.makedirs('my_quant_data', exist_ok=True)

# ==========================================
# 1. 存为单一的二进制文件 (Single File)
# ==========================================
@time_it
def save_single_file():
    df_to_save.to_parquet('my_quant_data/all_data.parquet', engine='pyarrow')
    print("✅ 单一文件保存成功！")

# ==========================================
# 2. 按【日期】分片存储 (Sharded by date)
# ==========================================
@time_it
def save_sharded_by_date():
    # 为了避免产生 1000 个文件夹（每天一个），我们这里提取“年月”来进行分片存储，这在业界更常见
    df_to_save['year_month'] = df_to_save['date'].dt.strftime('%Y-%m')
    df_to_save.to_parquet('my_quant_data/sharded_by_date', engine='pyarrow', partition_cols=['year_month'])
    print("✅ 按月分片保存成功！")

# ==========================================
# 3. 按【股票代码】分片存储 (Sharded by symbol)
# ==========================================
@time_it
def save_sharded_by_symbol():
    df_to_save.to_parquet('my_quant_data/sharded_by_symbol', engine='pyarrow', partition_cols=['symbol'])
    print("✅ 按股票代码分片保存成功！")

if __name__ == "__main__":
    save_single_file()
    save_sharded_by_date()
    save_sharded_by_symbol()