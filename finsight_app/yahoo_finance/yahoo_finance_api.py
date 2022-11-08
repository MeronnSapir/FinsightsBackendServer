import yfinance as yf
import pandas as pd


class YahooFinanceAPI:

    @staticmethod
    def get_current_price(ticker: str):
        stock = yf.Ticker(ticker=ticker)
        price = stock.info['currentPrice']
        return price

    @staticmethod
    def get_historic_data(ticker: str, days_back: int):
        stock_history = yf.Ticker(ticker=ticker).history(period=str(days_back) + "d", interval="1d")
        return stock_history

    @staticmethod
    def get_historic_price(ticker: str, time_back: str):
        data = yf.Ticker(ticker=ticker).history(period=time_back, interval=time_back)
        list_data = data.values.tolist()
        print(list_data)
        # print(list_data[])
        if time_back == '1d':
            return list_data[0][1]
        return list_data[0][3]

    @staticmethod
    def get_daily_move(ticker: str):
        stock_info = yf.Ticker(ticker=ticker).info
        current_price = stock_info['currentPrice']
        open_price = stock_info['regularMarketOpen']
        daily_move = (current_price / open_price - 1) * 100
        return daily_move


y = YahooFinanceAPI()
historic_data = y.get_historic_price(ticker='MSFT', time_back='5d')
print(type(historic_data))
print(historic_data)

