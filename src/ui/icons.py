"""
Icon-Management für USB-Monitor.
Unterstützt native Icons für Windows und macOS.
"""

from typing import Dict, Optional
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QStyle
from utils.platform_utils import PlatformUtils


class IconManager:
    """Verwaltet Icons für die Anwendung."""
    
    _instance: Optional['IconManager'] = None
    _icons: Dict[str, QIcon] = {}
    
    def __new__(cls) -> 'IconManager':
        """Singleton-Pattern für Icon-Manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialisiert den Icon-Manager."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._platform = PlatformUtils.get_platform()
            self._load_system_icons()
    
    def _load_system_icons(self) -> None:
        """Lädt plattformspezifische System-Icons."""
        app = QApplication.instance()
        if not app:
            return
        
        style = app.style()
        
        # Standard System-Icons laden
        self._icons.update({
            # Allgemeine Icons
            "refresh": style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload),
            "export": style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton),
            "import": style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton),
            "settings": style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon),
            "help": style.standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton),
            "info": style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation),
            "warning": style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning),
            "error": style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical),
            "close": style.standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton),
            
            # Datei-Icons
            "folder": style.standardIcon(QStyle.StandardPixmap.SP_DirIcon),
            "file": style.standardIcon(QStyle.StandardPixmap.SP_FileIcon),
            "save": style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton),
            "open": style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton),
            
            # Medien-Icons
            "play": style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay),
            "pause": style.standardIcon(QStyle.StandardPixmap.SP_MediaPause),
            "stop": style.standardIcon(QStyle.StandardPixmap.SP_MediaStop),
            
            # Navigation
            "back": style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack),
            "forward": style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward),
            "up": style.standardIcon(QStyle.StandardPixmap.SP_ArrowUp),
            "down": style.standardIcon(QStyle.StandardPixmap.SP_ArrowDown),
        })
        
        # Plattformspezifische Icons erstellen
        self._create_custom_icons()
    
    def _create_custom_icons(self) -> None:
        """Erstellt benutzerdefinierte Icons."""
        # USB-Icon
        self._icons["usb"] = self._create_usb_icon()
        
        # COM-Port-Icon
        self._icons["com_port"] = self._create_com_port_icon()
        
        # Verbindungs-Icons
        self._icons["connected"] = self._create_status_icon("connected")
        self._icons["disconnected"] = self._create_status_icon("disconnected")
        self._icons["available"] = self._create_status_icon("available")
        self._icons["unavailable"] = self._create_status_icon("unavailable")
        
        # Gerätetyp-Icons
        self._icons["keyboard"] = self._create_device_icon("keyboard")
        self._icons["mouse"] = self._create_device_icon("mouse")
        self._icons["audio"] = self._create_device_icon("audio")
        self._icons["storage"] = self._create_device_icon("storage")
        self._icons["bluetooth"] = self._create_device_icon("bluetooth")
        
        # Theme-Icons
        self._icons["dark_theme"] = self._create_theme_icon("dark")
        self._icons["light_theme"] = self._create_theme_icon("light")
        self._icons["auto_theme"] = self._create_theme_icon("auto")
    
    def _create_usb_icon(self) -> QIcon:
        """Erstellt ein USB-Icon."""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # USB-Symbol zeichnen
        color = self._get_icon_color()
        painter.setPen(color)
        painter.setBrush(color)
        
        # USB-Stecker
        painter.drawRect(8, 4, 8, 16)
        painter.drawRect(6, 8, 4, 8)
        
        # USB-Symbole
        painter.drawEllipse(10, 6, 2, 2)
        painter.drawRect(13, 6, 2, 2)
        painter.drawEllipse(10, 16, 2, 2)
        painter.drawRect(13, 16, 2, 2)
        
        painter.end()
        return QIcon(pixmap)
    
    def _create_com_port_icon(self) -> QIcon:
        """Erstellt ein COM-Port-Icon."""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        color = self._get_icon_color()
        painter.setPen(color)
        painter.setBrush(color)
        
        # Serieller Port
        painter.drawRect(4, 8, 16, 8)
        painter.drawRect(2, 10, 4, 4)
        painter.drawRect(18, 10, 4, 4)
        
        # Pins
        for i in range(3):
            painter.drawRect(6 + i * 4, 9, 2, 6)
        
        painter.end()
        return QIcon(pixmap)
    
    def _create_status_icon(self, status: str) -> QIcon:
        """Erstellt ein Status-Icon."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Farbe je nach Status
        if status in ["connected", "available"]:
            color = QColor(76, 175, 80)  # Grün
        else:
            color = QColor(244, 67, 54)  # Rot
        
        painter.setBrush(color)
        painter.setPen(color)
        painter.drawEllipse(2, 2, 12, 12)
        
        painter.end()
        return QIcon(pixmap)
    
    def _create_device_icon(self, device_type: str) -> QIcon:
        """Erstellt ein Gerätetyp-Icon."""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        color = self._get_icon_color()
        painter.setPen(color)
        painter.setBrush(color)
        
        if device_type == "keyboard":
            # Tastatur
            painter.drawRect(2, 10, 20, 8)
            for i in range(5):
                for j in range(3):
                    painter.drawRect(4 + i * 3, 12 + j * 2, 2, 1)
        
        elif device_type == "mouse":
            # Maus
            painter.drawEllipse(8, 6, 8, 12)
            painter.drawRect(10, 8, 2, 4)
            painter.drawRect(12, 8, 2, 4)
        
        elif device_type == "audio":
            # Lautsprecher
            painter.drawRect(6, 8, 4, 8)
            painter.drawPolygon([
                (10, 8), (16, 4), (16, 20), (10, 16)
            ])
        
        elif device_type == "storage":
            # Festplatte
            painter.drawRect(4, 8, 16, 8)
            painter.drawEllipse(6, 10, 4, 4)
        
        elif device_type == "bluetooth":
            # Bluetooth-Symbol
            painter.drawLine(12, 4, 12, 20)
            painter.drawLine(8, 8, 16, 16)
            painter.drawLine(8, 16, 16, 8)
            painter.drawLine(12, 4, 16, 8)
            painter.drawLine(12, 20, 16, 16)
        
        painter.end()
        return QIcon(pixmap)
    
    def _create_theme_icon(self, theme: str) -> QIcon:
        """Erstellt ein Theme-Icon."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if theme == "dark":
            # Mond
            painter.setBrush(QColor(255, 255, 255))
            painter.setPen(QColor(255, 255, 255))
            painter.drawEllipse(6, 2, 12, 12)
            painter.setBrush(QColor(0, 0, 0, 0))
            painter.drawEllipse(10, 2, 12, 12)
        
        elif theme == "light":
            # Sonne
            painter.setBrush(QColor(255, 193, 7))
            painter.setPen(QColor(255, 193, 7))
            painter.drawEllipse(6, 6, 8, 8)
            # Sonnenstrahlen
            for i in range(8):
                angle = i * 45
                painter.drawLine(10, 10, 
                               10 + 8 * (1 if i % 2 else 0.7), 
                               10 + 8 * (1 if i % 2 else 0.7))
        
        else:  # auto
            # Halb-Mond/Sonne
            painter.setBrush(QColor(128, 128, 128))
            painter.setPen(QColor(128, 128, 128))
            painter.drawEllipse(4, 4, 12, 12)
            painter.setBrush(QColor(255, 255, 255))
            painter.drawPie(4, 4, 12, 12, 0, 180 * 16)
        
        painter.end()
        return QIcon(pixmap)
    
    def _get_icon_color(self) -> QColor:
        """Ermittelt die passende Icon-Farbe basierend auf dem Theme."""
        app = QApplication.instance()
        if app:
            palette = app.palette()
            return palette.color(palette.ColorRole.Text)
        return QColor(0, 0, 0)
    
    def get_icon(self, name: str, size: QSize = QSize(24, 24)) -> QIcon:
        """Gibt ein Icon zurück."""
        if name in self._icons:
            icon = self._icons[name]
            # Icon auf gewünschte Größe skalieren
            if not size.isEmpty():
                pixmap = icon.pixmap(size)
                return QIcon(pixmap)
            return icon
        
        # Fallback: Standard-Icon
        app = QApplication.instance()
        if app:
            return app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        
        return QIcon()
    
    def get_device_icon(self, device_name: str, device_type: str = "") -> QIcon:
        """Gibt ein passendes Icon für ein Gerät zurück."""
        device_name_lower = device_name.lower()
        device_type_lower = device_type.lower()
        
        # Nach Gerätetyp
        if "keyboard" in device_type_lower or "keyboard" in device_name_lower:
            return self.get_icon("keyboard")
        elif "mouse" in device_type_lower or "mouse" in device_name_lower:
            return self.get_icon("mouse")
        elif "audio" in device_type_lower or "codec" in device_name_lower or "sound" in device_name_lower:
            return self.get_icon("audio")
        elif "storage" in device_type_lower or "card reader" in device_name_lower or "disk" in device_name_lower:
            return self.get_icon("storage")
        elif "bluetooth" in device_type_lower or "bluetooth" in device_name_lower:
            return self.get_icon("bluetooth")
        else:
            return self.get_icon("usb")
    
    def get_status_icon(self, is_connected: bool, is_available: bool = True) -> QIcon:
        """Gibt ein Status-Icon zurück."""
        if is_connected and is_available:
            return self.get_icon("connected")
        elif is_available:
            return self.get_icon("available")
        elif is_connected:
            return self.get_icon("disconnected")
        else:
            return self.get_icon("unavailable")
    
    @classmethod
    def instance(cls) -> 'IconManager':
        """Gibt die Icon-Manager-Instanz zurück."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Globale Instanz
icon_manager = IconManager.instance()


def get_icon(name: str, size: QSize = QSize(24, 24)) -> QIcon:
    """Shortcut-Funktion zum Abrufen von Icons."""
    return icon_manager.get_icon(name, size)


def get_device_icon(device_name: str, device_type: str = "") -> QIcon:
    """Shortcut-Funktion zum Abrufen von Geräte-Icons."""
    return icon_manager.get_device_icon(device_name, device_type)


def get_status_icon(is_connected: bool, is_available: bool = True) -> QIcon:
    """Shortcut-Funktion zum Abrufen von Status-Icons."""
    return icon_manager.get_status_icon(is_connected, is_available)
