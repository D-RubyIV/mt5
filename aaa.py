import sys
import os

# Mở port 9222 để Chrome có thể truy cập DevTools
os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '9222'

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remote Debug - QWebEngineView")
        self.resize(1200, 800)

        self.web = QWebEngineView()
        self.web.setUrl(QUrl("https://www.google.com"))
        self.setCentralWidget(self.web)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec())
