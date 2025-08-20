"""
Hauptfenster für USB-Monitor.
"""

import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget,
    QMenuBar, QMenu, QToolBar, QStatusBar, QMessageBox, QFileDialog,
    QSplitter, QLabel, QFrame, QApplication, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon, QKeySequence, QFont, QPixmap, QAction

from core.device_monitor import DeviceMonitor, USBDevice
from core.port_monitor import PortMonitor, COMPort
from utils.config import Config
from utils.platform_utils import PlatformUtils
from ui.styles import Styles
from ui.device_panel import DevicePanel
from ui.port_panel import PortPanel
from ui.icons import get_icon


class MainWindow(QMainWindow):
    """Hauptfenster der USB-Monitor Anwendung."""
    
    # Signale
    device_connected = pyqtSignal(USBDevice)
    device_disconnected = pyqtSignal(USBDevice)
    port_added = pyqtSignal(COMPort)
    port_status_changed = pyqtSignal(COMPort)
    
    def __init__(self):
        """Initialisiert das Hauptfenster."""
        super().__init__()
        
        # Konfiguration laden
        self.config = Config()
        
        # Monitore initialisieren
        self.device_monitor = DeviceMonitor(self.config)
        self.port_monitor = PortMonitor(self.config)
        
        # UI-Komponenten
        self.central_widget: Optional[QWidget] = None
        self.tab_widget: Optional[QTabWidget] = None
        self.device_panel: Optional[DevicePanel] = None
        self.port_panel: Optional[PortPanel] = None
        self.status_bar: Optional[QStatusBar] = None
        
        # Timer für Status-Updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        
        # Fenster-Einstellungen
        self._setup_window()
        
        # UI erstellen
        self._create_ui()
        
        # Menüs und Statusbar
        self._create_menus()
        self._create_statusbar()
        
        # Signale verbinden
        self._connect_signals()
        
        # Monitore starten
        self._start_monitoring()
        
        # Status-Timer starten
        self.status_timer.start(5000)  # Alle 5 Sekunden aktualisieren
        
        # Theme anwenden
        self._apply_theme()
        
        # Fenster-Einstellungen wiederherstellen
        self._restore_window_state()
    
    def _setup_window(self) -> None:
        """Konfiguriert das Hauptfenster."""
        self.setWindowTitle("USB-Monitor")
        
        # App-Icon setzen (falls vorhanden)
        icon_path = "assets/icons/app_icon.png"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Fallback: System-Icon verwenden
            self.setWindowIcon(get_icon("usb"))
        
        # Fenstergröße und Position
        window_width = self.config.get("window_width", 1200)
        window_height = self.config.get("window_height", 800)
        window_x = self.config.get("window_x", 100)
        window_y = self.config.get("window_y", 100)
        
        self.resize(window_width, window_height)
        self.move(window_x, window_y)
        
        # Fenster-Eigenschaften
        if self.config.get("maximized", False):
            self.showMaximized()
        
        # Plattformspezifische Einstellungen
        platform = PlatformUtils.get_platform()
        if platform == "macos":
            # macOS-spezifische Einstellungen
            self.setUnifiedTitleAndToolBarOnMac(True)
    
    def _create_ui(self) -> None:
        """Erstellt die Benutzeroberfläche."""
        # Zentrales Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Hauptlayout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Tab-Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        
        # USB-Geräte-Tab
        self.device_panel = DevicePanel(self.device_monitor, self.config)
        self.tab_widget.addTab(self.device_panel, "USB-Geräte")
        
        # COM-Port-Tab
        self.port_panel = PortPanel(self.port_monitor, self.config)
        self.tab_widget.addTab(self.port_panel, "COM-Ports")
        
        # Tab-Widget zum Layout hinzufügen
        main_layout.addWidget(self.tab_widget)
        
        # Status-Bar
        self._create_status_bar()
        
        main_layout.addWidget(self.status_bar)
    
    def _create_status_bar(self) -> None:
        """Erstellt die Status-Bar."""
        self.status_bar = QFrame()
        self.status_bar.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(self.status_bar)
        
        self.device_status_label = QLabel("USB-Geräte: 0/0 verbunden")
        self.port_status_label = QLabel("COM-Ports: 0/0 verfügbar")
        self.last_update_label = QLabel("Letzte Aktualisierung: --")
        
        # Theme-Toggle
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["🌙 Dark", "☀️ Light", "🔄 Auto"])
        current_theme = Styles.get_current_theme()
        if current_theme == "dark":
            self.theme_combo.setCurrentIndex(0)
        elif current_theme == "light":
            self.theme_combo.setCurrentIndex(1)
        else:
            self.theme_combo.setCurrentIndex(2)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        
        # Automatische Aktualisierung
        self.auto_refresh_cb = QCheckBox("Automatische Aktualisierung")
        self.auto_refresh_cb.setChecked(self.config.get("auto_refresh", True))
        self.auto_refresh_cb.toggled.connect(self._on_auto_refresh_changed)
        
        self.refresh_interval_combo = QComboBox()
        self.refresh_interval_combo.addItems(["1", "3", "5", "10", "30", "60"])
        self.refresh_interval_combo.setCurrentText(str(self.config.get("refresh_interval", 5)))
        self.refresh_interval_combo.currentTextChanged.connect(self._on_refresh_interval_changed)
        
        status_layout.addWidget(self.device_status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.port_status_label)
        status_layout.addStretch()
        status_layout.addWidget(QLabel("Theme:"))
        status_layout.addWidget(self.theme_combo)
        status_layout.addStretch()
        status_layout.addWidget(self.auto_refresh_cb)
        status_layout.addWidget(QLabel("Intervall (Sek.):"))
        status_layout.addWidget(self.refresh_interval_combo)
        status_layout.addStretch()
        status_layout.addWidget(self.last_update_label)
    
    def _create_menus(self) -> None:
        """Erstellt die Menüleiste."""
        menubar = self.menuBar()
        
        # Datei-Menü
        file_menu = menubar.addMenu("&Datei")
        
        # Export-Aktionen
        export_devices_action = QAction("USB-Geräte &exportieren...", self)
        export_devices_action.setIcon(get_icon("export"))
        export_devices_action.setShortcut(QKeySequence.StandardKey.Save)
        export_devices_action.triggered.connect(self._export_devices)
        file_menu.addAction(export_devices_action)
        
        export_ports_action = QAction("COM-Ports &exportieren...", self)
        export_ports_action.setIcon(get_icon("export"))
        export_ports_action.triggered.connect(self._export_ports)
        file_menu.addAction(export_ports_action)
        
        file_menu.addSeparator()
        
        # Beenden
        exit_action = QAction("&Beenden", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Bearbeiten-Menü
        edit_menu = menubar.addMenu("&Bearbeiten")
        
        # Aktualisieren
        refresh_action = QAction("&Aktualisieren", self)
        refresh_action.setIcon(get_icon("refresh"))
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self._refresh_all)
        edit_menu.addAction(refresh_action)
        
        edit_menu.addSeparator()
        
        # Einstellungen
        settings_action = QAction("&Einstellungen...", self)
        settings_action.setIcon(get_icon("settings"))
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._show_settings)
        edit_menu.addAction(settings_action)
        
        # Ansicht-Menü
        view_menu = menubar.addMenu("&Ansicht")
        
        # Theme-Aktionen
        dark_theme_action = QAction("&Dark Theme", self)
        dark_theme_action.setCheckable(True)
        dark_theme_action.triggered.connect(lambda: self._change_theme("dark"))
        view_menu.addAction(dark_theme_action)
        
        light_theme_action = QAction("&Light Theme", self)
        light_theme_action.setCheckable(True)
        light_theme_action.triggered.connect(lambda: self._change_theme("light"))
        view_menu.addAction(light_theme_action)
        
        auto_theme_action = QAction("&Automatisch", self)
        auto_theme_action.setCheckable(True)
        auto_theme_action.triggered.connect(lambda: self._change_theme("auto"))
        view_menu.addAction(auto_theme_action)
        
        # Theme-Gruppe
        theme_group = edit_menu.addAction("Theme-Gruppe")
        theme_group.setSeparator(True)
        
        # Aktuelles Theme setzen
        current_theme = self.config.get("theme", "auto")
        if current_theme == "dark":
            dark_theme_action.setChecked(True)
        elif current_theme == "light":
            light_theme_action.setChecked(True)
        else:
            auto_theme_action.setChecked(True)
        
        # Hilfe-Menü
        help_menu = menubar.addMenu("&Hilfe")
        
        # Über
        about_action = QAction("&Über USB-Monitor", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        # Über Qt
        about_qt_action = QAction("Über &Qt", self)
        about_qt_action.triggered.connect(QApplication.aboutQt)
        help_menu.addAction(about_qt_action)
    
    def _create_toolbar(self) -> None:
        """Erstellt die Toolbar."""
        # Toolbar entfernt - nur noch Tab-Navigation
        pass
    
    def _create_statusbar(self) -> None:
        """Erstellt die Statusleiste."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status-Nachrichten
        self.status_bar.showMessage("Bereit")
    
    def _connect_signals(self) -> None:
        """Verbindet alle Signale."""
        # Geräte-Signale (thread-sicher in den UI-Thread einreihen)
        self.device_monitor.on_device_connected = lambda device: QTimer.singleShot(
            0, lambda d=device: self._on_device_connected(d)
        )
        self.device_monitor.on_device_disconnected = lambda device: QTimer.singleShot(
            0, lambda d=device: self._on_device_disconnected(d)
        )
        # self.device_monitor.on_device_updated kann optional gesetzt werden
        
        # Port-Signale (thread-sicher in den UI-Thread einreihen)
        self.port_monitor.on_port_added = lambda port: QTimer.singleShot(
            0, lambda p=port: self._on_port_added(p)
        )
        self.port_monitor.on_port_status_changed = lambda port: QTimer.singleShot(
            0, lambda p=port: self._on_port_status_changed(p)
        )
        
        # Tab-Wechsel
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _start_monitoring(self) -> None:
        """Startet alle Überwachungsprozesse."""
        try:
            self.device_monitor.start_monitoring()
            self.port_monitor.start_monitoring()
            self.status_bar.showMessage("Überwachung gestartet", 3000)
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Starten der Überwachung: {e}")
    
    def _stop_monitoring(self) -> None:
        """Stoppt alle Überwachungsprozesse."""
        try:
            self.device_monitor.stop_monitoring()
            self.port_monitor.stop_monitoring()
        except Exception as e:
            print(f"Fehler beim Stoppen der Überwachung: {e}")
    
    def _update_status(self) -> None:
        """Aktualisiert den Status der Anwendung."""
        try:
            # USB-Geräte-Status
            total_devices = len(self.device_monitor.get_all_devices())
            connected_devices = len(self.device_monitor.get_connected_devices())
            self.device_status_label.setText(f"USB-Geräte: {connected_devices}/{total_devices} verbunden")
            
            # COM-Port-Status
            total_ports = len(self.port_monitor.get_all_ports())
            available_ports = len(self.port_monitor.get_available_ports())
            self.port_status_label.setText(f"COM-Ports: {available_ports}/{total_ports} verfügbar")
            
            # Letzte Aktualisierung
            current_time = datetime.now().strftime("%H:%M:%S")
            self.last_update_label.setText(f"Letzte Aktualisierung: {current_time}")
            
        except Exception as e:
            print(f"Fehler beim Aktualisieren des Status: {e}")
    
    def _on_auto_refresh_changed(self, enabled: bool) -> None:
        """Behandelt Änderungen der automatischen Aktualisierung."""
        self.config.set("auto_refresh", enabled)
        if enabled:
            self.refresh_timer.start()
        else:
            self.refresh_timer.stop()
    
    def _on_refresh_interval_changed(self, interval: str) -> None:
        """Behandelt Änderungen des Aktualisierungsintervalls."""
        try:
            interval_ms = int(interval) * 1000
            self.config.set("refresh_interval", int(interval))
            self.refresh_timer.setInterval(interval_ms)
        except ValueError:
            pass
    
    def _on_theme_changed(self, theme_text: str) -> None:
        """Wird aufgerufen, wenn sich das Theme ändert."""
        # Theme aus Text extrahieren
        if "Dark" in theme_text:
            theme = "dark"
        elif "Light" in theme_text:
            theme = "light"
        else:
            theme = "auto"
        
        # Theme speichern und anwenden
        Styles.set_theme(theme)
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        """Wendet das aktuelle Theme auf die gesamte Anwendung an."""
        stylesheet = Styles.get_main_stylesheet()
        self.setStyleSheet(stylesheet)
        
        # Theme auch auf alle Child-Widgets anwenden
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet("")  # Reset
        
        # Hauptstylesheet erneut anwenden
        QApplication.instance().setStyleSheet(stylesheet)
    
    def _on_device_connected(self, device: USBDevice) -> None:
        """Wird aufgerufen, wenn ein USB-Gerät verbunden wird."""
        self.device_connected.emit(device)
        self.status_bar.showMessage(f"USB-Gerät verbunden: {device.name}", 3000)
        
        # Benachrichtigung anzeigen (falls aktiviert)
        if self.config.get("notify_device_connect", True):
            self._show_notification("USB-Gerät verbunden", device.name)
    
    def _on_device_disconnected(self, device: USBDevice) -> None:
        """Wird aufgerufen, wenn ein USB-Gerät getrennt wird."""
        self.device_disconnected.emit(device)
        self.status_bar.showMessage(f"USB-Gerät getrennt: {device.name}", 3000)
        
        # Benachrichtigung anzeigen (falls aktiviert)
        if self.config.get("notify_device_disconnect", True):
            self._show_notification("USB-Gerät getrennt", device.name)
    
    def _on_port_added(self, port: COMPort) -> None:
        """Wird aufgerufen, wenn ein neuer COM-Port hinzugefügt wird."""
        self.port_added.emit(port)
        self.status_bar.showMessage(f"Neuer COM-Port: {port.port_name}", 3000)
    
    def _on_port_status_changed(self, port: COMPort) -> None:
        """Wird aufgerufen, wenn sich der Status eines COM-Ports ändert."""
        self.port_status_changed.emit(port)
        
        if port.is_available:
            self.status_bar.showMessage(f"COM-Port verfügbar: {port.port_name}", 3000)
        else:
            self.status_bar.showMessage(f"COM-Port nicht verfügbar: {port.port_name}", 3000)
    
    def _on_tab_changed(self, index: int) -> None:
        """Wird aufgerufen, wenn der aktive Tab gewechselt wird."""
        if index == 0:
            self.status_bar.showMessage("USB-Geräte-Übersicht")
        elif index == 1:
            self.status_bar.showMessage("COM-Port-Übersicht")
    
    def _refresh_all(self) -> None:
        """Aktualisiert alle Daten."""
        try:
            self.device_monitor.refresh_devices()
            self.port_monitor.refresh_ports()
            self.status_bar.showMessage("Alle Daten aktualisiert", 2000)
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Aktualisieren: {e}")
    
    def _export_devices(self) -> None:
        """Exportiert die USB-Geräteliste."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "USB-Geräte exportieren",
                f"usb_devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON-Dateien (*.json);;Alle Dateien (*)"
            )
            
            if filename:
                if self.device_monitor.export_devices(filename):
                    self.status_bar.showMessage(f"USB-Geräte exportiert nach: {filename}", 3000)
                else:
                    QMessageBox.warning(self, "Fehler", "Fehler beim Exportieren der USB-Geräte")
                    
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Exportieren: {e}")
    
    def _export_ports(self) -> None:
        """Exportiert die COM-Portliste."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "COM-Ports exportieren",
                f"com_ports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON-Dateien (*.json);;Alle Dateien (*)"
            )
            
            if filename:
                if self.port_monitor.export_ports(filename):
                    self.status_bar.showMessage(f"COM-Ports exportiert nach: {filename}", 3000)
                else:
                    QMessageBox.warning(self, "Fehler", "Fehler beim Exportieren der COM-Ports")
                    
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Exportieren: {e}")
    
    def _export_all(self) -> None:
        """Exportiert alle Daten."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Alle Daten exportieren",
                f"usb_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON-Dateien (*.json);;Alle Dateien (*)"
            )
            
            if filename:
                # Alle Daten sammeln
                export_data = {
                    "export_date": datetime.now().isoformat(),
                    "usb_devices": [device.to_dict() for device in self.device_monitor.get_all_devices()],
                    "com_ports": [port.to_dict() for port in self.port_monitor.get_all_ports()],
                    "statistics": {
                        "usb_devices": self.device_monitor.get_device_statistics(),
                        "com_ports": self.port_monitor.get_port_statistics()
                    }
                }
                
                import json
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                self.status_bar.showMessage(f"Alle Daten exportiert nach: {filename}", 3000)
                
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Exportieren: {e}")
    
    def _show_settings(self) -> None:
        """Zeigt den Einstellungsdialog an."""
        # TODO: Einstellungsdialog implementieren
        QMessageBox.information(self, "Einstellungen", "Einstellungsdialog wird in einer zukünftigen Version verfügbar sein.")
    
    def _show_about(self) -> None:
        """Zeigt den Über-Dialog an."""
        about_text = """
        <h3>USB-Monitor v1.0.0</h3>
        <p>Ein modernes Programm zur Überwachung von USB-Geräten und COM-Ports.</p>
        <p><b>Features:</b></p>
        <ul>
            <li>USB-Geräte-Erkennung in Echtzeit</li>
            <li>COM-Port-Überwachung</li>
            <li>Moderne macOS-ähnliche Benutzeroberfläche</li>
            <li>Plattformübergreifend (Windows, macOS, Linux)</li>
        </ul>
        <p><b>Entwickelt mit:</b> Python, PyQt6</p>
        <p><b>Lizenz:</b> MIT</p>
        """
        
        QMessageBox.about(self, "Über USB-Monitor", about_text)
    
    def _change_theme(self, theme: str) -> None:
        """Ändert das Theme der Anwendung."""
        try:
            self.config.set("theme", theme)
            
            # Stylesheet anwenden
            if theme == "auto":
                # Automatische Theme-Erkennung
                import platform
                if platform.system() == "Darwin":  # macOS
                    current_theme = "dark" if self._is_macos_dark_mode() else "light"
                else:
                    current_theme = "light"
            else:
                current_theme = theme
            
            stylesheet = Styles.get_style_sheet(current_theme)
            self.setStyleSheet(stylesheet)
            
            self.status_bar.showMessage(f"Theme geändert zu: {theme}", 2000)
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Ändern des Themes: {e}")
    
    def _is_macos_dark_mode(self) -> bool:
        """Ermittelt, ob macOS im Dark Mode läuft."""
        try:
            import subprocess
            result = subprocess.run(["defaults", "read", "-g", "AppleInterfaceStyle"], 
                                  capture_output=True, text=True)
            return result.stdout.strip() == "Dark"
        except:
            return False
    
    def _show_notification(self, title: str, message: str) -> None:
        """Zeigt eine Benachrichtigung an."""
        # Einfache Benachrichtigung über Statusleiste
        self.status_bar.showMessage(f"{title}: {message}", 5000)
        
        # TODO: System-Benachrichtigungen implementieren
    
    def _save_window_state(self) -> None:
        """Speichert den Fensterzustand."""
        try:
            # Fenstergröße und Position
            if not self.isMaximized():
                self.config.set("window_width", self.width())
                self.config.set("window_height", self.height())
                self.config.set("window_x", self.x())
                self.config.set("window_y", self.y())
            
            # Maximiert-Status
            self.config.set("maximized", self.isMaximized())
            
        except Exception as e:
            print(f"Fehler beim Speichern des Fensterzustands: {e}")
    
    def _restore_window_state(self) -> None:
        """Stellt den Fensterzustand wieder her."""
        try:
            # Fenstergröße und Position
            window_width = self.config.get("window_width", 1200)
            window_height = self.config.get("window_height", 800)
            window_x = self.config.get("window_x", 100)
            window_y = self.config.get("window_y", 100)
            
            self.resize(window_width, window_height)
            self.move(window_x, window_y)
            
            # Maximiert-Status
            if self.config.get("maximized", False):
                self.showMaximized()
                
        except Exception as e:
            print(f"Fehler beim Wiederherstellen des Fensterzustands: {e}")
    
    def closeEvent(self, event) -> None:
        """Wird aufgerufen, wenn das Fenster geschlossen wird."""
        try:
            # Fensterzustand speichern
            self._save_window_state()
            
            # Überwachung stoppen
            self._stop_monitoring()
            
            # Event akzeptieren
            event.accept()
            
        except Exception as e:
            print(f"Fehler beim Schließen des Fensters: {e}")
            event.accept()
    
    def keyPressEvent(self, event) -> None:
        """Behandelt Tastatureingaben."""
        # F5: Aktualisieren
        if event.key() == Qt.Key.Key_F5:
            self._refresh_all()
        # Ctrl+R: Aktualisieren
        elif event.key() == Qt.Key.Key_R and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._refresh_all()
        # Ctrl+Q: Beenden
        elif event.key() == Qt.Key.Key_Q and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.close()
        else:
            super().keyPressEvent(event)
