APP_STYLE = """
QMainWindow { background: #f3f5f6; color: #1f2933; }
QWidget { font-family: 'Microsoft YaHei UI', 'Segoe UI'; font-size: 13px; }
QFrame#topBar { background: #ffffff; border-bottom: 1px solid #d9e0e3; }
QLabel#appTitle { color: #17212b; font-size: 20px; font-weight: 700; }
QLabel#appSubtitle { color: #6b7780; font-size: 12px; }
QLabel#userLabel { color: #425466; font-weight: 600; }
QListWidget#navigation { background: #20282c; border: none; color: #c9d2d7; padding: 12px 8px; outline: none; }
QListWidget#navigation::item { height: 42px; margin: 2px 0; padding-left: 14px; border-radius: 4px; }
QListWidget#navigation::item:hover { background: #303b40; color: #ffffff; }
QListWidget#navigation::item:selected { background: #0f766e; color: #ffffff; font-weight: 700; }
QFrame#contentPanel { background: #ffffff; border: 1px solid #dce3e6; border-radius: 8px; }
QLabel#pageTitle { color: #17212b; font-size: 18px; font-weight: 700; }
QLabel#metricValue { color: #17212b; font-size: 25px; font-weight: 700; }
QLabel#metricCaption { color: #70808a; font-size: 12px; }
QLabel#serviceError { color: #b42318; font-size: 12px; }
QFrame#metricCard { background: #ffffff; border: 1px solid #dce3e6; border-radius: 8px; }
QPushButton { background: #ffffff; color: #263238; border: 1px solid #bcc9ce; border-radius: 7px; min-height: 34px; padding: 0 14px; font-weight: 600; }
QPushButton:hover { background: #f1f5f4; border-color: #0f766e; }
QPushButton:pressed { background: #dcece8; }
QPushButton#primaryButton { background: #0f766e; color: #ffffff; border-color: #0f766e; }
QPushButton#primaryButton:hover { background: #0b625b; }
QPushButton#dangerButton { color: #b42318; border-color: #e6b8b2; }
QPushButton#signOutButton { color: #425466; border-color: #d5dfe2; min-height: 30px; padding: 0 12px; margin-left: 10px; }
QPushButton#signOutButton:hover { color: #b42318; border-color: #e6b8b2; background: #fff7f6; }
QTableWidget { background: #ffffff; alternate-background-color: #f7f9fa; gridline-color: #e3e9eb; border: 1px solid #dce3e6; border-radius: 8px; selection-background-color: #e5f3f0; selection-color: #163833; }
QTableWidget::item { padding: 0 8px; border: none; }
QTableWidget::item:selected { background: #e5f3f0; color: #163833; border-top: 1px solid #a8d7cd; border-bottom: 1px solid #a8d7cd; }
QTableWidget::item:focus { outline: none; }
QHeaderView::section { background: #f1f4f5; color: #52616b; border: none; border-bottom: 1px solid #dce3e6; padding: 9px 8px; font-weight: 700; text-align: center; }
QLineEdit, QSpinBox, QDateTimeEdit { background: #ffffff; border: 1px solid #bfcbd0; border-radius: 7px; min-height: 33px; padding: 0 10px; selection-background-color: #0f766e; }
QLineEdit:focus, QSpinBox:focus, QDateTimeEdit:focus { border: 2px solid #0f766e; }
QComboBox { background: #ffffff; color: #17212b; border: 1px solid #bfcbd0; border-radius: 7px; min-height: 33px; padding: 0 38px 0 10px; }
QComboBox:hover { border-color: #6d8d88; background: #fbfdfd; }
QComboBox:focus, QComboBox:on { border: 2px solid #0f766e; background: #ffffff; }
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 32px; border: none; border-left: 1px solid #dce3e6; border-top-right-radius: 7px; border-bottom-right-radius: 7px; }
QComboBox QAbstractItemView { background: #ffffff; color: #263238; border: 1px solid #b7c9c5; border-radius: 7px; outline: none; padding: 5px; selection-background-color: #dcefe9; selection-color: #0b504a; }
QComboBox QAbstractItemView::item { min-height: 30px; padding: 0 10px; border-radius: 4px; }
QComboBox QAbstractItemView::item:hover { background: #edf6f3; }
QDateTimeEdit::drop-down { width: 32px; border: none; border-left: 1px solid #dce3e6; border-top-right-radius: 7px; border-bottom-right-radius: 7px; }
QCalendarWidget QWidget { background: #ffffff; color: #263238; }
QCalendarWidget QToolButton { color: #1f4f49; background: transparent; border: none; border-radius: 5px; min-height: 28px; padding: 0 8px; font-weight: 700; }
QCalendarWidget QToolButton:hover { background: #eaf4f1; }
QCalendarWidget QMenu { background: #ffffff; border: 1px solid #c6d7d3; }
QCalendarWidget QSpinBox { background: #ffffff; border: none; min-height: 26px; }
QCalendarWidget QAbstractItemView:enabled { color: #263238; selection-background-color: #0f766e; selection-color: #ffffff; outline: none; }
QCalendarWidget QAbstractItemView:disabled { color: #b0bcc2; }
QCheckBox { spacing: 7px; color: #37474f; }
QCheckBox#autoStartToggle { font-weight: 600; color: #52616b; spacing: 8px; }
QCheckBox#autoStartToggle::indicator { width: 34px; height: 18px; border-radius: 9px; background: #c4d0d3; }
QCheckBox#autoStartToggle::indicator:checked { background: #0f766e; }
QScrollBar:vertical { width: 10px; background: transparent; }
QScrollBar::handle:vertical { background: #b8c3c8; min-height: 28px; border-radius: 5px; }
"""
