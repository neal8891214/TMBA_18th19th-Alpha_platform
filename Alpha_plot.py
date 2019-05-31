import pandas as pd
import numpy as np
import datetime
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)

'''宣告一個固定用樣式模板，爾後更改 title 即可直接套用'''
layout = go.Layout(
    xaxis=go.layout.XAxis(
        title=go.layout.xaxis.Title(
            text='Date',
            font=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    ),
    yaxis=go.layout.YAxis(
        title=go.layout.yaxis.Title(
            text='NTD',
            font=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    ),
    title = 'Equity Curve',
    paper_bgcolor='rgba(245, 246, 249, 1)',
    plot_bgcolor='rgba(245, 246, 249, 1)',
    legend=dict(
        x=0,
        y=1    
    )
)

def plot_equity(alpha_platform):
    '''印出權益曲線並標記創新高的點'''
    value_info = pd.DataFrame({ 'date': alpha_platform.date, 
                                'total_value': alpha_platform.total_value_list})
    # 找出創新高點
    new_highest_index = []
    for i in range(len(value_info.total_value)):
        current_accumulate_profit = value_info.total_value.iloc[i]
        if i == 0:
            new_highest = value_info.total_value.iloc[i]
        if (current_accumulate_profit > new_highest) and (current_accumulate_profit > 0):
            new_highest = current_accumulate_profit
            new_highest_index.append(i)

    layout.title.text = 'Equity curve'

    equity = go.Scatter(
        x = value_info.date,
        y = value_info.total_value,
        name = "Equity curve",
        line = dict(color = '#000000'),
        opacity = 0.5)
    
    high_points = go.Scatter(
        x = value_info.date[new_highest_index],
        y = value_info.total_value[new_highest_index],
        mode = 'markers',
        name = 'Highest Equity so for'
    )
    high_points.marker.color = '#02ff0f'

    data = [equity, high_points]
    fig = go.Figure(data=data, layout=layout)
    iplot(fig, filename='equity curve')

def plot_each_profit(alpha_platform):
    '''印出個別股票獲利'''
    value_info = pd.DataFrame({'date': alpha_platform.date})

    data = []
    for i in range(len(alpha_platform.data.columns.levels[0])):
        data.append(
            go.Scatter(
                x = value_info.date,
                y = alpha_platform.stocks_each_profit[:,i],
                name = alpha_platform.data.columns.levels[0][i]
            )
        )

    layout.title.text = 'All stocks Profits'
    fig = go.Figure(data=data, layout=layout)
    iplot(fig, filename='all profits')

def plot_drawdown(alpha_platform):
    '''印出總績效之 drawdown'''
    value_info = pd.DataFrame( {'date': alpha_platform.date, 
                                'drawdown': alpha_platform.drawdown_list})
    equity = go.Scatter(
        x = value_info.date,
        y = value_info.drawdown,
        name = "Equity curve",
        line = dict(color = 'red'))

    layout.yaxis.title.text = 'Drawdown'
    layout.title.text = 'Drawdown'

    data = [equity]
    fig = go.Figure(data=data, layout=layout)
    iplot(fig, filename='Drawdown')

def plot_sharpe_ratio_return(alpha_platform):
    '''將 sharpe ratio 及 return 印在同一張圖中'''
    sh = go.Scatter(
        x = alpha_platform.yearly_info.year,
        y = alpha_platform.yearly_info.sharpe_ratio,
        name = "Sharpe Ratio",
        line = dict(color = '#ff8040'),
        opacity = 0.8)

    re = go.Scatter(
        x = alpha_platform.yearly_info.year,
        y = alpha_platform.yearly_info.returns,
        name = "Return",
        line = dict(color = '#0066cc'),
        opacity = 0.8,
        yaxis='y2')

    layout.yaxis2 = dict(title='Return',
                        titlefont=dict(
                            color='rgb(148, 103, 189)'
                        ),
                        tickfont=dict(
                            color='rgb(148, 103, 189)'
                        ),
                        overlaying='y',
                        side='right'
                    )

    layout.yaxis.title.text = 'Sharpe Ratio'
    layout.title.text = 'Sharpe Ratio and Return'

    data = [sh, re]
    fig = go.Figure(data=data, layout=layout)
    iplot(fig, filename='Sharpe Ratio and Return')
