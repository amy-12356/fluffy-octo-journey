import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import os

def load_stock_data(file_path):
    """加载股票CSV数据"""
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    # 按日期排序
    df = df.sort_values('date').reset_index(drop=True)
    print(f"✓ 成功加载数据: {len(df)} 条记录")
    print(f"  日期范围: {df['date'].min().date()} 至 {df['date'].max().date()}")
    return df

def calculate_indicators(df):
    """计算技术指标"""
    # 日收益率
    df['return'] = df['close'].pct_change() * 100
    
    # 涨跌标记
    df['color'] = df.apply(lambda row: 'green' if row['close'] >= row['open'] else 'red', axis=1)
    
    # 实体大小
    df['body_size'] = abs(df['close'] - df['open'])
    
    # 上影线长度
    df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
    
    # 下影线长度
    df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
    
    return df

def plot_candlestick(df, stock_name='AAPL'):
    """绘制蜡烛图"""
    # 创建子图：上方K线图，下方成交量图
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{stock_name} 日线蜡烛图', '成交量'),
        row_width=[0.7, 0.3]
    )
    
    # 添加蜡烛图
    fig.add_trace(
        go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K线',
            increasing_line_color='#ef4444',  # 上涨红色
            decreasing_line_color='#22c55e',  # 下跌绿色
            increasing_fillcolor='#ef4444',   # 上涨填充红色
            decreasing_fillcolor='#22c55e',   # 下跌填充绿色
            opacity=0.8,
            whiskerwidth=1
        ),
        row=1, col=1
    )
    
    # 添加5日均线
    df['ma5'] = df['close'].rolling(window=5).mean()
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['ma5'],
            name='MA5',
            line=dict(color='#3b82f6', width=2),
            opacity=0.8
        ),
        row=1, col=1
    )
    
    # 添加20日均线
    df['ma20'] = df['close'].rolling(window=20).mean()
    fig.add_trace(
        go.Scatter(
            x=df['date'],
            y=df['ma20'],
            name='MA20',
            line=dict(color='#f59e0b', width=2, dash='dash'),
            opacity=0.8
        ),
        row=1, col=1
    )
    
    # 添加成交量柱状图
    colors = ['#ef4444' if close >= open else '#22c55e' for close, open in zip(df['close'], df['open'])]
    fig.add_trace(
        go.Bar(
            x=df['date'],
            y=df['volume'],
            name='成交量',
            marker_color=colors,
            opacity=0.6
        ),
        row=2, col=1
    )
    
    # 更新布局
    fig.update_layout(
        title=f'{stock_name} 股票日线蜡烛图',
        title_font=dict(size=20, color='#333'),
        xaxis_title='日期',
        yaxis_title='价格 ($)',
        xaxis_rangeslider_visible=False,
        template='plotly_white',
        height=800,
        width=1200,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        hovermode='x unified'
    )
    
    # 更新坐标轴
    fig.update_xaxes(
        rangebreaks=[
            dict(bounds=['sat', 'mon']),  # 隐藏周末
            dict(bounds=[17, 9.5], pattern='hour')  # 隐藏非交易时间
        ],
        tickformat='%Y-%m-%d',
        showgrid=True,
        gridcolor='#f3f4f6'
    )
    
    fig.update_yaxes(
        title_text='价格 ($)',
        row=1, col=1,
        showgrid=True,
        gridcolor='#f3f4f6'
    )
    
    fig.update_yaxes(
        title_text='成交量',
        row=2, col=1,
        showgrid=True,
        gridcolor='#f3f4f6',
        ticksuffix=''
    )
    
    # 添加注释信息
    avg_return = df['close'].pct_change().mean() * 100
    stats_text = f"""
    统计信息:
    - 总记录数: {len(df)}
    - 日期范围: {df['date'].min().date()} ~ {df['date'].max().date()}
    - 平均收盘价: ${df['close'].mean():.2f}
    - 最高收盘价: ${df['close'].max():.2f}
    - 最低收盘价: ${df['close'].min():.2f}
    - 平均日收益率: {avg_return:.2f}%
    """
    
    # 生成HTML文件
    html_filename = f'{stock_name.lower()}_candlestick.html'
    fig.write_html(html_filename)
    print(f"✓ 蜡烛图已保存到: {html_filename}")
    
    # 自动打开浏览器
    webbrowser.open('file://' + os.path.abspath(html_filename))
    
    return fig

def plot_interactive_candlestick(df, stock_name='AAPL'):
    """绘制交互式蜡烛图（带更多交互功能）"""
    # 计算指标
    df = calculate_indicators(df)
    
    # 创建图表
    fig = go.Figure(data=[
        go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K线',
            increasing_line_color='#ef4444',
            decreasing_line_color='#22c55e',
            increasing_fillcolor='#ef4444',
            decreasing_fillcolor='#22c55e',
            opacity=0.8,
            showlegend=True
        )
    ])
    
    # 添加布林带
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['upper_bb'] = df['ma20'] + 2 * df['close'].rolling(window=20).std()
    df['lower_bb'] = df['ma20'] - 2 * df['close'].rolling(window=20).std()
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['ma20'],
        line=dict(color='#f59e0b', width=2),
        name='MA20'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['upper_bb'],
        line=dict(color='#8b5cf6', width=1, dash='dash'),
        name='布林带上轨'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['lower_bb'],
        line=dict(color='#8b5cf6', width=1, dash='dash'),
        name='布林带下轨'
    ))
    
    # 填充布林带区域
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['upper_bb'],
        fill=None,
        mode='lines',
        line_color='rgba(139, 92, 246, 0.1)',
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'], y=df['lower_bb'],
        fill='tonexty',
        mode='lines',
        line_color='rgba(139, 92, 246, 0.1)',
        showlegend=False
    ))
    
    fig.update_layout(
        title=f'{stock_name} 交互式蜡烛图（含布林带）',
        title_font=dict(size=20, color='#333'),
        xaxis_title='日期',
        yaxis_title='价格 ($)',
        xaxis_rangeslider_visible=True,
        template='plotly_dark',
        height=700,
        width=1200,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        hovermode='x unified'
    )
    
    fig.update_xaxes(
        rangebreaks=[dict(bounds=['sat', 'mon'])],
        tickformat='%Y-%m-%d'
    )
    
    # 生成HTML文件
    html_filename = f'{stock_name.lower()}_interactive_candlestick.html'
    fig.write_html(html_filename)
    print(f"✓ 交互式蜡烛图已保存到: {html_filename}")
    
    # 自动打开浏览器
    webbrowser.open('file://' + os.path.abspath(html_filename))
    
    return fig

if __name__ == "__main__":
    # 数据文件路径
    data_file = "aapl_daily_20250701_20260630.csv"
    
    # 加载数据
    df = load_stock_data(data_file)
    
    # 绘制标准蜡烛图（含成交量子图）
    print("\n正在绘制标准蜡烛图...")
    plot_candlestick(df, stock_name='AAPL')
    
    # 绘制交互式蜡烛图（含布林带）
    print("\n正在绘制交互式蜡烛图...")
    plot_interactive_candlestick(df, stock_name='AAPL')
    
    print("\n✓ 蜡烛图绘制完成！")
