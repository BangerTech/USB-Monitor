"""
CSS-Styles für die USB-Monitor Benutzeroberfläche.
"""

from typing import Dict, Any
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings


class Styles:
    """CSS-Styles für die moderne macOS-ähnliche Benutzeroberfläche."""
    
    @staticmethod
    def get_current_theme() -> str:
        """Ermittelt das aktuelle Theme (dark/light/auto)."""
        settings = QSettings()
        return settings.value("theme", "auto")
    
    @staticmethod
    def set_theme(theme: str) -> None:
        """Setzt das Theme (dark/light/auto)."""
        settings = QSettings()
        settings.setValue("theme", theme)
    
    @staticmethod
    def is_dark_theme() -> bool:
        """Prüft, ob Dark Theme aktiv ist."""
        theme = Styles.get_current_theme()
        if theme == "dark":
            return True
        elif theme == "light":
            return False
        else:  # auto
            # System-Theme erkennen
            app = QApplication.instance()
            if app:
                palette = app.palette()
                # Wenn Hintergrund dunkler als Text ist, dann Dark Theme
                bg_color = palette.color(palette.ColorRole.Window)
                return bg_color.lightness() < 128
            return False
    
    @staticmethod
    def get_main_stylesheet() -> str:
        """Gibt das Haupt-Stylesheet zurück."""
        if Styles.is_dark_theme():
            return Styles.get_dark_theme()
        else:
            return Styles.get_light_theme()
    
    @staticmethod
    def get_dark_theme() -> str:
        """Gibt die CSS-Styles für das Dark Theme zurück."""
        return """
        /* Dark Theme - macOS Style */
        QMainWindow {
            background-color: #2D2D30;
            color: #FFFFFF;
        }
        
        QWidget {
            background-color: #2D2D30;
            color: #FFFFFF;
            font-family: "SF Pro Display", "Segoe UI", sans-serif;
            font-size: 12px;
        }
        
        /* Menüleiste */
        QMenuBar {
            background-color: #3E3E42;
            color: #FFFFFF;
            border: none;
            padding: 4px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
        }
        
        QMenuBar::item:selected {
            background-color: #007ACC;
        }
        
        QMenu {
            background-color: #3E3E42;
            color: #FFFFFF;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 8px 16px;
            border-radius: 4px;
        }
        
        QMenu::item:selected {
            background-color: #007ACC;
        }
        
        /* Toolbar */
        QToolBar {
            background-color: #3E3E42;
            border: none;
            spacing: 4px;
            padding: 4px;
        }
        
        QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 6px;
            padding: 8px;
            margin: 2px;
        }
        
        QToolButton:hover {
            background-color: #4A4A4A;
            border-color: #555555;
        }
        
        QToolButton:pressed {
            background-color: #007ACC;
            border-color: #007ACC;
        }
        
        /* Statusleiste */
        QStatusBar {
            background-color: #3E3E42;
            color: #CCCCCC;
            border-top: 1px solid #555555;
            padding: 4px;
        }
        
        /* Tabs */
        QTabWidget::pane {
            border: 1px solid #555555;
            border-radius: 6px;
            background-color: #2D2D30;
        }
        
        QTabBar::tab {
            background-color: #3E3E42;
            color: #CCCCCC;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            border: 1px solid #555555;
            border-bottom: none;
        }
        
        QTabBar::tab:selected {
            background-color: #2D2D30;
            color: #FFFFFF;
            border-bottom: 1px solid #2D2D30;
        }
        
        QTabBar::tab:hover {
            background-color: #4A4A4A;
        }
        
        /* Tabellen */
        QTableView {
            background-color: #2D2D30;
            alternate-background-color: #3E3E42;
            color: #FFFFFF;
            gridline-color: #555555;
            border: 1px solid #555555;
            border-radius: 6px;
            selection-background-color: #007ACC;
        }
        
        QTableView::item {
            padding: 8px;
            border: none;
        }
        
        QTableView::item:selected {
            background-color: #007ACC;
            color: #FFFFFF;
        }
        
        QHeaderView::section {
            background-color: #3E3E42;
            color: #FFFFFF;
            padding: 8px;
            border: none;
            border-right: 1px solid #555555;
            border-bottom: 1px solid #555555;
        }
        
        QHeaderView::section:hover {
            background-color: #4A4A4A;
        }
        
        /* Listen */
        QListWidget {
            background-color: #2D2D30;
            color: #FFFFFF;
            border: 1px solid #555555;
            border-radius: 6px;
            alternate-background-color: #3E3E42;
        }
        
        QListWidget::item {
            padding: 8px;
            border: none;
            border-radius: 4px;
            margin: 2px;
        }
        
        QListWidget::item:selected {
            background-color: #007ACC;
            color: #FFFFFF;
        }
        
        QListWidget::item:hover {
            background-color: #4A4A4A;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #007ACC;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 500;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #1A8CD8;
        }
        
        QPushButton:pressed {
            background-color: #005A9E;
        }
        
        QPushButton:disabled {
            background-color: #555555;
            color: #888888;
        }
        
        QPushButton[class="secondary"] {
            background-color: #4EC9B0;
        }
        
        QPushButton[class="secondary"]:hover {
            background-color: #5ED9C0;
        }
        
        QPushButton[class="danger"] {
            background-color: #F44747;
        }
        
        QPushButton[class="danger"]:hover {
            background-color: #FF5555;
        }
        
        /* Eingabefelder */
        QLineEdit {
            background-color: #3E3E42;
            color: #FFFFFF;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 8px 12px;
            selection-background-color: #007ACC;
        }
        
        QLineEdit:focus {
            border-color: #007ACC;
        }
        
        QLineEdit:disabled {
            background-color: #2A2A2A;
            color: #888888;
        }
        
        /* Dropdown-Listen */
        QComboBox {
            background-color: #3E3E42;
            color: #FFFFFF;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 8px 12px;
            min-height: 20px;
        }
        
        QComboBox:hover {
            border-color: #007ACC;
        }
        
        QComboBox:focus {
            border-color: #007ACC;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #FFFFFF;
            margin-right: 5px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #3E3E42;
            color: #FFFFFF;
            border: 1px solid #555555;
            border-radius: 6px;
            selection-background-color: #007ACC;
        }
        
        /* Checkboxen */
        QCheckBox {
            color: #FFFFFF;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #555555;
            border-radius: 4px;
            background-color: #3E3E42;
        }
        
        QCheckBox::indicator:checked {
            background-color: #007ACC;
            border-color: #007ACC;
        }
        
        QCheckBox::indicator:checked::after {
            content: "✓";
            color: #FFFFFF;
            font-weight: bold;
            font-size: 14px;
        }
        
        /* Radio Buttons */
        QRadioButton {
            color: #FFFFFF;
            spacing: 8px;
        }
        
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #555555;
            border-radius: 9px;
            background-color: #3E3E42;
        }
        
        QRadioButton::indicator:checked {
            background-color: #007ACC;
            border-color: #007ACC;
        }
        
        QRadioButton::indicator:checked::after {
            content: "";
            width: 8px;
            height: 8px;
            border-radius: 4px;
            background-color: #FFFFFF;
            margin: 3px;
        }
        
        /* Scrollbars */
        QScrollBar:vertical {
            background-color: #3E3E42;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #666666;
        }
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #3E3E42;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #555555;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #666666;
        }
        
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* Gruppenboxen */
        QGroupBox {
            font-weight: bold;
            border: 1px solid #555555;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 8px;
            color: #FFFFFF;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            color: #CCCCCC;
        }
        
        /* Splitter */
        QSplitter::handle {
            background-color: #555555;
        }
        
        QSplitter::handle:horizontal {
            width: 2px;
        }
        
        QSplitter::handle:vertical {
            height: 2px;
        }
        
        /* Progress Bar */
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 6px;
            text-align: center;
            background-color: #3E3E42;
            color: #FFFFFF;
        }
        
        QProgressBar::chunk {
            background-color: #007ACC;
            border-radius: 5px;
        }
        
        /* Slider */
        QSlider::groove:horizontal {
            border: 1px solid #555555;
            height: 8px;
            background-color: #3E3E42;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background-color: #007ACC;
            border: 1px solid #007ACC;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        
        QSlider::handle:horizontal:hover {
            background-color: #1A8CD8;
        }
        
        /* Spinbox */
        QSpinBox {
            background-color: #3E3E42;
            color: #FFFFFF;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 8px 12px;
        }
        
        QSpinBox::up-button,
        QSpinBox::down-button {
            background-color: #4A4A4A;
            border: none;
            border-radius: 3px;
            margin: 1px;
        }
        
        QSpinBox::up-button:hover,
        QSpinBox::down-button:hover {
            background-color: #555555;
        }
        
        /* Tree Widget */
        QTreeWidget {
            background-color: #2D2D30;
            color: #FFFFFF;
            border: 1px solid #555555;
            border-radius: 6px;
            alternate-background-color: #3E3E42;
        }
        
        QTreeWidget::item {
            padding: 4px;
            border: none;
        }
        
        QTreeWidget::item:selected {
            background-color: #007ACC;
            color: #FFFFFF;
        }
        
        QTreeWidget::item:hover {
            background-color: #4A4A4A;
        }
        
        /* Dock Widget */
        QDockWidget {
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }
        
        QDockWidget::title {
            background-color: #3E3E42;
            color: #FFFFFF;
            padding: 6px;
            border: 1px solid #555555;
            border-bottom: none;
        }
        
        /* Tool Tips */
        QToolTip {
            background-color: #3E3E42;
            color: #FFFFFF;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 8px;
        }
        
        /* Context Menu */
        QMenu {
            background-color: #3E3E42;
            color: #FFFFFF;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 4px;
        }
        
        QMenu::separator {
            height: 1px;
            background-color: #555555;
            margin: 4px 0;
        }
        
        /* Dialog Buttons */
        QDialogButtonBox QPushButton {
            min-width: 80px;
        }
        
        /* File Dialog */
        QFileDialog {
            background-color: #2D2D30;
            color: #FFFFFF;
        }
        
        QFileDialog QListView,
        QFileDialog QTreeView {
            background-color: #2D2D30;
            color: #FFFFFF;
            alternate-background-color: #3E3E42;
        }
        
        /* Message Box */
        QMessageBox {
            background-color: #2D2D30;
            color: #FFFFFF;
        }
        
        QMessageBox QPushButton {
            min-width: 80px;
        }
        """
    
    @staticmethod
    def get_light_theme() -> str:
        """Gibt die CSS-Styles für das Light Theme zurück."""
        return """
        /* Light Theme - macOS Style */
        QMainWindow {
            background-color: #FFFFFF;
            color: #000000;
        }
        
        QWidget {
            background-color: #FFFFFF;
            color: #000000;
            font-family: "SF Pro Display", "Segoe UI", sans-serif;
            font-size: 12px;
        }
        
        /* Menüleiste */
        QMenuBar {
            background-color: #F5F5F5;
            color: #000000;
            border: none;
            padding: 4px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
        }
        
        QMenuBar::item:selected {
            background-color: #007ACC;
            color: #FFFFFF;
        }
        
        QMenu {
            background-color: #F5F5F5;
            color: #000000;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 8px 16px;
            border-radius: 4px;
        }
        
        QMenu::item:selected {
            background-color: #007ACC;
            color: #FFFFFF;
        }
        
        /* Toolbar */
        QToolBar {
            background-color: #F5F5F5;
            border: none;
            spacing: 4px;
            padding: 4px;
        }
        
        QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 6px;
            padding: 8px;
            margin: 2px;
        }
        
        QToolButton:hover {
            background-color: #E5E5E5;
            border-color: #CCCCCC;
        }
        
        QToolButton:pressed {
            background-color: #007ACC;
            border-color: #007ACC;
            color: #FFFFFF;
        }
        
        /* Statusleiste */
        QStatusBar {
            background-color: #F5F5F5;
            color: #666666;
            border-top: 1px solid #CCCCCC;
            padding: 4px;
        }
        
        /* Tabs */
        QTabWidget::pane {
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            background-color: #FFFFFF;
        }
        
        QTabBar::tab {
            background-color: #F5F5F5;
            color: #666666;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            border: 1px solid #CCCCCC;
            border-bottom: none;
        }
        
        QTabBar::tab:selected {
            background-color: #FFFFFF;
            color: #000000;
            border-bottom: 1px solid #FFFFFF;
        }
        
        QTabBar::tab:hover {
            background-color: #E5E5E5;
        }
        
        /* Tabellen */
        QTableView {
            background-color: #FFFFFF;
            alternate-background-color: #F8F8F8;
            color: #000000;
            gridline-color: #CCCCCC;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            selection-background-color: #007ACC;
            selection-color: #FFFFFF;
        }
        
        QTableView::item {
            padding: 8px;
            border: none;
        }
        
        QTableView::item:selected {
            background-color: #007ACC;
            color: #FFFFFF;
        }
        
        QHeaderView::section {
            background-color: #F5F5F5;
            color: #000000;
            padding: 8px;
            border: none;
            border-right: 1px solid #CCCCCC;
            border-bottom: 1px solid #CCCCCC;
        }
        
        QHeaderView::section:hover {
            background-color: #E5E5E5;
        }
        
        /* Listen */
        QListWidget {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            alternate-background-color: #F8F8F8;
        }
        
        QListWidget::item {
            padding: 8px;
            border: none;
            border-radius: 4px;
            margin: 2px;
        }
        
        QListWidget::item:selected {
            background-color: #007ACC;
            color: #FFFFFF;
        }
        
        QListWidget::item:hover {
            background-color: #E5E5E5;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #007ACC;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 500;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #1A8CD8;
        }
        
        QPushButton:pressed {
            background-color: #005A9E;
        }
        
        QPushButton:disabled {
            background-color: #CCCCCC;
            color: #888888;
        }
        
        QPushButton[class="secondary"] {
            background-color: #4EC9B0;
        }
        
        QPushButton[class="secondary"]:hover {
            background-color: #5ED9C0;
        }
        
        QPushButton[class="danger"] {
            background-color: #F44747;
        }
        
        QPushButton[class="danger"]:hover {
            background-color: #FF5555;
        }
        
        /* Eingabefelder */
        QLineEdit {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            padding: 8px 12px;
            selection-background-color: #007ACC;
        }
        
        QLineEdit:focus {
            border-color: #007ACC;
        }
        
        QLineEdit:disabled {
            background-color: #F5F5F5;
            color: #888888;
        }
        
        /* Dropdown-Listen */
        QComboBox {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            padding: 8px 12px;
            min-height: 20px;
        }
        
        QComboBox:hover {
            border-color: #007ACC;
        }
        
        QComboBox:focus {
            border-color: #007ACC;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #000000;
            margin-right: 5px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            selection-background-color: #007ACC;
            selection-color: #FFFFFF;
        }
        
        /* Checkboxen */
        QCheckBox {
            color: #000000;
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #CCCCCC;
            border-radius: 4px;
            background-color: #FFFFFF;
        }
        
        QCheckBox::indicator:checked {
            background-color: #007ACC;
            border-color: #007ACC;
        }
        
        QCheckBox::indicator:checked::after {
            content: "✓";
            color: #FFFFFF;
            font-weight: bold;
            font-size: 14px;
        }
        
        /* Radio Buttons */
        QRadioButton {
            color: #000000;
            spacing: 8px;
        }
        
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #CCCCCC;
            border-radius: 9px;
            background-color: #FFFFFF;
        }
        
        QRadioButton::indicator:checked {
            background-color: #007ACC;
            border-color: #007ACC;
        }
        
        QRadioButton::indicator:checked::after {
            content: "";
            width: 8px;
            height: 8px;
            border-radius: 4px;
            background-color: #FFFFFF;
            margin: 3px;
        }
        
        /* Scrollbars */
        QScrollBar:vertical {
            background-color: #F5F5F5;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #CCCCCC;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #BBBBBB;
        }
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #F5F5F5;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #CCCCCC;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #BBBBBB;
        }
        
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* Gruppenboxen */
        QGroupBox {
            font-weight: bold;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 8px;
            color: #000000;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
            color: #666666;
        }
        
        /* Splitter */
        QSplitter::handle {
            background-color: #CCCCCC;
        }
        
        QSplitter::handle:horizontal {
            width: 2px;
        }
        
        QSplitter::handle:vertical {
            height: 2px;
        }
        
        /* Progress Bar */
        QProgressBar {
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            text-align: center;
            background-color: #F5F5F5;
            color: #000000;
        }
        
        QProgressBar::chunk {
            background-color: #007ACC;
            border-radius: 5px;
        }
        
        /* Slider */
        QSlider::groove:horizontal {
            border: 1px solid #CCCCCC;
            height: 8px;
            background-color: #F5F5F5;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background-color: #007ACC;
            border: 1px solid #007ACC;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        
        QSlider::handle:horizontal:hover {
            background-color: #1A8CD8;
        }
        
        /* Spinbox */
        QSpinBox {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            padding: 8px 12px;
        }
        
        QSpinBox::up-button,
        QSpinBox::down-button {
            background-color: #E5E5E5;
            border: none;
            border-radius: 3px;
            margin: 1px;
        }
        
        QSpinBox::up-button:hover,
        QSpinBox::down-button:hover {
            background-color: #CCCCCC;
        }
        
        /* Tree Widget */
        QTreeWidget {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            alternate-background-color: #F8F8F8;
        }
        
        QTreeWidget::item {
            padding: 4px;
            border: none;
        }
        
        QTreeWidget::item:selected {
            background-color: #007ACC;
            color: #FFFFFF;
        }
        
        QTreeWidget::item:hover {
            background-color: #E5E5E5;
        }
        
        /* Dock Widget */
        QDockWidget {
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }
        
        QDockWidget::title {
            background-color: #F5F5F5;
            color: #000000;
            padding: 6px;
            border: 1px solid #CCCCCC;
            border-bottom: none;
        }
        
        /* Tool Tips */
        QToolTip {
            background-color: #F5F5F5;
            color: #000000;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            padding: 8px;
        }
        
        /* Context Menu */
        QMenu {
            background-color: #F5F5F5;
            color: #000000;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            padding: 4px;
        }
        
        QMenu::separator {
            height: 1px;
            background-color: #CCCCCC;
            margin: 4px 0;
        }
        
        /* Dialog Buttons */
        QDialogButtonBox QPushButton {
            min-width: 80px;
        }
        
        /* File Dialog */
        QFileDialog {
            background-color: #FFFFFF;
            color: #000000;
        }
        
        QFileDialog QListView,
        QFileDialog QTreeView {
            background-color: #FFFFFF;
            color: #000000;
            alternate-background-color: #F8F8F8;
        }
        
        /* Message Box */
        QMessageBox {
            background-color: #FFFFFF;
            color: #000000;
        }
        
        QMessageBox QPushButton {
            min-width: 80px;
        }
        """
    
    @staticmethod
    def get_theme_colors(theme: str = "dark") -> Dict[str, str]:
        """Gibt die Farben für das angegebene Theme zurück."""
        if theme == "light":
            return {
                "background": "#FFFFFF",
                "surface": "#F5F5F5",
                "primary": "#007ACC",
                "secondary": "#4EC9B0",
                "text": "#000000",
                "text_secondary": "#666666",
                "border": "#CCCCCC",
                "accent": "#007ACC",
                "error": "#F44747",
                "warning": "#FFA500",
                "success": "#4EC9B0"
            }
        else:  # dark theme
            return {
                "background": "#2D2D30",
                "surface": "#3E3E42",
                "primary": "#007ACC",
                "secondary": "#4EC9B0",
                "text": "#FFFFFF",
                "text_secondary": "#CCCCCC",
                "border": "#555555",
                "accent": "#007ACC",
                "error": "#F44747",
                "warning": "#FFA500",
                "success": "#4EC9B0"
            }
    
    @staticmethod
    def get_style_sheet(theme: str = "dark") -> str:
        """Gibt das vollständige Stylesheet für das angegebene Theme zurück."""
        if theme == "light":
            return Styles.get_light_theme()
        else:
            return Styles.get_dark_theme()
