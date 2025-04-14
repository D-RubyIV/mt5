import os
import sys
from dataclasses import asdict

import MetaTrader5 as Mt5
import pandas as pd
from PySide6.QtGui import QAction

from constant import TimeFrames

# Đặt các tùy chọn hiển thị để in toàn bộ DataFrame
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

import talib
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QTextBrowser, QHBoxLayout, QMenu
from pandas import DataFrame
from scipy.signal import find_peaks

from chart.lightweight_charts.widgets import QtChart
from model import MarkerObject
from technicals import Compute
from util import DataUtil

os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '9222'


class DataUpdater(QThread):
    data_updated = Signal(DataFrame)

    def __init__(self, chart: QtChart, parent=None):
        super().__init__(parent)
        self.symbol = chart.topbar['symbol'].value
        self.timeframe_key = chart.topbar['timeframe_key'].value
        self.running = True
        print(f"Symbol: {self.symbol}")
        print(f"timeframe Key: {self.timeframe_key}")

    def run(self):
        while self.running:
            data = DataUtil.get_bar_data(mt5=Mt5, timeframe=TimeFrames[self.timeframe_key], symbol=self.symbol)
            print(type(data))
            if data is not None and not data.empty:
                # noinspection PyUnresolvedReferences
                self.data_updated.emit(data)
            self.msleep(30000)

    def stop(self):
        self.running = False
        self.quit()


class TradingView(QMainWindow):
    symbol = "XAUUSDm"

    def __init__(self):
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

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self._chart = QtChart(self.widget, toolbox=True, scale_candles_only=True)
        self._chart.get_webview().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._chart.get_webview().customContextMenuRequested.connect(self.show_custom_context_menu)

        self._chart.layout(
            background_color="#ffffff",
            text_color="#000000"
        )
        self._chart.grid(
            color="#00000033"
        )
        self._chart.candle_style(
            up_color="#4CAF50",
            down_color="#000000",
            border_down_color="#000000",
            border_up_color="#000000",

        )
        self._chart.topbar.menu(
            'timeframe_key',
            tuple(TimeFrames.keys()),
            default=list(TimeFrames.keys())[0],
            func=lambda chart: self.on_timeframe_change(chart)
        )
        self._chart.events.new_bar += self.on_new_bar
        self._chart.events.search += self.on_search

        self._chart.topbar.textbox('symbol', self.symbol)
        # self.chart.toolbox.import_drawings('draw.json')
        self._chart.toolbox.load_drawings(self._chart.topbar['symbol'].value)
        self._chart.toolbox.save_drawings_under(self._chart.topbar['symbol'])

        self.layout.addWidget(self._chart.get_webview())
        self.layout.addWidget(self.right_arena())
        self.setCentralWidget(self.widget)
        self.start_interval()

    def show_custom_context_menu(self, pos):
        menu = QMenu()

        action1 = QAction("Reset chart view", self)
        action1.triggered.connect(self._chart.scale_price)

        action2 = QAction("Fit chart content", self)
        action2.triggered.connect(self._chart.fit)

        menu.addAction(action1)
        menu.addAction(action2)

        # Hiển thị menu tại vị trí global
        menu.exec(self._chart.get_webview().mapToGlobal(pos))

    def right_arena(self):
        frame = QFrame(self)
        frame.setFixedWidth(300)
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        text_arena = QTextBrowser(frame)
        frame_layout.addWidget(text_arena)
        return frame

    def start_interval(self):
        if self.data_thread is not None and self.data_thread.running:
            self.data_thread.stop()
        print("Stop")
        self.data_thread = DataUpdater(
            chart=self._chart,
            parent=self
        )
        # noinspection PyUnresolvedReferences
        self.data_thread.data_updated.connect(self.update_chart)
        self.data_thread.start()

    def on_timeframe_change(self, c: QtChart):
        print("Đổi time frame")
        self._chart.clear_markers()
        self.start_interval()

    @staticmethod
    def calculate_sma(df, period: int = 50):
        return pd.DataFrame({
            'time': df['time'],
            f'SMA {period}': df['close'].rolling(window=period).mean()
        }).dropna()

    @staticmethod
    def on_search(self, searched_string):
        self.symbol = searched_string
        print(f'Search Text: "{searched_string}" | Chart/SubChart ID: "{self._chart.id}"')
        self._chart.topbar['symbol'].set(searched_string)

    @staticmethod
    def on_new_bar(chart):
        print('New bar event!')

    @staticmethod
    def detect_peaks_troughs(df, window=2):
        # Tìm các đỉnh và đáy cơ bản
        peaks, _ = find_peaks(df['high'])
        troughs, _ = find_peaks(-df['low'])

        # Thêm cột is_peak và is_trough vào DataFrame
        df['is_peak'] = False
        df['is_trough'] = False

        # Đánh dấu các đỉnh và đáy trong DataFrame
        df.loc[peaks, 'is_peak'] = True
        df.loc[troughs, 'is_trough'] = True

        # Lọc các đỉnh và đáy trong cửa sổ động
        rolling_max = df['high'].rolling(window=2 * window + 1, center=True, min_periods=1).max()
        rolling_min = df['low'].rolling(window=2 * window + 1, center=True, min_periods=1).min()

        # Kiểm tra đỉnh và đáy trong cửa sổ
        df['is_peak'] = df['is_peak'] & (df['high'] == rolling_max)
        df['is_trough'] = df['is_trough'] & (df['low'] == rolling_min)

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
        self._chart.clear_markers()
        df = df.tail(500).copy()
        df.reset_index(inplace=True)
        # Tính các chỉ báo kỹ thuật
        self.analyze(df)
        self.detect_peaks_troughs(df)
        # Cập nhật biểu đồ
        self._chart.set(
            df=df,
            keep_drawings=True,
            keep_price_scale=True
        )
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

            space = 5
            if buy_score > sell_score + space:
                score = f"{round(buy_score - (sell_score + space), 1)}"
                markers.append(
                    MarkerObject(
                        text=f"[{score}]",
                        position="below",
                        color="#86A187",
                        shape="arrow_up",
                        time=last["time"]
                    )
                )
            elif sell_score > buy_score + space:
                score = f"{round(sell_score - (buy_score + space), 1)}"
                markers.append(
                    MarkerObject(
                        text=f"[{score}]",
                        position="above",
                        color="#E35E5E",
                        shape="arrow_down",
                        time=last["time"]
                    )
                )
            if last["is_peak"]:
                markers.append(
                    MarkerObject(
                        text="",
                        position="above",
                        color="#000000",
                        shape="triangleDown",
                        time=last["time"]
                    )
                )
            elif last["is_trough"]:
                markers.append(
                    MarkerObject(
                        text="",
                        position="below",
                        color="#000000",
                        shape="triangleUp",
                        time=last["time"]
                    )
                )

        print(len(markers))
        self._chart.marker_list([asdict(m) for m in markers])

    def draw(self):
        self.show()

    def stop(self):
        self.data_thread.stop()

    def closeEvent(self, event):
        self._chart.toolbox.export_drawings('draw.json')
        print("Close")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = TradingView()
    view.draw()
    view.maximumSize()

    app.aboutToQuit.connect(view.stop)
    app.exec()
