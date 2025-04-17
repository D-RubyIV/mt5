
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QPixmap, QScreen, QIcon
from PySide6.QtWidgets import QWidget

from toast.customtoast import Toast
from toast.toastenum import ToastPreset, ToastButtonAlignment


class ToastUtil:

    @staticmethod
    def show_toast(
            parent: QWidget,
            screen: QScreen,
            delay: int = 2000,
            title: str = "Thông báo mới",
            message: str = "Chào mừng quay trở lại",
            color: str = "#292929",
            icon: QPixmap = None,
            icon_size: int = None,
            change_color: bool = False
    ):
        # Hide after 5 seconds
        toast = Toast(parent=parent)
        toast.setDuration(delay)
        toast.setTitle(title)
        toast.setText(message)
        toast.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        toast.setShowIcon(True)
        toast.setMaximumHeight(50)

        text_font = QFont()
        text_font.setPointSize(8)
        toast.setTextFont(text_font)

        title_font = QFont()
        title_font.setPointSize(9)
        title_font.setBold(True)
        toast.setTitleFont(title_font)

        toast.setMaximumOnScreen(3)
        toast.setShowDurationBar(False)
        toast.setFadeOutDuration(150)
        toast.setMinimumWidth(300)
        toast.applyPreset(ToastPreset.ERROR)
        toast.setBackgroundColor(QColor(color))
        toast.setTitleColor(QColor('#FFFFFF'))  # Default: #000000
        toast.setTextColor(QColor('#D0D0D0'))
        if color:
            toast.setIcon(icon)
        if icon_size:
            toast.setIconSize(QSize(icon_size, icon_size))
            # toast.setCloseButtonIcon(QPixmap(":/newPrefix/x.svg"))
        toast.setCloseButtonIconColor(QColor('#d7e5d4'))
        toast.setCloseButtonAlignment(ToastButtonAlignment.MIDDLE)  # Default: ToastButtonAlignment.TOP
        offset_x = screen.geometry().width() - parent.geometry().width() - parent.pos().x() + 5
        offset_y = screen.geometry().height() - parent.geometry().height() - parent.pos().y() + 5
        toast.setOffset(offset_x, offset_y)
        toast.show()
        return toast