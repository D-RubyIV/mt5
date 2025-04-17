import os

ROOT_PATH = os.getcwd()


class StyleSheet:
    Q_TOAST_CSS = """
        #toast-drop-shadow-layer-1 {
        background: rgba(0, 0, 0, 3);
        border-radius: 8px;
    }

    #toast-drop-shadow-layer-2 {
        background: rgba(0, 0, 0, 5);
        border-radius: 8px;
    }

    #toast-drop-shadow-layer-3 {
        background: rgba(0, 0, 0, 6);
        border-radius: 8px;
    }

    #toast-drop-shadow-layer-4 {
        background: rgba(0, 0, 0, 9);
        border-radius: 8px;
    }

    #toast-drop-shadow-layer-5 {
        background: rgba(0, 0, 0, 10);
        border-radius: 8px;
    }

    #toast-close-button {
        background: transparent;
    }

    #toast-icon-widget {
        background: transparent;
    }
    """
    Q_DIALOG_CONFIRM_CSS = """
        QMessageBox {
            background-color: rgb(40, 44, 52);
            color: white;
            border: none;
            padding: 15px 15px;
            border-radius: 2px;
        }
        QPushButton {
            background-color: rgb(56,58,60);
            color: white;
            padding: 4px 15px;
            border-radius: 2px;
            font-size: 11px
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        """
    Q_MENU_CSS = """
        QMenu
        {   
            color: #f0f2f5;
            font: 10.5px;
            background-color: #303031;
            border-radius: 3px;
        }

        QMenu::item
        {
            color: #cfd1d5;
            background-color: #303031;
        }

        QMenu::item:selected
        {
            color: #0e0e0e;
            background-color: rgb(170,170,255);
        }

        QMenu::item:hover
        {
            color: #0e0e0e;
            background-color: rgb(170,170,255);
        }

        QMenu::separator
        {
            height: 1px;
            background-color: #565656;
            margin-left: 5px;
            margin-right: 5px;
        }

        QMenu::indicator:checked
        {
            background-color: rgb(85, 170, 255);
        }

        QMenu::indicator:unchecked
        {
            background-color: #303031;
        }

        QMenu::submenu
        {
            background-color: #303031;
            border-radius: 3px;
        }

        QMenu::submenu:pressed
        {
            background-color: rgb(170,170,255);
        }

        QMenu::submenu:hover
        {
            background-color: rgb(170,170,255);
        }

        QMenu::submenu:selected
        {
            background-color: rgb(170,170,255);
        }
        """
    APP_CSS = """
    /*initial */
* {
    margin: 0;
    padding: 0;
}
QRadioButton {
font-size: 12px;
color: #444;
}
QRadioButton::indicator {
width: 6px;
height: 6px;
border: 2px solid #555;
background-color: #fff;
}
QRadioButton::indicator:hover {
border: 2px solid #0078d7;
}
QRadioButton::indicator:checked {
background-color: #0078d7;
border: 2px solid #555;
}
QFrame {
border: none;
}
QRadioButton{
color:white
}
QScrollArea {
background-color: transparent;
}
QScrollArea   QWidget {
background-color: transparent;
}
QLabel{
color:white;
background-color: transparent;
}
QGroupBox {
border:none
}

#centralwidget {
    background-color: rgb(56,58,60);
    border: 1px solid rgb(33, 37, 43);
    border-radius: 10px;
}
#framebody {
    background-color: rgb(40, 44, 52);
    border: 1px solid rgb(33, 37, 43);
    border-radius: 10px;
}

#groupboxclientinfomation > QPushButton{
    text-align: left;

}
#twidget{
    background-color: rgb(33, 37, 43);
    border-radius: 10px;
}
#leftnavbar > QPushButton{
text-align: left;
padding-left: 12px
}
#footerprimary {
text-align: left;
}
#footerprimary QLabel{
color: rgb(229,238,248);
padding-left: 4px;
}
#frame_key_info QLabel{
background-color: rgb(124, 124, 124);
border-radius: 2px;
}
#tgprocessframe QLabel{
color: rgb(225,225,225);
}
/*CHECK BOX*/
QCheckBox{
color: rgb(202,192,204);
}
QCheckBox::indicator{
width: 28px;
height: 20px;
padding: 0px;
border: 0px;
background-color: rgba(0,0,0,0);
text-align: left;
}
QCheckBox::indicator:checked{
image: url(":/newPrefix/toggle-button-on-removebg-preview.png");
}
QCheckBox::indicator:unchecked{
image: url(":/newPrefix/toggle-button-off-removebg-preview.png");
}
QComboBox:editable {
    background: #ffffff;
}
QComboBox:on {
    padding-top: 3px;
}
QTableWidget {
    font-size: 12px
}
QTableWidget::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid black;
    border-radius: 8px;
}
QTableWidget::indicator:checked {
    border: 5px solid #005fb8;
    width: 6px;
    height: 6px;
    border-radius: 8px;
}
QPushButton {
    color: rgb(30, 30, 30);
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
    border-bottom-left-radius: 20px;
    border-bottom-right-radius: 20px;
    background-color: rgb(170, 170, 255);
    border-radius: 3px;
    padding: 4px;

    text-align: bottom;
}
QPushButton:pressed {
    padding-left: 5px;
    padding-top: 5px;
    background-color: rgba(2, 65, 118, 100);
    background-position: calc(100% - 50px)center;
}
QPushButton:hover {
    background-color: rgba(2, 65, 118, 200);
    color: rgb(255, 255, 255);
}
QTableWidget {
    border-radius: 10px;
    background-color: transparent
}
QTableWidget::item {
    border-radius: 3px;
    margin-bottom: 3px;
    margin-right: 3px;
}
QTableWidget::item:selected {
    color: rgb(255, 255, 255);
    border: 0px;
}
QScrollBar:vertical {
    width: 10px;

}
QScrollBar::handle:vertical {
    min-height: 30px;
}
QScrollBar::add-line:vertical {
    background: none;
    height: 13px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}
QScrollBar::sub-line:vertical {
    background: none;
    height: 13px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}
QScrollBar:horizontal {
    height: 13px;

}

QScrollBar::handle:horizontal {
    min-width: 30px;
}
QScrollBar::add-line:horizontal {
    background: none;
    width: 13px;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}
QScrollBar::sub-line:horizontal {
    background: none;
    width: 13px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}
#groupboxclientinfomation, #groupboxdevicekey{
    background-color: rgb(32,32,40);
    color: rgb(255, 255, 255);
    text-align: left;
    border-radius: 0px;
}
"""