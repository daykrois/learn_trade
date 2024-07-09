import baostock as bs
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, DateFormatter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.font_manager import FontProperties

# 指定中文字体
# fname 使用绝对路径来指定字体文件，这里是微软雅黑字体（MSYH.TTC），位于 Windows 字体目录下
font = FontProperties(fname=r'c:\Windows\Fonts\MSYH.TTC' )

# 开始日期
start_date = '2017-07-01'


# 结束日期
end_date = '2017-12-31'

# 证券代码，这里是沪深300 
code = 'h.000300'

# 需要获取的具体字段
fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST"

# fields 里每个字段的中文含义
columns = ['交易所行情日期', '证券代码', '开盘价', '最高价', '最低价', '收盘价', '前收盘价', 
           '成交量（累计 单位：股）', '成交额（单位：人民币元）', '复权状态(1：后复权， 2：前复权，3：不复权）', 
           '换手率', '交易状态(1：正常交易 0：停牌）', '涨跌幅（百分比）', '滚动市盈率', 
           '市净率', '滚动市销率', '滚动市现率', '是否ST股，1是，0否']


def fetch_stock_data(code):
    lg = bs.login()
    rs = bs.query_history_k_data_plus(code=code,fields=fields,
                                 start_date=start_date, end_date=end_date,
                                 frequency="d", adjustflag="3")
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=columns)
    result.to_csv("history_A_stock_k_data.csv", index=False, encoding='utf-8-sig')
    bs.logout()
    
    
def decimal_formatter(x, pos):
    return f'{x:,.0f}'

# 绘制折线图
def show_Line_chart(date,close):

    # 使用Matplotlib绘制折线图
    plt.figure(figsize=(10, 5))
    plt.plot(date,close, marker='o')

    #  # 对每个点添加注解
    # for i in range(len(date)):
    #     plt.annotate(f'{close[i]:,.0f}', 
    #                  (date[i], close[i]), 
    #                  textcoords="offset points", 
    #                  xytext=(0,10), 
    #                  ha='center')  # 设置注解相对于点的位置
        
    # 找到最高点和最低点的索引
    max_index = close.idxmax()
    min_index = close.idxmin()
    # 在图上标注最高点和最低点
    plt.scatter(date[max_index], close[max_index], color='red', label='Max')
    plt.annotate(f'{close[max_index]:,.0f}', xy=(date[max_index], close[max_index]), 
                 xytext=(date[max_index], close[max_index]+50))
    plt.scatter(date[min_index], close[min_index], color='green', label='Min')
    plt.annotate(f'{close[min_index]:,.0f}', xy=(date[min_index], close[min_index]), 
                 xytext=(date[min_index], close[min_index]-50))
    # 添加对最后一天数据的标注
    last_date = date.iloc[-1]
    last_close = close.iloc[-1]
    plt.scatter(last_date, last_close, color='blue', label='Last')
    plt.annotate(f'{last_close:,.0f}', xy=(last_date, last_close),
                 xytext=(last_date, last_close+50)) 
    
     
    # 设置x轴日期格式器和定位器
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)  # 自动选择最佳的间隔 
    plt.gca().xaxis.set_major_locator(locator)
    # 使用逗号作为千位分隔符
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(decimal_formatter))
    # 显示网格
    plt.grid(True)
    # 自动旋转日期标签防止重叠
    plt.gcf().autofmt_xdate()
    # 显示图表
    plt.show()


def trade_stock(direction,quantity,price):
    if direction == 'buy':
        cost_RMB = quantity * price + quantity * price * commission_rate
        return cost_RMB

    if direction == 'sell':
        get_RMB = quantity * price - quantity * price * commission_rate
        return get_RMB

if __name__ == "__main__":

    init_RMB = 10000000
    commission_rate = 0.001

    data = pd.read_csv("history_A_stock_k_data.csv")
    data['涨跌值'] = data['收盘价'].diff()
    data['涨跌值'] = data['涨跌值'].fillna(0.0)
    data['是否涨跌'] = np.where(data['涨跌值'] > 0, 1, 0)
    # show_Line_chart(data['交易所行情日期'],data['收盘价'])
    # show_Line_chart(data['交易所行情日期'],data['是否涨跌'])
    data['下单'] = (data['是否涨跌'].diff()*100).fillna(0.0)
    # 总价值
    total_values = []
    balance = init_RMB
    shares = 0

    for i in range(0,len(data['下单'])):
        if data['下单'][i] == 0:
            total_value = balance + shares * data.loc[i,'收盘价']
            total_values.append(total_value)



        if data['下单'][i] == 100:
            cost_RMB = trade_stock('buy',100,data.loc[i,'收盘价'])
            balance = balance - cost_RMB
            shares = shares + 100
            total_value = balance + shares * data.loc[i,'收盘价']
            total_values.append(total_value)

        
        if data['下单'][i] == -100:
            get_RMB = trade_stock('sell',100,data.loc[i,'收盘价'])
            balance = balance + get_RMB
            shares = shares - 100
            total_value = balance + shares * data.loc[i,'收盘价']
            total_values.append(total_value)

    data['总价值'] = total_values

    show_Line_chart(data['交易所行情日期'],data['总价值'])



          


     