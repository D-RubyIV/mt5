import os
import sys
from dataclasses import asdict

import MetaTrader5 as Mt5
import pandas as pd
import talib
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from pandas import DataFrame

from chart.lightweight_charts.widgets import QtChart
from model import MarkerObject
from technicals import Compute
from util import DataUtil

os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '9222'


class DataUpdater(QThread):
    data_updated = pyqtSignal(DataFrame)

    def __init__(self, chart: QtChart, parent=None):
        super().__init__(parent)
        self.symbol = chart.topbar['symbol'].value
        self.timeframe = chart.topbar['timeframe'].value
        self.running = True
        print(f"Symbol: {self.symbol}")
        print(f"timeframe: {self.timeframe}")

    def run(self):
        while self.running:
            data = DataUtil.get_bar_data(mt5=Mt5, timeframe=self.timeframe, symbol=self.symbol)
            print(type(data))
            if data is not None and not data.empty:
                # noinspection PyUnresolvedReferences
                self.data_updated.emit(data)
            self.msleep(30000)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class TradingView(QMainWindow):
    symbol = "XAUUSDm"

    def __init__(self):
        timeframes = [
            {
                "key": "1m",
                "value": Mt5.TIMEFRAME_M1
            },
            {
                "key": "5m",
                "value": Mt5.TIMEFRAME_M5
            },
            {
                "key": "15m",
                "value": Mt5.TIMEFRAME_M15
            },
            {
                "key": "1h",
                "value": Mt5.TIMEFRAME_H1
            },
            {
                "key": "4h",
                "value": Mt5.TIMEFRAME_H4
            },
        ]
        keys_timeframes = tuple(tf["key"] for tf in timeframes)
        print(keys_timeframes)
        print(type(keys_timeframes))
        super().__init__()
        self.data_thread = None
        # Khởi tạo MT5
        Mt5.initialize()
        self.login = 244519321
        self.password = "Ha19102004dzz@#"
        self.server = "Exness-MT5Trial14"
        self.authorized = Mt5.login(login=self.login, password=self.password, server=self.server)
        print("Login result:", self.authorized)

        # Tạo UI
        self.resize(1400, 800)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.chart = QtChart(self.widget, toolbox=True)

        self.chart.layout(
            background_color="#ffffff",
            text_color="#000000"
        )
        self.chart.grid(
            color="#00000033"
        )
        self.chart.candle_style(
            up_color="#4CAF50",
            down_color="#000000",
            border_down_color="#000000",
            border_up_color="#000000",

        )
        self.chart.topbar.switcher(
            'timeframe',
            (
                Mt5.TIMEFRAME_M1,
                Mt5.TIMEFRAME_M3,
                Mt5.TIMEFRAME_M5,
                Mt5.TIMEFRAME_M15,
                Mt5.TIMEFRAME_H1,
                Mt5.TIMEFRAME_H4,
                Mt5.TIMEFRAME_D1,
            ),
            default=Mt5.TIMEFRAME_H1,
            func=lambda chart: self.start_interval(chart)
        )
        self.chart.events.new_bar += self.on_new_bar
        self.chart.events.search += self.on_search

        self.chart.topbar.textbox('symbol', self.symbol)
        self.chart.toolbox.import_drawings('draw.json')
        self.chart.toolbox.load_drawings(self.chart.topbar['symbol'].value)
        self.chart.toolbox.save_drawings_under(self.chart.topbar['symbol'])

        self.layout.addWidget(self.chart.get_webview())
        self.setCentralWidget(self.widget)

        self.start_interval(chart=self.chart)

    def start_interval(self, chart):
        if self.data_thread is not None and self.data_thread.running:
            self.data_thread.stop()
        self.data_thread = DataUpdater(
            chart=chart,
            parent=self
        )
        # noinspection PyUnresolvedReferences
        self.data_thread.data_updated.connect(self.update_chart)
        self.data_thread.start()

    def on_timeframe_change(self, chart):
        self.start_interval(chart=chart)

    @staticmethod
    def calculate_sma(df, period: int = 50):
        return pd.DataFrame({
            'time': df['time'],
            f'SMA {period}': df['close'].rolling(window=period).mean()
        }).dropna()

    @staticmethod
    def on_search(self, chart, searched_string):
        self.symbol = searched_string
        print(f'Search Text: "{searched_string}" | Chart/SubChart ID: "{chart.id}"')
        chart.topbar['symbol'].set(searched_string)

    @staticmethod
    def on_new_bar(chart):
        print('New bar event!')

    @staticmethod
    def analyze(df):
        df["MA20"] = talib.SMA(df["close"], timeperiod=20)
        df["RSI14"] = talib.RSI(df["close"], timeperiod=14)
        df["K"], df["D"] = talib.STOCH(df["high"], df["low"], df["close"])
        df["CCI20"] = talib.CCI(df["high"], df["low"], df["close"], timeperiod=20)
        df["ADX"] = talib.ADX(df["high"], df["low"], df["close"])
        df["+DI"] = talib.PLUS_DI(df["high"], df["low"], df["close"])
        df["-DI"] = talib.MINUS_DI(df["high"], df["low"], df["close"])
        df["AO"] = talib.APO(df["close"])
        df["MOM"] = talib.MOM(df["close"], timeperiod=10)
        df["MACD"], df["MACD_signal"], _ = talib.MACD(df["close"])
        df["BB_upper"], df["BB_middle"], df["BB_lower"] = talib.BBANDS(df["close"])
        df["PSAR"] = talib.SAR(df["high"], df["low"])

    def update_chart(self, df):
        # Tính các chỉ báo kỹ thuật
        self.analyze(df)
        # Cập nhật biểu đồ
        self.chart.set(df=df, keep_drawings=True)

        # Danh sách indicator + trọng số
        # @formatter:off
        indicators = [
            {"name": "MA", "weight": 1.0, "compute": lambda l, p, p2: Compute.MA(l['MA20'], l['close'])},
            {"name": "RSI", "weight": 1.5, "compute": lambda l, p, p2: Compute.RSI(l['RSI14'], p['RSI14'])},
            {"name": "Stoch", "weight": 1.0, "compute": lambda l, p, p2: Compute.Stoch(l['K'], l['D'], p['K'], p['D'])},
            {"name": "CCI20", "weight": 1.0, "compute": lambda l, p, p2: Compute.CCI20(l['CCI20'], p['CCI20'])},
            {"name": "ADX", "weight": 2.0, "compute": lambda l, p, p2: Compute.ADX(l['ADX'], l['+DI'], l['-DI'], p['+DI'], p['-DI'])},
            {"name": "AO", "weight": 1.2, "compute": lambda l, p, p2: Compute.AO(l['AO'], p['AO'], p2['AO'])},
            {"name": "MOM", "weight": 1.0, "compute": lambda l, p, p2: Compute.Mom(l['MOM'], p['MOM'])},
            {"name": "MACD", "weight": 2.0, "compute": lambda l, p, p2: Compute.MACD(l['MACD'], l['MACD_signal'])},
            {"name": "BBBuy", "weight": 1.5, "compute": lambda l, p, p2: Compute.BBBuy(l['close'], l['BB_lower'])},
            {"name": "BBSell", "weight": 1.5, "compute": lambda l, p, p2: Compute.BBSell(l['close'], l['BB_upper'])},
            {"name": "PSAR", "weight": 1.0, "compute": lambda l, p, p2: Compute.PSAR(l['PSAR'], l['open'])},
        ]
        # @formatter:on
        markers: list[MarkerObject] = []
        rows = df.to_dict("records")
        for i in range(2, len(rows)):
            last = df.iloc[i]
            prev = df.iloc[i - 1]
            prev2 = df.iloc[i - 2]

            buy_score = 0
            sell_score = 0
            neutral_score = 0
            result_detail = []

            for ind in indicators:
                signal = ind["compute"](last, prev, prev2)
                weight = ind["weight"]
                result_detail.append((ind["name"], signal, weight))

                if signal == "BUY":
                    buy_score += weight
                elif signal == "SELL":
                    sell_score += weight
                else:
                    neutral_score += weight

            if buy_score > sell_score + neutral_score:
                markers.append(
                    MarkerObject(
                        text="Buy",
                        position="allow",
                        color="00FF00",
                        shape="arrow_up",
                        time=last["time"]
                    )
                )
            elif sell_score > buy_score + neutral_score:
                markers.append(
                    MarkerObject(
                        text="Sell",
                        position="below",
                        color="00FF00",
                        shape="arrow_down",
                        time=last["time"]
                    )
                )
        self.chart.marker_list( [asdict(m) for m in markers])

    def draw(self):
        self.show()

    def stop(self):
        self.data_thread.stop()

    def closeEvent(self, event):
        self.chart.toolbox.export_drawings('draw.json')
        print("Close")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = TradingView()
    view.draw()

    app.aboutToQuit.connect(view.stop)
    app.exec()
