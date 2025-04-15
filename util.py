from datetime import datetime

import pandas as pd


class DataUtil:
    @staticmethod
    def calculate_sma(df, period: int = 50):
        return pd.DataFrame({
            'time': df['time'],
            f'SMA {period}': df['close'].rolling(window=period).mean()
        }).dropna()

    @staticmethod
    def on_horizontal_line_move(chart, line):
        print(f'Horizontal line moved to: {line.price}')

    @staticmethod
    def on_timeframe_selection(mt5, chart):  # Called when the user changes the timeframe.
        print("Ok")
        new_data = DataUtil.get_bar_data(
            mt5=mt5,
            symbol=chart.topbar['symbol'].value,
            timeframe=chart.topbar['timeframe'].value)
        if new_data.empty:
            return
        chart.set(new_data, True)

    @staticmethod
    def on_search(mt5, chart, searched_string):  # Called when the user searches.
        new_data = DataUtil.get_bar_data(
            mt5=mt5,
            symbol=searched_string,
            timeframe=chart.topbar['timeframe'].value
        )
        if new_data.empty:
            return
        chart.topbar['symbol'].set(searched_string)
        chart.set(new_data)

    @staticmethod
    def get_bar_data(mt5, timeframe: str = "", symbol: str = ""):
        if symbol not in ('XAUUSDm', 'EURUSD', 'GPDUSD'):
            print(f'No data for "{symbol}"')
            return pd.DataFrame()
        else:
            date_from = datetime(2025, 1, 15)
            date_to = datetime.now()
            prices = pd.DataFrame(
                mt5.copy_rates_range(
                    symbol,
                    int(timeframe),
                    date_from,
                    date_to
                )
            )
            prices["time"] = pd.to_datetime(prices["time"], unit="s")
            prices = prices.rename(columns={
                'tick_volume': 'volume',
            })
            prices.columns = prices.columns.str.lower()
            return prices
