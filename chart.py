import sys

import MetaTrader5 as Mt5
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from lightweight_chart_python.lightweight_charts.widgets import QtChart
from pandas import DataFrame

from util import DataUtil


class DataUpdater(QThread):
    data_updated = pyqtSignal(DataFrame)

    def __init__(self, symbol, timeframe, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.timeframe = timeframe
        self.running = True

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


class TradingView:
    def __init__(self):
        # Khởi tạo MT5
        Mt5.initialize()
        self.login = 244519321
        self.password = "Ha19102004dzz@#"
        self.server = "Exness-MT5Trial14"
        self.authorized = Mt5.login(login=self.login, password=self.password, server=self.server)
        print("Login result:", self.authorized)

        # Tạo UI
        self.window = QMainWindow()
        self.window.resize(1400, 800)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.chart = QtChart(self.widget, toolbox=True)
        self.chart.topbar.textbox('symbol', 'XAUUSDm')
        self.chart.topbar.switcher(
            'timeframe',
            (Mt5.TIMEFRAME_M15, Mt5.TIMEFRAME_M1),
            default=Mt5.TIMEFRAME_M15,
            func=lambda chart: DataUtil.on_timeframe_selection(Mt5, chart)
        )
        self.chart.events.new_bar += self.on_new_bar

        self.layout.addWidget(self.chart.get_webview())
        self.window.setCentralWidget(self.widget)

        self.data_thread = DataUpdater(symbol="XAUUSDm", timeframe=Mt5.TIMEFRAME_M5)
        # noinspection PyUnresolvedReferences
        self.data_thread.data_updated.connect(self.update_chart)
        self.data_thread.start()

    def on_new_bar(self, chart):
        print('New bar event!')

    def update_chart(self, data):
        self.chart.set(df=data, keep_drawings=True)
        self.chart.watermark("XAUUSD")
        self.chart.toolbox.export_drawings("draw.json")

    def draw(self):
        self.window.show()

    def stop(self):
        self.data_thread.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = TradingView()
    view.draw()

    app.aboutToQuit.connect(view.stop)
    app.exec()
