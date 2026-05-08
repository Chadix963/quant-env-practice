import pandas as pd
import numpy as np
from timer_test import time_it

# ==========================================
# 1. 创建模拟数据集 (Dates & Symbols)
# ==========================================
print("正在生成模拟数据...")
# 生成 1000 个交易日
dates = pd.date_range(start='2020-01-01', periods=1000)
# 生成 50 只模拟股票代码
symbols = [f'TICKER_{i:02d}' for i in range(50)]

# 创建 MultiIndex (第一维度：date, 第二维度：symbol)
multi_idx = pd.MultiIndex.from_product([dates, symbols], names=['date', 'symbol'])

# 填入随机因子数据
df = pd.DataFrame(np.random.randn(len(multi_idx), 2), index=multi_idx, columns=['factor_A', 'factor_B'])

print(f"原始数据维度: {df.shape}")

# ==========================================
# 2. 模拟数据缺失 (删除 10% 的行)
# ==========================================
# 为了后续测试“向前填充(forward fill)”，我们需要制造一些空缺
drop_fraction = 0.1
drop_count = int(len(df) * drop_fraction)

# 随机选择要删除的行索引
np.random.seed(42) # 固定随机种子以保证每次结果一致
drop_indices = np.random.choice(len(df), size=drop_count, replace=False)

# 删掉这 10% 的数据，这就模拟了停牌或者缺失的数据点
df_missing = df.drop(df.index[drop_indices]).sort_index()

print(f"挖空后数据维度: {df_missing.shape}")
print("-" * 40)

# ==========================================
# 3. 准备待填充的包含 NaN 的数据
# ==========================================
# 重新对齐索引，把缺失的那 10% 用 NaN 暴露出来
df_to_fill = df_missing.reindex(multi_idx)
print(f"准备填充的数据维度: {df_to_fill.shape}，包含 NaN")
print("-" * 40)

# ==========================================
# 测试 1: 使用纯 for 循环进行向前填充 (Forward Fill)
# ==========================================
@time_it
def ffill_with_loop(df):
    # 拷贝一份数据，防止污染原数据
    df_filled = df.copy()
    
    # 提取唯一的股票代码
    symbols = df_filled.index.get_level_values('symbol').unique()
    
    # 遍历每只股票
    for sym in symbols:
        last_a, last_b = np.nan, np.nan
        
        # 提取这只股票的所有日期记录
        sub_df = df_filled.xs(sym, level='symbol', drop_level=False)
        
        # 遍历这只股票的每一天
        for idx in sub_df.index:
            # 填充因子 A
            if pd.isna(df_filled.loc[idx, 'factor_A']):
                df_filled.loc[idx, 'factor_A'] = last_a
            else:
                last_a = df_filled.loc[idx, 'factor_A']
                
            # 填充因子 B
            if pd.isna(df_filled.loc[idx, 'factor_B']):
                df_filled.loc[idx, 'factor_B'] = last_b
            else:
                last_b = df_filled.loc[idx, 'factor_B']
                
    return df_filled

# ==========================================
# 测试 2: 使用 groupby + apply (初级向量化，有 Python 层开销)
# ==========================================
@time_it
def ffill_with_apply(df):
    # 按股票分组，然后对每组应用 ffill。
    # group_keys=False 是为了防止索引错乱
    return df.groupby(level='symbol', group_keys=False).apply(lambda x: x.ffill())

# ==========================================
# 测试 3: 使用原生 groupby.ffill() (标准向量化，底层 C 语言优化)
# ==========================================
@time_it
def ffill_with_groupby(df):
    # Pandas 认识 ffill，所以不需要 apply 绕路，直接调底层 C 代码
    return df.groupby(level='symbol').ffill()

# ==========================================
# 测试 4: Unstack -> ffill -> Stack (高阶魔法：空间换时间)
# ==========================================
@time_it
def ffill_with_unstack(df):
    # 终极奥义：先把多重索引“拍平”成一张宽表 (横轴是股票，纵轴是时间)，
    # 然后进行极速二维填充，最后再“折叠”回原来的长表结构。
    return df.unstack(level='symbol').ffill().stack(level='symbol')

# ==========================================
# 一键运行所有 Benchmark
# ==========================================
print("\n" + "="*40)

print("\n[参赛者 1] 纯 For 循环 (请耐心等待...)")
df_result_1 = ffill_with_loop(df_to_fill)

print("\n[参赛者 2] Groupby + Apply")
df_result_2 = ffill_with_apply(df_to_fill)

print("\n[参赛者 3] 原生 Groupby FFill")
df_result_3 = ffill_with_groupby(df_to_fill)

print("\n[参赛者 4] Unstack -> FFill -> Stack")
df_result_4 = ffill_with_unstack(df_to_fill)

print("\n" + "="*40)