import sys

import MetaTrader5 as Mt5
import pandas as pd
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from pandas import DataFrame

from lightweight_chart_python.lightweight_charts.widgets import QtChart
from util import DataUtil


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
            self.msleep(500)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


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

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.chart = QtChart(self.widget, toolbox=True)

        self.chart.layout(
            background_color="#ffffff"
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
            default=Mt5.TIMEFRAME_M15,
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

    def update_chart(self, data):
        self.chart.set(df=data, keep_drawings=True)
        self.chart.watermark("XAUUSD")

    def draw(self):
        self.show()

    def stop(self):
        self.data_thread.stop()

    def closeEvent(self, event):
        print("Close")
        self.chart.toolbox.export_drawings('draw.json')
        print(self.chart.toolbox.drawings)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = TradingView()
    view.draw()

    app.aboutToQuit.connect(view.stop)
    app.exec()
