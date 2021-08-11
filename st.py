import pandas as pd
import streamlit as st
import time 
import pandas_datareader.data as web

def load_equities_web(symbol, date_from):
    raw_data = web.DataReader(symbol, 'yahoo', pd.to_datetime(date_from), pd.datetime.now())
    data = raw_data.stack(dropna=False)['Adj Close'].to_frame().reset_index().rename(columns = {'Symbols':'symbol', 'Date':'date', 'Adj Close':'value'}).sort_values(by = ['symbol', 'date'])
    return pd.pivot_table(data, columns = 'symbol', index = 'date', values ='value')

def backtest_strategy(prices, symbol_trade, symbol_volatility, volatility_threshold, capital, symbol_benchmark):
    
    df_init   = (prices[symbol_trade]*0).to_frame().assign(cash = 0) #beg of trading session
    df_update = (prices[symbol_trade]*0).to_frame().assign(cash = 0) #diff between end and beg
    df_end    = (prices[symbol_trade]*0).to_frame().assign(cash = 0) #pos holding at the end of the day
    
    df_init.iloc[0, df_init.columns.get_loc('cash')] = capital
    df_end.iloc[0, df_end.columns.get_loc('cash')]   = capital
    
    calendar = pd.Series(prices.index).iloc[1:]
    
    
    for date in calendar:
        prev_date = df_init.index[df_init.index<date][-1]
        
        df_init.loc[date, :] = df_end.loc[prev_date, :]
        
        port_value = df_init.loc[date, symbol_trade] * prices.loc[date, symbol_trade] + df_init.loc[date, 'cash']
        
        if prices.loc[date, symbol_volatility] > volatility_threshold: # volatility is high -> be fully in cash
            df_end.loc[date, symbol_trade] = 0
            df_end.loc[date, 'cash']       = port_value
        else: # volatility is low -> be in market position
            df_end.loc[date, symbol_trade] = port_value/prices.loc[date, symbol_trade]
            df_end.loc[date, 'cash'] = 0
        df_update.loc[date] = df_end.loc[date] - df_init.loc[date]
    

    portval = (df_end*prices.assign(cash = 1)[[symbol_trade, 'cash']]).sum(axis = 1).to_frame().rename(columns = {0:'strategy'})
    portval['benchmark'] = prices[symbol_benchmark]
    portval = portval/portval.iloc[0].values
    
    return portval
    


"""
# Interactive Backtesting Module

Dataset used: Price data of SP500 (SPY)
"""
"""
Problems with data: Not survivorship bias free as constituent are of 2021.
"""
"""
This is intended to get an interactive feel and response.
"""
"""
The sample backtest here has no form of portfolio optimization, shares are bought at equal weights and assumed to allow for fractional shares. Starting capital of $10,000
"""
"""
Assumptions: No transaction costs, trading can be only done once a day by the end of the trading session 
"""


df1 = pd.DataFrame({
    'first column': [_ for _ in range(2000, 2022)]   
})

df2 = pd.DataFrame({
    'second column': ["Low Volatility Trade","Mean Reversion"]
})

option1 = st.selectbox(
    'Indicate Start Year',
    df1['first column'])

option2 = st.selectbox(
    'Indicate Preferred Strategy',
    df2['second column'])

if option2 == "Low Volatility Trade":
    vol_threshold = st.slider('Volatility Threshold', min_value=0, max_value=100, value=30)

'You selected the backtest to be from ', option1, "to today, using a ", option2, "investing strategy."

submit_button = st.button(label='Commence backtest')
    
# st.form_submit_button returns True upon form submit
if submit_button:
    if option2 == 'Low Volatility Trade': 
        prices = load_equities_web(['SPY', '^GSPC', '^VIX'], date_from = str(option1) + "-01-01")

        res = backtest_strategy(prices = prices, symbol_trade = 'SPY', symbol_volatility = '^VIX', volatility_threshold = vol_threshold, capital = 10000, symbol_benchmark = '^GSPC')

        st._arrow_line_chart(res)

        st.dataframe(res)
        