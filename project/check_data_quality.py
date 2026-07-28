import pandas as pd
import numpy as np
from datetime import datetime

def load_data(file_path):
    """加载股票数据CSV文件"""
    try:
        df = pd.read_csv(file_path)
        # 将日期列转换为datetime格式
        df['date'] = pd.to_datetime(df['date'])
        print(f"✓ 成功加载数据: {file_path}")
        return df
    except Exception as e:
        print(f"✗ 加载数据失败: {e}")
        return None

def check_data_shape(df):
    """检查数据形状（行数、列数）"""
    print("\n" + "="*50)
    print("【数据形状检查】")
    print("="*50)
    rows, cols = df.shape
    print(f"总记录数: {rows}")
    print(f"总列数: {cols}")
    print(f"列名: {list(df.columns)}")
    
    # 日期范围
    min_date = df['date'].min()
    max_date = df['date'].max()
    print(f"日期范围: {min_date.date()} 至 {max_date.date()}")
    
    # 计算预期交易日数（排除周末）
    expected_days = np.busday_count(min_date.date(), max_date.date()) + 1
    print(f"预期交易日数: {expected_days}")
    print(f"实际交易日数: {rows}")
    print(f"缺失交易日数: {expected_days - rows}")
    
    return rows, cols, min_date, max_date

def check_missing_values(df):
    """检查缺失值"""
    print("\n" + "="*50)
    print("【缺失值检查】")
    print("="*50)
    
    # 每列的缺失值数量和比例
    missing_count = df.isnull().sum()
    missing_ratio = (df.isnull().sum() / len(df)) * 100
    
    missing_df = pd.DataFrame({
        '缺失数量': missing_count,
        '缺失比例(%)': missing_ratio.round(2)
    })
    
    print(missing_df)
    
    # 检查是否有完全缺失的行
    fully_missing_rows = df[df.isnull().all(axis=1)]
    if len(fully_missing_rows) > 0:
        print(f"\n✗ 发现 {len(fully_missing_rows)} 行完全缺失")
    else:
        print("\n✓ 没有完全缺失的行")
    
    # 检查关键列是否有缺失
    critical_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in critical_cols:
        if df[col].isnull().any():
            print(f"✗ {col} 列存在缺失值")
        else:
            print(f"✓ {col} 列无缺失值")
    
    return missing_df

def check_statistics(df):
    """计算基本统计量"""
    print("\n" + "="*50)
    print("【基本统计量】")
    print("="*50)
    
    # 价格列的统计量
    price_cols = ['open', 'high', 'low', 'close']
    stats = df[price_cols].describe().round(4)
    print("\n价格数据统计:")
    print(stats)
    
    # 成交量统计
    print("\n成交量数据统计:")
    volume_stats = df['volume'].describe().round(0)
    print(volume_stats)
    
    # 额外统计信息
    print("\n额外统计信息:")
    print(f"收盘价均值: {df['close'].mean():.2f}")
    print(f"收盘价中位数: {df['close'].median():.2f}")
    print(f"收盘价标准差: {df['close'].std():.2f}")
    print(f"收盘价变异系数: {(df['close'].std() / df['close'].mean() * 100):.2f}%")
    print(f"成交量均值: {df['volume'].mean():,.0f}")
    
    return stats

def check_data_consistency(df):
    """检查数据一致性（价格逻辑）"""
    print("\n" + "="*50)
    print("【数据一致性检查】")
    print("="*50)
    
    issues = []
    
    # 检查 high >= low
    high_low_issue = df[df['high'] < df['low']]
    if len(high_low_issue) > 0:
        issues.append(f"✗ 发现 {len(high_low_issue)} 条记录 high < low")
        print(issues[-1])
    else:
        print("✓ high >= low 检查通过")
    
    # 检查 close 在 [low, high] 范围内
    close_range_issue = df[(df['close'] < df['low']) | (df['close'] > df['high'])]
    if len(close_range_issue) > 0:
        issues.append(f"✗ 发现 {len(close_range_issue)} 条记录 close 超出 [low, high] 范围")
        print(issues[-1])
    else:
        print("✓ close 在 [low, high] 范围内检查通过")
    
    # 检查 open 在 [low, high] 范围内
    open_range_issue = df[(df['open'] < df['low']) | (df['open'] > df['high'])]
    if len(open_range_issue) > 0:
        issues.append(f"✗ 发现 {len(open_range_issue)} 条记录 open 超出 [low, high] 范围")
        print(issues[-1])
    else:
        print("✓ open 在 [low, high] 范围内检查通过")
    
    # 检查价格是否为负数
    negative_price = df[(df['open'] < 0) | (df['high'] < 0) | (df['low'] < 0) | (df['close'] < 0)]
    if len(negative_price) > 0:
        issues.append(f"✗ 发现 {len(negative_price)} 条记录价格为负数")
        print(issues[-1])
    else:
        print("✓ 价格非负检查通过")
    
    # 检查成交量是否为负数或零
    invalid_volume = df[df['volume'] <= 0]
    if len(invalid_volume) > 0:
        issues.append(f"✗ 发现 {len(invalid_volume)} 条记录成交量无效（<=0）")
        print(issues[-1])
    else:
        print("✓ 成交量有效性检查通过")
    
    return issues

def check_date_continuity(df):
    """检查日期连续性"""
    print("\n" + "="*50)
    print("【日期连续性检查】")
    print("="*50)
    
    # 按日期排序
    df_sorted = df.sort_values('date')
    
    # 计算日期间隔
    df_sorted['date_diff'] = df_sorted['date'].diff().dt.days
    
    # 找出间隔大于1天的情况（周末除外）
    gaps = df_sorted[df_sorted['date_diff'] > 1]
    
    if len(gaps) > 0:
        print(f"发现 {len(gaps)} 个日期间隔大于1天的情况:")
        for idx, row in gaps.iterrows():
            prev_date = row['date'] - pd.Timedelta(days=row['date_diff'])
            print(f"  {prev_date.date()} -> {row['date'].date()}, 间隔 {row['date_diff']} 天")
    else:
        print("✓ 日期连续性检查通过")
    
    return gaps

def generate_quality_report(df):
    """生成完整的数据质量报告"""
    print("="*70)
    print("苹果股票(AAPL)日线数据质量检查报告")
    print("="*70)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行各项检查
    rows, cols, min_date, max_date = check_data_shape(df)
    missing_df = check_missing_values(df)
    stats = check_statistics(df)
    issues = check_data_consistency(df)
    gaps = check_date_continuity(df)
    
    # 总结
    print("\n" + "="*70)
    print("【数据质量总结】")
    print("="*70)
    
    total_issues = len(issues) + len(gaps) + missing_df['缺失数量'].sum()
    
    if total_issues == 0:
        print("✓✓✓ 数据质量优秀，未发现任何问题！")
    else:
        print(f"⚠ 发现 {total_issues} 个潜在问题，建议进一步检查")
        if len(issues) > 0:
            print("\n问题列表:")
            for issue in issues:
                print(f"  {issue}")
    
    return {
        'rows': rows,
        'cols': cols,
        'date_range': f"{min_date.date()} 至 {max_date.date()}",
        'total_issues': total_issues,
        'missing_count': int(missing_df['缺失数量'].sum()),
        'consistency_issues': len(issues),
        'date_gaps': len(gaps)
    }

if __name__ == "__main__":
    # 数据文件路径
    data_file = "aapl_daily_20250701_20260630.csv"
    
    # 加载数据
    df = load_data(data_file)
    
    if df is not None:
        # 生成质量报告
        report = generate_quality_report(df)
        
        # 保存报告到文件
        report_filename = f"data_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("苹果股票(AAPL)日线数据质量检查报告\n")
            f.write("="*70 + "\n")
            f.write(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"数据文件: {data_file}\n")
            f.write(f"记录数: {report['rows']}\n")
            f.write(f"列数: {report['cols']}\n")
            f.write(f"日期范围: {report['date_range']}\n")
            f.write(f"总问题数: {report['total_issues']}\n")
            f.write(f"缺失值数量: {report['missing_count']}\n")
            f.write(f"一致性问题: {report['consistency_issues']}\n")
            f.write(f"日期间隔问题: {report['date_gaps']}\n")
            f.write("="*70 + "\n")
        
        print(f"\n✓ 报告已保存到: {report_filename}")
