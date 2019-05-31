# Taiwan Quant beta
## 簡介
此為台灣股票回測平台，由TMBA 19th程式交易部合力完成，透過撰寫expression產生回測訊號，共有以下檔案(data放置於雲端硬碟中)：
  * [**alpha_platform_beta**](https://github.com/Andy-Liu66/TMBA_pair_trading_module/blob/master/Taiwan%20Quant%20beta/alpha_platform_beta.py):
    
	  存放主要程式碼
  * [**Operators**](https://github.com/Andy-Liu66/TMBA_pair_trading_module/tree/master/Taiwan%20Quant%20beta/Operators):
  
 	  存放撰寫expression的Operators
  * [**basic_tool**](https://github.com/Andy-Liu66/TMBA_pair_trading_module/blob/master/Taiwan%20Quant%20beta/basic_tool.py):
    
	  存放策略撰寫過程所需function
  * [**Alpha_plot**](https://github.com/Andy-Liu66/TMBA_pair_trading_module/blob/master/Taiwan%20Quant%20beta/Alpha_plot.py):
  
    存放績效視覺化class
  * [**help**](https://github.com/Andy-Liu66/TMBA_pair_trading_module/tree/master/Taiwan%20Quant%20beta/help):
  
    存放損益計算方式說明
  * [**example**](https://github.com/Andy-Liu66/TMBA_pair_trading_module/blob/master/Taiwan%20Quant%20beta/example.ipynb)
   
    存放Demo檔
## 要求
* **使用套件**：
  * pandas
  * numpy
  * plotly(3.7.1 以上)
  * progressbar(2.5)
## Demo
例子存放於example中，以下簡要介紹使用方法：

#### 輸入套件
```python
import pandas as pd
import numpy as np
from alpha_platform_beta import alpha_platform
from basic_tool import select_data, neturalize_weights
from Alpha_plot import *
```

#### 輸入資料
```python
data = pd.read_csv("data/financial_industry.csv", low_memory=False, header=[0, 1], index_col=0)

# 取2001年後的資料
data = data.iloc[271:]
```

#### 建立alpha_platform物件
```python
test_platform = alpha_platform(data)
```

#### 撰寫expression
```python
# 來自Operators
def sigmoid(x):
    return(1 / (1 + np.exp(-x)))

# 撰寫expression
def expression():
    # 依據給定max_look_back值，回推資料區間(由現在回推至t-max_look_back期)
    # 之後便可透過used_data進行後續運算
    used_data = test_platform.get_used_data()

    # 可透過select_data功能選擇欲使用的資料
    eps = select_data(used_data, "每股盈餘 (元)")

    # 依據最新一期eps資料丟到sigmoid函數後產生權重
    temp_weights = sigmoid(eps[-1])
    
    # 將權重正規劃並指定回上面建立的alpha_platform物件中的weights
    test_platform.weights = neturalize_weights(temp_weights)
```

#### 開始回測
```python
# 定義完expression後，將其加入原先alpha_platform物件
test_platform.add_expression(expression)

# 開始回測
test_platform.simulate()
```

#### 檢視策略績效基本資訊
```python
test_platform.strategy_report()

淨利：              128132.05
最大策略虧損：      -383784.44
```

#### 檢視策略權益曲線
```python
plot_equity(alpha_platform=test_platform)
```

![Equity curve](https://i.imgur.com/xEhe5uX.png)

#### 檢視策略中各股績效表現
```python
plot_each_profit(test_platform)
```

![all stocks profit](https://i.imgur.com/80q8gnI.png)

#### 檢視策略drawdown
```python
plot_drawdown(alpha_platform=test_platform)
```

![drawdown](https://i.imgur.com/QVCcmmw.png)

#### 檢視策略sharpe ratio
```python
plot_sharpe_ratio_return(alpha_platform=test_platform)
```

![drawdown](https://i.imgur.com/SHjAGK1.png)

#### 檢視策略年化資訊
<table border="1" class="dataframe">  <thead>    <tr style="text-align: right;">      <th></th>      <th>fitness</th>      <th>long_short_count</th>      <th>returns</th>      <th>sharpe_ratio</th>      <th>turnover</th>      <th>year</th>    </tr>  </thead>  <tbody>    <tr>      <th>0</th>      <td>3.488575</td>      <td>[3.41588785047, 6.16822429907]</td>      <td>1.919475</td>      <td>1.003505</td>      <td>0.158828</td>      <td>2001</td>    </tr>    <tr>      <th>1</th>      <td>5.419819</td>      <td>[7.04838709677, 2.95161290323]</td>      <td>2.652236</td>      <td>1.408819</td>      <td>0.179206</td>      <td>2002</td>    </tr>    <tr>      <th>2</th>      <td>-4.775621</td>      <td>[4.47791164659, 6.04417670683]</td>      <td>-2.667819</td>      <td>-1.243848</td>      <td>0.180980</td>      <td>2003</td>    </tr>    <tr>      <th>3</th>      <td>-3.646221</td>      <td>[3.488, 7.512]</td>      <td>-2.038759</td>      <td>-0.857610</td>      <td>0.112787</td>      <td>2004</td>    </tr>    <tr>      <th>4</th>      <td>3.219523</td>      <td>[7.45748987854, 3.54251012146]</td>      <td>1.046574</td>      <td>0.732804</td>      <td>0.054220</td>      <td>2005</td>    </tr>  </tbody></table>

## 說明
* 權重在撰寫expression中生成，由於權重產生後會乘以initial cash得到該股票被分配的金額，接著再依據此金額除以其收盤價決定股數，程式中會判斷若權重相同則沿用首次出現此權重的股數(與最初版本方式不同)，目的是在權重相同的情況下，不會因為收盤價的變動而出現更改股數的狀況，會導致過於頻繁的重新平衡，而產生過多交易成本。
* 資料若為低頻資料，如季報資料，則在公布後至下次公布前都會是相同值，所以若使用這類型資料產生權重，則權重理應會相同，延續第一點邏輯則不會有部位更動，直到下次有新值產生後才會重新平衡。
* 目前由開盤價計算損益，亦即假設在收盤決定權重後，以當日開盤價作為成本價，與下次平衡時的開盤價進行比較計算績效(但權重產生是在開盤後，不見得買的到開盤價)。
* 獲利計算方式與help資料夾中的[excel檔](https://github.com/Andy-Liu66/TMBA_pair_trading_module/tree/master/Taiwan%20Quant%20beta/help)舉例相同邏輯。
* 寫expression若有問題，當中有用except去抓error的原因，較好debug。
* 目前尚未考量融券成本。
* Operators基本上輸入向量回傳向量，在撰寫expression過程中應該不會有太大問題。
* 若出現*RuntimeWarning*，基本上應該跟nan有關係，如果出現所有input資料都是nan時則會警示，可能像是除以0之類的狀況。

## 待完成
* 考量融券成本。
* 權重正規化的方式尚待確定。
* Operators可能需要debug(有試過rank結果爆炸)。
* Operators裝在py檔裡比較好import。
* turnover(計算方式待確定)。
* Debug再Debug...

## Feedback
欲修改code歡迎直接送pull request。