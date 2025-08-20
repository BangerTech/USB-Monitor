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
        self.app: Optional[QApplication] = None
        self.main_window: Optional[MainWindow] = None
        self.config = Config()

    def setup_application(self) -> None:
        """Konfiguriert die PyQt6-Anwendung."""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("USB-Monitor")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("USB-Monitor")
        self.app.setOrganizationDomain("usb-monitor.com")

        # Plattformspezifische Konfiguration
        self._setup_platform_specific()
        
        # Anwendungsstil
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
        # Verschiedene Icon-Formate versuchen (nur für Windows)
        platform = PlatformUtils.get_platform()
        
        if platform == "windows":
            # Windows: ICO-Format bevorzugen
            icon_paths = [
                "assets/icons/app_icon.ico",  # Windows (bevorzugt)
                "assets/icons/app_icon.png",  # Universal
                "assets/icons/logo.png",      # Fallback
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    try:
                        icon = QIcon(icon_path)
                        if not icon.isNull():
                            self.app.setWindowIcon(icon)
                            print(f"✅ Windows App-Icon gesetzt: {icon_path}")
                            return
                    except Exception as e:
                        print(f"⚠️  Fehler beim Laden des Icons {icon_path}: {e}")
                        continue
        else:
            # macOS/Linux: Standard-Icon
            icon_path = project_root / "assets" / "icons" / "app_icon.png"
            if icon_path.exists():
                self.app.setWindowIcon(QIcon(str(icon_path)))
                print(f"✅ Standard App-Icon gesetzt: {icon_path}")
        
        # Fallback: System-Icon
        if self.app.windowIcon().isNull():
            print("⚠️  Verwende System-Icon als Fallback")
            from ui.icons import get_icon
            self.app.setWindowIcon(get_icon("usb"))

    def create_main_window(self) -> None:
        """Erstellt das Hauptfenster der Anwendung."""
        self.main_window = MainWindow(self.config)
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
    """Hauptfunktion."""
    try:
        # Anwendung erstellen und starten
        app = USBMonitorApp()
        return app.run()
        
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        return 1


if __name__ == "__main__":
    main()
