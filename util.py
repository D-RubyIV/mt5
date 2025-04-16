from datetime import datetime, timedelta

import pandas as pd

from constant import SYMBOLS, TimeFrames

def timeframe_to_minutes(timeframe_value: int) -> int:
    FLAG_HOUR = 0x4000
    FLAG_WEEK = 0x8000
    FLAG_MONTH = 0xC000

    # Tách phần số bằng cách loại bỏ cờ
    base_value = timeframe_value & 0x3FFF  # giữ lại 14 bit thấp

    if timeframe_value & FLAG_HOUR:
        return base_value * 60
    elif timeframe_value & FLAG_WEEK:
        return base_value * 7 * 1440  # 1 tuần = 7 ngày
    elif timeframe_value & FLAG_MONTH:
        return base_value * 30 * 1440  # 1 tháng ~ 30 ngày
    else:
        return base_value  # mặc định là phút

def get_color_for_level(level):
    if level == 1:
        return "#000000"  # Đen
    elif level == 2:
        return "#FFA500"  # Cam
    elif level == 3:
        return "#FF0000"  # Đỏ
    return "#000000"


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
        from pytz import timezone
        eastern = timezone('Asia/Bangkok')
        if symbol not in SYMBOLS:
            print(f'No data for "{symbol}"')
            return pd.DataFrame()
        else:
            print(f"TimeFrame: {timeframe_to_minutes(int(timeframe))}")
            date_from = datetime.now() - timedelta(minutes=int(timeframe_to_minutes(int(timeframe))) * 500)
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
            prices['time'] = pd.to_datetime(prices['time'], unit='ms', origin='unix', utc=True).dt.tz_convert(
                eastern).dt.tz_localize(None)
            prices = prices.rename(columns={
                'tick_volume': 'volume',
            })
            prices.columns = prices.columns.str.lower()
            return prices
