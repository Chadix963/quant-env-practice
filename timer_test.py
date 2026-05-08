import time
from contexttimer import Timer

def time_it(func):
    """
    一个用于统计函数执行时间的装饰器
    """
    def wrapper(*args, **kwargs):
        # 使用 contexttimer 的 Timer 作为上下文管理器
        with Timer() as t:
            # 运行被包裹的函数
            result = func(*args, **kwargs)
        
        # 打印出函数名和耗时
        print(f"[{func.__name__}] 执行耗时: {t.elapsed:.4f} 秒")
        return result
    return wrapper

# 测试一下我们的装饰器
@time_it
def test_model_computation():
    print("开始模拟高频因子计算...")
    time.sleep(1.5)  # 模拟代码执行了 1.5 秒
    print("计算完成！")

if __name__ == "__main__":
    test_model_computation()