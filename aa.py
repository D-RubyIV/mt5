import sys
import pandas as pd
import pandas_ta as ta
import yfinance as yf
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from chart.lightweight_charts.widgets import QtChart

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biểu đồ MSFT với SMA")
        self.resize(1000, 600)

        # Tạo widget chính và layout
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Tạo biểu đồ
        chart = QtChart(widget, toolbox=True)

        # Lấy dữ liệu từ yfinance
        msft = yf.Ticker("MSFT")
        df = msft.history(period="1y")
        df = df.reset_index()
        df.columns = df.columns.str.lower()

        # Tính SMA 20
        sma = df.ta.sma(length=20).to_frame()
        sma = sma.reset_index()
        sma = sma.rename(columns={"date": "time", "SMA_20": "value"})
        sma = sma.dropna()

        # Thiết lập dữ liệu cho biểu đồ
        chart.set(df)

        # Thêm đường SMA
        line = chart.create_line()
        line.set(sma)

        # Thêm watermark
        chart.watermark("MSFT")

        # Thêm biểu đồ vào layout
        layout.addWidget(chart.get_webview())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
