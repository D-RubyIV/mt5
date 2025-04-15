import os
import sys
from dataclasses import asdict

import MetaTrader5 as Mt5
import pandas as pd
from PySide6.QtGui import QAction, QIcon

from constant import TimeFrames
from level import MultiLevelPeaksTroughs
from object.model import TrendObject, MarkerObject
from trend import TrendDetector

# Đặt các tùy chọn hiển thị để in toàn bộ DataFrame
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

import talib
from PySide6.QtCore import QThread, Signal, Qt, QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QHBoxLayout, QMenu, QPushButton, \
    QVBoxLayout, QSpacerItem, QSizePolicy
from pandas import DataFrame

from chart.lightweight_charts.widgets import QtChart
from util import DataUtil, get_color_for_level

os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '9222'
MIN_LEVEL_DRAW = 2


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
        self.layout_trend_card = None
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
            default=list(TimeFrames.keys())[3],
            func=lambda chart: self.on_timeframe_change(chart)
        )
        self._chart.events.new_bar += self.on_new_bar
        self._chart.events.search += self.on_search

        self._chart.topbar.textbox('symbol', self.symbol)
        # self.chart.toolbox.import_drawings('draw.json')
        self._chart.toolbox.load_drawings(self._chart.topbar['symbol'].value)
        self._chart.toolbox.save_drawings_under(self._chart.topbar['symbol'])
        ######################
        ######################
        ######################
        self.layout.addWidget(self._chart.get_webview())
        self.trend_arena([])
        self.setCentralWidget(self.widget)
        ######################
        ######################
        ######################
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

    def trend_arena(self, trends: list[TrendObject]):
        item = self.layout.itemAt(1)  # lấy item ở vị trí 0
        if item is not None:
            widget = item.widget()
            if widget is not None:
                self.layout.removeWidget(widget)
                widget.deleteLater()

        frame = QFrame(self)
        frame.setFixedWidth(300)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        for trend in trends[::-1]:
            if "Uptrend" in str(trend.trend) or "Downtrend" in str(trend.trend):
                frame_trend_card = QFrame()
                self.layout_trend_card = QHBoxLayout(frame_trend_card)
                self.layout_trend_card.setContentsMargins(0, 0, 0, 0)
                button = QPushButton(f"[{trend.level}] - {trend.trend}")
                button.setStyleSheet("background-color: transparent; border: none;")
                button.setIcon(
                    QIcon(
                        "resource/icon/down_trend.png" if "Downtrend" in str(
                            trend.trend) else "resource/icon/up_trend.png"
                    )
                )
                button.setIconSize(QSize(6 * (trend.level + 1), 6 * (trend.level + 1)))
                self.layout_trend_card.addWidget(button)

                card_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
                self.layout_trend_card.addItem(card_spacer)

                frame_layout.addWidget(frame_trend_card)
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        frame_layout.addItem(spacer)
        self.layout.insertWidget(1, frame)  # Chèn ở vị trí đầu tiên

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
    def detect_multi_level_peaks_troughs(df, max_level=3, base_window=2):
        from scipy.signal import find_peaks

        # Khởi tạo cột cấp độ
        for level in range(1, max_level + 1):
            df[f'is_peak_L{level}'] = False
            df[f'is_trough_L{level}'] = False

        # Cấp độ 1: Đỉnh/đáy nhỏ
        peaks, _ = find_peaks(df['high'])
        troughs, _ = find_peaks(-df['low'])

        df.loc[peaks, 'is_peak_L1'] = True
        df.loc[troughs, 'is_trough_L1'] = True

        # Cấp độ từ 2 trở lên
        for level in range(2, max_level + 1):
            window = base_window * level

            for i in range(window, len(df) - window):
                # Xử lý đỉnh
                if df.loc[i, f'is_peak_L{level - 1}']:
                    left = df.loc[i - window:i - 1]
                    right = df.loc[i + 1:i + window]
                    if any(left[f'is_peak_L{level - 1}']) and any(right[f'is_peak_L{level - 1}']):
                        if df.loc[i, 'high'] > max(left['high']) and df.loc[i, 'high'] > max(right['high']):
                            df.loc[i, f'is_peak_L{level}'] = True

                # Xử lý đáy
                if df.loc[i, f'is_trough_L{level - 1}']:
                    left = df.loc[i - window:i - 1]
                    right = df.loc[i + 1:i + window]
                    if any(left[f'is_trough_L{level - 1}']) and any(right[f'is_trough_L{level - 1}']):
                        if df.loc[i, 'low'] < min(left['low']) and df.loc[i, 'low'] < min(right['low']):
                            df.loc[i, f'is_trough_L{level}'] = True

        return df

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
        # df = analyze_ict_signals_with_pda(df)
        # Tính các chỉ báo kỹ thuật
        df = MultiLevelPeaksTroughs.detect_all_levels(df, max_level=100)
        # Cập nhật biểu đồ
        self._chart.set(
            df=df,
            keep_drawings=True,
            keep_price_scale=True
        )
        markers: list[MarkerObject] = []
        for i in range(2, len(df)):
            row = df.iloc[i]
            max_level = max(int(col.split('_')[-1]) for col in df.columns if col.startswith('peak_level_'))
            for level in reversed(range(1, max_level + 1)):
                if level >= MIN_LEVEL_DRAW:
                    if row.get(f"peak_level_{level}", False):
                        markers.append(
                            MarkerObject(
                                text=f"H{level}",
                                position="above",
                                color=get_color_for_level(level),
                                shape="triangleDown",
                                time=row["time"]
                            )
                        )
                        break  # Đã đánh dấu peak rồi thì không xét level thấp hơn nữa

                    elif row.get(f"trough_level_{level}", False):
                        markers.append(
                            MarkerObject(
                                text=f"L{level}",
                                position="below",
                                color=get_color_for_level(level),
                                shape="triangleUp",
                                time=row["time"]
                            )
                        )
                        break  # Đã đánh dấu trough rồi thì không xét level thấp hơn nữa
        print(df.head())
        self._chart.marker_list([asdict(m) for m in markers])
        max_level = max(int(col.split('_')[-1]) for col in df.columns if col.startswith('peak_level_'))
        trend_by_level = TrendDetector.detect_latest_trend(df, level_max=max_level)
        trend_objects = TrendDetector.print_latest_trends(trend_by_level)
        self.trend_arena(trends=trend_objects)

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
