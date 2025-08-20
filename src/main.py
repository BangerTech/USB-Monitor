#!/usr/bin/env python3
"""
USB-Monitor - Hauptanwendung
Überwacht USB-Geräte und COM-Ports in Echtzeit.
"""

import sys
import os
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Projektpfad hinzufügen
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ui.main_window import MainWindow
from src.utils.config import Config


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

        # App-Icon explizit setzen
        self._set_application_icon()

        # Anwendungseigenschaften
        self.app.setQuitOnLastWindowClosed(True)

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

    def _set_application_icon(self) -> None:
        """Setzt das Anwendungsicon explizit."""
        # Verschiedene Icon-Formate versuchen
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
                        print(f"✅ App-Icon gesetzt: {icon_path}")
                        return
                except Exception as e:
                    print(f"⚠️  Fehler beim Laden des Icons {icon_path}: {e}")
                    continue
        
        # Fallback: System-Icon
        print("⚠️  Kein benutzerdefiniertes Icon gefunden, verwende System-Icon")
        from src.ui.icons import get_icon
        self.app.setWindowIcon(get_icon("usb"))

    def create_main_window(self) -> None:
        """Erstellt das Hauptfenster."""
        self.main_window = MainWindow(self.config)

    def run(self) -> int:
        """Startet die Anwendung."""
        try:
            # Anwendung einrichten
            self.setup_application()
            
            # Hauptfenster erstellen
            self.create_main_window()
            
            # Fenster anzeigen
            self.main_window.show()
            
            # Event-Loop starten
            return self.app.exec()
            
        except Exception as e:
            print(f"❌ Fehler beim Starten der Anwendung: {e}")
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
    # Import hier, da es von der Pfad-Konfiguration abhängt
    from src.utils.platform_utils import PlatformUtils
    
    exit_code = main()
    sys.exit(exit_code)
