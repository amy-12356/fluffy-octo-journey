import akshare as ak
import pandas as pd

def download_aapl_daily_price(start_date, end_date):
    """
    下载苹果股票(AAPL)的日线价格数据
    
    参数:
    start_date: 开始日期，格式为 'YYYY-MM-DD'
    end_date: 结束日期，格式为 'YYYY-MM-DD'
    
    返回:
    DataFrame: 包含日期、开盘价、最高价、最低价、收盘价、成交量等数据
    """
    print(f"正在下载苹果股票(AAPL)日线数据")
    
    # 使用 akshare 的美股日线接口（新浪财经数据源）
    # 苹果股票代码: AAPL
    # 注意：stock_us_daily 接口不支持日期范围参数，需下载全部数据后筛选
    df = ak.stock_us_daily(
        symbol="AAPL",
        adjust="qfq"  # 前复权
    )
    
    print(f"下载完成，原始数据共 {len(df)} 条")
    
    # 筛选指定日期范围的数据
    df['date'] = pd.to_datetime(df['date'])
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    df_filtered = df.loc[mask].copy()
    
    # 重置索引
    df_filtered = df_filtered.reset_index(drop=True)
    
    print(f"筛选后数据: {len(df_filtered)} 条")
    print(f"数据预览:\n{df_filtered.head()}")
    
    return df_filtered

def save_to_csv(df, filename):
    """
    将数据保存为CSV文件
    
    参数:
    df: 数据DataFrame
    filename: 保存的文件名
    """
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"数据已保存到: {filename}")

if __name__ == "__main__":
    # 用户指定的日期范围
    start_date = "2025-07-01"
    end_date = "2026-06-30"
    
    # 下载数据
    try:
        data = download_aapl_daily_price(start_date, end_date)
        
        # 保存到CSV文件
        filename = f"aapl_daily_{start_date.replace('-', '')}_{end_date.replace('-', '')}.csv"
        save_to_csv(data, filename)
        
        # 打印数据统计信息
        print("\n数据统计信息:")
        print(f"日期范围: {data['date'].min()} 至 {data['date'].max()}")
        print(f"平均收盘价: {data['close'].mean():.2f}")
        print(f"最高收盘价: {data['close'].max():.2f}")
        print(f"最低收盘价: {data['close'].min():.2f}")
        
    except Exception as e:
        print(f"下载失败: {e}")
