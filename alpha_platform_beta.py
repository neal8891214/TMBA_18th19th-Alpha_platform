import pandas as pd
import numpy as np
import progressbar

class alpha_platform(object):
    def __init__(
        self, data, max_look_back=30, initial_cash=100000,
        fee_ratio=0.001425, tax_rate=0.003
        ):
        self.data = data
        self.max_look_back = max_look_back
        self.initial_cash = initial_cash
        self.data_len = len(self.data)
        self.commodity_num = len(self.data.columns.levels[0])
        self.fee_ratio = fee_ratio
        self.tax_rate = tax_rate
        self.entry_exit_price="開盤價(元)"
        # 每次建立物件(initiate)時執行，確保重設
        self.__reset()
    
    def __reset(self):
        # 一開始設定step_counter與max_look_back相同，之後step_counter會一直累加
        self.step_counter = self.max_look_back
        # 其餘資料也先歸零
        self.total_value = self.initial_cash
        self.weights_list = []
        self.position_vector = np.zeros([self.commodity_num])
        self.fee_cost = []
        self.tax_cost = []
        self.transaction_cost = []
        self.stocks_each_profit = []
        self.profit_list = []
        self.total_value_list = []
        self.long_short_count = []
        self.turnover = []
        
    def get_used_data(self):
        # 之後step_counter會一直累加，可確定欲使用資料窗格為當前step_counter回推至max_look_back之期間
        return self.data.iloc[
            (self.step_counter-self.max_look_back): self.step_counter
        ]
        
    def get_price_data(self, select_price=None):
        if select_price == None:
            select_price=self.entry_exit_price
        else:
            select_price = select_price
        return self.data.iloc[
            (self.step_counter-1): (self.step_counter+1)
        ].loc[:, (slice(None), select_price)].values
    
    def add_expression(self, expression):
        self.expression = expression
    
    def create_alpha(self):
        self.expression()
        assert len(self.weights) == self.commodity_num
    
    def simulate(self):
        # 回測前也先reset
        self.__reset()
        bar = progressbar.ProgressBar(maxval=len(self.data)).start()
        while self.step_counter < len(self.data):
            # 獲取最新價格資料(計算損益用)
            price_data = self.get_price_data()
            # 當日損益：部位權重*(今日的投組價值-昨日投組價值)
            daily_profit = self.position_vector[-1] * (price_data[-1,:] - price_data[-2,:])
            # 計算交易成本(稅&手續費，借券費用尚未考量)
            if self.step_counter == self.max_look_back:
                self.position_change = np.zeros([self.commodity_num])
            else:
                self.position_change = np.vstack([
                    self.position_change,
                    self.position_vector[-1]-self.position_vector[-2]
                ])
            # 手續費
            current_fee_cost = abs(self.position_change[-1] * price_data[-1,:] * self.fee_ratio)
            # 交易稅
            current_tax_cost = list(
                map(
                    lambda x: abs(x * self.tax_rate) if x<0 else 0,
                    self.position_change[-1] * price_data[-1,:]
                    )
            )
            # 總交易成本
            current_transaction_cost = current_fee_cost + current_tax_cost
            # 儲存交易成本結果
            if self.step_counter == self.max_look_back:
                self.fee_cost = current_fee_cost
                self.tax_cost = current_tax_cost
                self.transaction_cost = current_transaction_cost
            else:
                self.fee_cost = np.vstack([
                    self.fee_cost,
                    current_fee_cost
                ])
                self.tax_cost = np.vstack([
                    self.tax_cost,
                    current_tax_cost
                ])
                self.transaction_cost = np.vstack([
                    self.transaction_cost,
                    current_transaction_cost
                ])
            # 毛獲利扣除交易成本
            daily_profit = daily_profit - current_transaction_cost
            # 把nan轉成0，否則計算損益相關績效全部會變nan
            daily_profit = np.nan_to_num(daily_profit)
            # 計算turnover(計算方式待確定)
            self.turnover.append(sum(abs(daily_profit)) / self.initial_cash)
            # 計算各股票損益狀況
            if self.step_counter == self.max_look_back:
                self.stocks_each_profit = daily_profit
            else:
                # 透過np.vstack把過往各期的累計損益狀況記錄下來
                self.stocks_each_profit = np.vstack([
                    self.stocks_each_profit,
                    # 上一期損益+本期損益=最新累加損益
                    self.stocks_each_profit[-1]+daily_profit
                ])
            # 紀錄獲利情況
            self.profit_list.append(sum(daily_profit))
            self.total_value += sum(daily_profit)
            self.total_value_list.append(self.total_value)
            # 考量損益後，重新產生權重，呼叫此function後，sel.weights將被更新
            try:
                self.create_alpha()
            except Exception as e:
                print("Something wrong with exception:")
                print(e)
            # 紀錄weights
            if self.step_counter == self.max_look_back:
                self.weights_list = self.weights
            else:
                self.weights_list = np.vstack([
                    self.weights_list,
                    self.weights
                ])
            # 紀錄各期部位分配情況(各股票被分得多少單位)
            # 若權重不變則沿用舊的position_vector，不重新reblance，但就沒有將價格納入考量
            if self.step_counter == self.max_look_back:
                self.position_vector = np.vstack([
                    self.position_vector,
                    (self.initial_cash * self.weights) / price_data[-1,:]
                ])
            else:
                # 兩數列相比時，即使相對應位置都是nan，用"!="還是會顯示false，所以先將nan值轉為0再比較
                if sum(np.nan_to_num(self.weights) != np.nan_to_num(self.weights_list[-2])) >0:
                    self.position_vector = np.vstack([
                        self.position_vector,
                        (self.initial_cash * self.weights) / price_data[-1,:]
                    ])
                else:
                    self.position_vector = np.vstack([
                        self.position_vector,
                        self.position_vector[-1]
                    ])
            # 紀錄多與空各別交易次數
            self.long_short_count.append(
                (
                    (np.nan_to_num(self.weights)>0).sum(),
                    (np.nan_to_num(self.weights)<0).sum()
                )
            )
            # 完成步驟step_counter向下推移
            self.step_counter += 1
            bar.update(self.step_counter)
        bar.finish()
        print('Compelete the simulation!')
    
    def calculate_info(self):
        # 儲存交易日期
        self.date = list(map(lambda x: pd.to_datetime(x),
                             self.data.index.values[self.max_look_back: ]))
        # 計算drawdown
        self.drawdown_list = []
        for i in range(len(self.total_value_list)):
            max_temp_equity = max(self.total_value_list[:i+1])
            drawdown = self.total_value_list[i] - max_temp_equity
            self.drawdown_list.append(drawdown)  
        # 計算Sharpe ratio, returns
        yearly_sharpe_ratio = []
        yearly_returns = []
        yearly_long_short = []
        yearly_turnover = []
        yearly_fitness = []
        years = []
        self.value_info = pd.DataFrame({
            'date': self.date,
            'profit': self.profit_list,
            'long_short_count': self.long_short_count,
            'turnover': self.turnover
        })
        yearly_info_df = self.value_info.groupby(pd.Grouper(key='date', freq='1y'))
        year_keys = list(yearly_info_df.groups.keys())
        for key in year_keys:
            year_info = yearly_info_df.get_group(key)
            # IR = Avg(PnL)/Std_dev(PnL)
            yearly_sharpe_ratio.append(
                year_info.profit.mean() / year_info.profit.std() * np.sqrt(len(year_info))
            )
            # Annualized PnL / Half of Book Size.
            yearly_returns.append(year_info.profit.sum()/self.initial_cash*2)
            # average long/short count of 1 year
            yearly_long_short.append([sum(y)/len(y) for y in zip(*year_info.long_short_count)])
            yearly_turnover.append(year_info.turnover.mean())
            yearly_fitness.append(
                yearly_sharpe_ratio[-1] * np.sqrt(abs(yearly_returns[-1]) / yearly_turnover[-1])
            )
            years.append(key.year)

        self.yearly_info = pd.DataFrame({'year': years, 
                                         'sharpe_ratio': yearly_sharpe_ratio, 
                                         'returns': yearly_returns, 
                                         'long_short_count': yearly_long_short, 
                                         'turnover': yearly_turnover,
                                         'fitness': yearly_fitness})
    def strategy_report(self):
        self.calculate_info()
        print('淨利：        {:15.2f}'.format(self.total_value))
        print('最大策略虧損： {:15.2f}'.format(min(self.drawdown_list)))