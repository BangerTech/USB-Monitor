#!/usr/bin/env python3
"""
USB-Monitor - Hauptanwendung
Ein modernes Programm zur Überwachung von USB-Geräten und COM-Ports.
"""

import sys
import os
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication, QStyleFactory
from PyQt6.QtCore import Qt, QTranslator, QLocale
from PyQt6.QtGui import QIcon, QFont

# Projektpfade hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.main_window import MainWindow
from utils.config import Config
from utils.platform_utils import PlatformUtils


class USBMonitorApp:
    """Hauptanwendungsklasse für USB-Monitor."""
    
    def __init__(self):
        """Initialisiert die USB-Monitor Anwendung."""
        self.app: Optional[QApplication] = None
        self.main_window: Optional[MainWindow] = None
        self.config = Config()
        
    def setup_application(self) -> None:
        """Konfiguriert die QApplication mit plattformspezifischen Einstellungen."""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("USB-Monitor")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("USB-Monitor")
        self.app.setOrganizationDomain("usb-monitor.com")
        
        # Plattformspezifische Konfiguration
        self._setup_platform_specific()
        
        # Anwendungsstil setzen
        self._setup_application_style()
        
        # Übersetzungen laden
        self._setup_translations()
        
        # Fenster-Icon setzen
        self._setup_application_icon()
        
    def _setup_platform_specific(self) -> None:
        """Konfiguriert plattformspezifische Einstellungen."""
        platform = PlatformUtils.get_platform()
        
        if platform == "macos":
            # macOS-spezifische Einstellungen
            self.app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)
            # High-DPI wird automatisch von macOS gehandhabt
            pass
            
        elif platform == "windows":
            # Windows-spezifische Einstellungen
            # High-DPI wird automatisch von Windows gehandhabt
            pass
            
    def _setup_application_style(self) -> None:
        """Konfiguriert den Anwendungsstil."""
        platform = PlatformUtils.get_platform()
        
        if platform == "macos":
            # macOS-Stil verwenden
            self.app.setStyle(QStyleFactory.create("Fusion"))
        else:
            # Windows/Linux-Stil
            self.app.setStyle(QStyleFactory.create("Fusion"))
            
        # Standard-Schriftart setzen
        font = QFont("SF Pro Display" if platform == "macos" else "Segoe UI", 10)
        self.app.setFont(font)
        
    def _setup_translations(self) -> None:
        """Lädt Übersetzungsdateien."""
        translator = QTranslator()
        locale = QLocale.system().name()
        
        # Übersetzungsdatei laden (falls vorhanden)
        translation_file = f"translations/usb_monitor_{locale}.qm"
        if os.path.exists(translation_file):
            translator.load(translation_file)
            self.app.installTranslator(translator)
            
    def _setup_application_icon(self) -> None:
        """Setzt das Anwendungs-Icon."""
        icon_path = project_root / "assets" / "icons" / "app_icon.png"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))
            
    def create_main_window(self) -> None:
        """Erstellt das Hauptfenster der Anwendung."""
        self.main_window = MainWindow()
        self.main_window.show()
        
    def run(self) -> int:
        """Startet die Anwendung und gibt den Exit-Code zurück."""
        try:
            # Anwendung konfigurieren
            self.setup_application()
            
            # Hauptfenster erstellen
            self.create_main_window()
            
            # Event-Loop starten
            return self.app.exec()
            
        except Exception as e:
            print(f"Fehler beim Starten der Anwendung: {e}")
            return 1


def main():
    """Hauptfunktion der Anwendung."""
    app = USBMonitorApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
