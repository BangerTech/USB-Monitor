"""
USB-Geräte-Panel für USB-Monitor.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QLabel, QFrame, QHeaderView, QAbstractItemView, QMessageBox,
    QCheckBox, QComboBox, QLineEdit, QGroupBox, QSplitter,
    QTabWidget, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QFont, QColor, QBrush

from core.device_monitor import DeviceMonitor, USBDevice
from utils.config import Config


class USBDeviceTableModel(QAbstractTableModel):
    """Tabellenmodell für USB-Geräte."""
    
    def __init__(self, device_monitor: DeviceMonitor):
        """Initialisiert das Tabellenmodell."""
        super().__init__()
        self.device_monitor = device_monitor
        self.devices: List[USBDevice] = []
        self.filtered_devices: List[USBDevice] = []
        self.show_disconnected = True
        self.show_hubs = True
        
        # Spalten-Header
        self.headers = [
            "Status", "Name", "Hersteller", "Gerätetyp", "USB-Version",
            "Seriennummer", "Produkt-ID", "Vendor-ID", "Treiber", "Erstmals gesehen"
        ]
        
        # Geräteliste aktualisieren
        self._update_devices()
    
    def _update_devices(self) -> None:
        """Aktualisiert die Geräteliste."""
        self.devices = self.device_monitor.get_all_devices()
        self._apply_filters()
    
    def _apply_filters(self) -> None:
        """Wendet die aktuellen Filter an."""
        self.filtered_devices = []
        
        for device in self.devices:
            # Filter für getrennte Geräte
            if not self.show_disconnected and not device.is_connected:
                continue
            
            # Filter für USB-Hubs
            if not self.show_hubs and "hub" in device.device_type.lower():
                continue
            
            self.filtered_devices.append(device)
        
        # Tabelle aktualisieren
        self.layoutChanged.emit()
    
    def set_show_disconnected(self, show: bool) -> None:
        """Setzt den Filter für getrennte Geräte."""
        self.show_disconnected = show
        self._apply_filters()
    
    def set_show_hubs(self, show: bool) -> None:
        """Setzt den Filter für USB-Hubs."""
        self.show_hubs = show
        self._apply_filters()
    
    def refresh(self) -> None:
        """Aktualisiert die Geräteliste."""
        self._update_devices()
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Gibt die Anzahl der Zeilen zurück."""
        return len(self.filtered_devices)
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Gibt die Anzahl der Spalten zurück."""
        return len(self.headers)
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Gibt die Daten für den angegebenen Index zurück."""
        if not index.isValid():
            return None
        
        if index.row() >= len(self.filtered_devices):
            return None
        
        device = self.filtered_devices[index.row()]
        column = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_data(device, column)
        elif role == Qt.ItemDataRole.BackgroundRole:
            return self._get_background_color(device)
        elif role == Qt.ItemDataRole.FontRole:
            return self._get_font(device)
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Gibt die Header-Daten zurück."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if section < len(self.headers):
                return self.headers[section]
        return None
    
    def _get_display_data(self, device: USBDevice, column: int) -> str:
        """Gibt die Anzeigedaten für eine Spalte zurück."""
        if column == 0:  # Status
            return "🟢 Verbunden" if device.is_connected else "🔴 Getrennt"
        elif column == 1:  # Name
            return device.name or "Unbekannt"
        elif column == 2:  # Hersteller
            return device.manufacturer or "Unbekannt"
        elif column == 3:  # Gerätetyp
            return device.device_type or "USB Device"
        elif column == 4:  # USB-Version
            return device.usb_version or "Unbekannt"
        elif column == 5:  # Seriennummer
            return device.serial_number or "Keine"
        elif column == 6:  # Produkt-ID
            return device.product_id or "Unbekannt"
        elif column == 7:  # Vendor-ID
            return device.vendor_id or "Unbekannt"
        elif column == 8:  # Treiber
            return device.driver_version or "Unbekannt"
        elif column == 9:  # Erstmals gesehen
            if device.first_seen:
                return device.first_seen.strftime("%d.%m.%Y %H:%M")
            return "Unbekannt"
        
        return ""
    
    def _get_background_color(self, device: USBDevice) -> QBrush:
        """Gibt die Hintergrundfarbe für eine Zeile zurück."""
        if not device.is_connected:
            return QBrush(QColor(64, 64, 64))  # Dunkelgrau für getrennte Geräte
        return QBrush()
    
    def _get_font(self, device: USBDevice) -> QFont:
        """Gibt die Schriftart für eine Zeile zurück."""
        font = QFont()
        if not device.is_connected:
            font.setItalic(True)
        return font


class DevicePanel(QWidget):
    """Panel für die Anzeige und Verwaltung von USB-Geräten."""
    
    def __init__(self, device_monitor: DeviceMonitor, config: Config):
        """Initialisiert das Device Panel."""
        super().__init__()
        
        self.device_monitor = device_monitor
        self.config = config
        
        # UI-Komponenten
        self.table_model: Optional[USBDeviceTableModel] = None
        self.device_table: Optional[QTableView] = None
        self.filter_frame: Optional[QFrame] = None
        self.stats_frame: Optional[QFrame] = None
        
        # Timer für automatische Aktualisierung
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh)
        
        # UI erstellen
        self._create_ui()
        
        # Signale verbinden
        self._connect_signals()
        
        # Automatische Aktualisierung starten
        self._start_auto_refresh()
    
    def _create_ui(self) -> None:
        """Erstellt die Benutzeroberfläche."""
        # Hauptlayout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Filter-Bereich
        self._create_filter_section(main_layout)
        
        # Statistiken
        self._create_stats_section(main_layout)
        
        # Gerätetabelle
        self._create_device_table(main_layout)
        
        # Button-Bereich
        self._create_button_section(main_layout)
    
    def _create_filter_section(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt den Filter-Bereich."""
        self.filter_frame = QFrame()
        self.filter_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        filter_layout = QHBoxLayout(self.filter_frame)
        
        # Filter-Label
        filter_label = QLabel("Filter:")
        filter_label.setFont(QFont("", weight=QFont.Weight.Bold))
        filter_layout.addWidget(filter_label)
        
        # Getrennte Geräte anzeigen
        self.show_disconnected_cb = QCheckBox("Getrennte Geräte anzeigen")
        self.show_disconnected_cb.setChecked(self.config.get("show_disconnected_devices", True))
        self.show_disconnected_cb.toggled.connect(self._on_filter_changed)
        filter_layout.addWidget(self.show_disconnected_cb)
        
        # USB-Hubs anzeigen
        self.show_hubs_cb = QCheckBox("USB-Hubs anzeigen")
        self.show_hubs_cb.setChecked(self.config.get("show_usb_hubs", True))
        self.show_hubs_cb.toggled.connect(self._on_filter_changed)
        filter_layout.addWidget(self.show_hubs_cb)
        
        # Suchfeld
        search_label = QLabel("Suche:")
        filter_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Gerätename, Hersteller...")
        self.search_input.textChanged.connect(self._on_search_changed)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addStretch()
        
        parent_layout.addWidget(self.filter_frame)
    
    def _create_stats_section(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt den Statistiken-Bereich."""
        self.stats_frame = QFrame()
        self.stats_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        stats_layout = QHBoxLayout(self.stats_frame)
        
        # USB-Geräte-Statistiken
        self.total_devices_label = QLabel("Gesamt: 0")
        self.connected_devices_label = QLabel("Verbunden: 0")
        self.disconnected_devices_label = QLabel("Getrennt: 0")
        
        stats_layout.addWidget(self.total_devices_label)
        stats_layout.addWidget(self.connected_devices_label)
        stats_layout.addWidget(self.disconnected_devices_label)
        
        stats_layout.addStretch()
        
        # Letzte Aktualisierung
        self.last_refresh_label = QLabel("Letzte Aktualisierung: --")
        stats_layout.addWidget(self.last_refresh_label)
        
        parent_layout.addWidget(self.stats_frame)
    
    def _create_device_table(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt die Gerätetabelle."""
        # Tabellenmodell
        self.table_model = USBDeviceTableModel(self.device_monitor)
        
        # Tabelle
        self.device_table = QTableView()
        self.device_table.setModel(self.table_model)
        self.device_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.device_table.setAlternatingRowColors(True)
        self.device_table.setSortingEnabled(True)
        self.device_table.setWordWrap(False)
        
        # Spaltenbreiten anpassen
        header = self.device_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Hersteller
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Gerätetyp
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # USB-Version
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Seriennummer
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Produkt-ID
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Vendor-ID
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Treiber
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)  # Erstmals gesehen
        
        # Zeilenhöhe
        self.device_table.verticalHeader().setDefaultSectionSize(30)
        
        parent_layout.addWidget(self.device_table)
    
    def _create_button_section(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt den Button-Bereich."""
        button_layout = QHBoxLayout()
        
        # Aktualisieren-Button
        self.refresh_button = QPushButton("Aktualisieren")
        self.refresh_button.clicked.connect(self._refresh_devices)
        button_layout.addWidget(self.refresh_button)
        
        # Export-Button
        self.export_button = QPushButton("Exportieren")
        self.export_button.clicked.connect(self._export_devices)
        button_layout.addWidget(self.export_button)
        
        # Verlauf löschen-Button
        self.clear_history_button = QPushButton("Verlauf löschen")
        self.clear_history_button.clicked.connect(self._clear_history)
        button_layout.addWidget(self.clear_history_button)
        
        button_layout.addStretch()
        
        # Auto-Refresh-Checkbox
        self.auto_refresh_cb = QCheckBox("Automatische Aktualisierung")
        self.auto_refresh_cb.setChecked(self.config.get("auto_refresh", True))
        self.auto_refresh_cb.toggled.connect(self._on_auto_refresh_changed)
        button_layout.addWidget(self.auto_refresh_cb)
        
        # Aktualisierungsintervall
        interval_label = QLabel("Intervall (Sek.):")
        button_layout.addWidget(interval_label)
        
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1", "2", "5", "10", "30", "60"])
        current_interval = str(self.config.get("refresh_interval", 5000) // 1000)
        index = self.interval_combo.findText(current_interval)
        if index >= 0:
            self.interval_combo.setCurrentIndex(index)
        self.interval_combo.currentTextChanged.connect(self._on_interval_changed)
        button_layout.addWidget(self.interval_combo)
        
        parent_layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """Verbindet alle Signale."""
        # Filter-Änderungen
        self.show_disconnected_cb.toggled.connect(self._on_filter_changed)
        self.show_hubs_cb.toggled.connect(self._on_filter_changed)
        
        # Auto-Refresh
        self.auto_refresh_cb.toggled.connect(self._on_auto_refresh_changed)
        self.interval_combo.currentTextChanged.connect(self._on_interval_changed)
    
    def _start_auto_refresh(self) -> None:
        """Startet die automatische Aktualisierung."""
        if self.config.get("auto_refresh", True):
            interval = self.config.get("refresh_interval", 5000)
            self.refresh_timer.start(interval)
    
    def _stop_auto_refresh(self) -> None:
        """Stoppt die automatische Aktualisierung."""
        self.refresh_timer.stop()
    
    def _on_filter_changed(self) -> None:
        """Wird aufgerufen, wenn sich die Filter ändern."""
        if self.table_model:
            self.table_model.set_show_disconnected(self.show_disconnected_cb.isChecked())
            self.table_model.set_show_hubs(self.show_hubs_cb.isChecked())
            
            # Konfiguration speichern
            self.config.set("show_disconnected_devices", self.show_disconnected_cb.isChecked())
            self.config.set("show_usb_hubs", self.show_hubs_cb.isChecked())
    
    def _on_search_changed(self, text: str) -> None:
        """Wird aufgerufen, wenn sich der Suchtext ändert."""
        # TODO: Suchfunktionalität implementieren
        pass
    
    def _on_auto_refresh_changed(self, enabled: bool) -> None:
        """Wird aufgerufen, wenn sich die Auto-Refresh-Einstellung ändert."""
        if enabled:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()
        
        # Konfiguration speichern
        self.config.set("auto_refresh", enabled)
    
    def _on_interval_changed(self, interval_text: str) -> None:
        """Wird aufgerufen, wenn sich das Aktualisierungsintervall ändert."""
        try:
            interval = int(interval_text) * 1000  # In Millisekunden
            self.config.set("refresh_interval", interval)
            
            if self.refresh_timer.isActive():
                self.refresh_timer.start(interval)
                
        except ValueError:
            pass
    
    def _auto_refresh(self) -> None:
        """Führt eine automatische Aktualisierung durch."""
        if self.auto_refresh_cb.isChecked():
            self._refresh_devices()
    
    def _refresh_devices(self) -> None:
        """Aktualisiert die Geräteliste."""
        try:
            # Geräteliste aktualisieren
            self.device_monitor.refresh_devices()
            
            # Tabellenmodell aktualisieren
            if self.table_model:
                self.table_model.refresh()
            
            # Statistiken aktualisieren
            self._update_statistics()
            
            # Zeitstempel aktualisieren
            current_time = datetime.now().strftime("%H:%M:%S")
            self.last_refresh_label.setText(f"Letzte Aktualisierung: {current_time}")
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Aktualisieren der Geräteliste: {e}")
    
    def _update_statistics(self) -> None:
        """Aktualisiert die Statistiken."""
        try:
            stats = self.device_monitor.get_device_statistics()
            
            self.total_devices_label.setText(f"Gesamt: {stats['total_devices']}")
            self.connected_devices_label.setText(f"Verbunden: {stats['connected_devices']}")
            self.disconnected_devices_label.setText(f"Getrennt: {stats['disconnected_devices']}")
            
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Statistiken: {e}")
    
    def _export_devices(self) -> None:
        """Exportiert die USB-Geräteliste."""
        try:
            from PyQt6.QtWidgets import QFileDialog
            from datetime import datetime
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "USB-Geräte exportieren",
                f"usb_devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON-Dateien (*.json);;Alle Dateien (*)"
            )
            
            if filename:
                if self.device_monitor.export_devices(filename):
                    QMessageBox.information(self, "Erfolg", f"USB-Geräte erfolgreich exportiert nach:\n{filename}")
                else:
                    QMessageBox.warning(self, "Fehler", "Fehler beim Exportieren der USB-Geräte")
                    
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Exportieren: {e}")
    
    def _clear_history(self) -> None:
        """Löscht den Geräteverlauf."""
        try:
            reply = QMessageBox.question(
                self,
                "Verlauf löschen",
                "Möchten Sie wirklich den gesamten Geräteverlauf löschen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.device_monitor.clear_history()
                self._refresh_devices()
                QMessageBox.information(self, "Erfolg", "Geräteverlauf erfolgreich gelöscht")
                
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Löschen des Verlaufs: {e}")
    
    def refresh(self) -> None:
        """Öffentliche Methode zum Aktualisieren der Anzeige."""
        self._refresh_devices()
    
    def get_selected_device(self) -> Optional[USBDevice]:
        """Gibt das aktuell ausgewählte USB-Gerät zurück."""
        if not self.device_table or not self.table_model:
            return None
        
        current_index = self.device_table.currentIndex()
        if current_index.isValid():
            row = current_index.row()
            if row < len(self.table_model.filtered_devices):
                return self.table_model.filtered_devices[row]
        
        return None
    
    def show_device_details(self, device: USBDevice) -> None:
        """Zeigt Details zu einem USB-Gerät an."""
        if not device:
            return
        
        details_text = f"""
        <h3>USB-Gerät Details</h3>
        <p><b>Name:</b> {device.name}</p>
        <p><b>Beschreibung:</b> {device.description or 'Keine'}</p>
        <p><b>Hersteller:</b> {device.manufacturer or 'Unbekannt'}</p>
        <p><b>Gerätetyp:</b> {device.device_type or 'USB Device'}</p>
        <p><b>USB-Version:</b> {device.usb_version or 'Unbekannt'}</p>
        <p><b>Seriennummer:</b> {device.serial_number or 'Keine'}</p>
        <p><b>Produkt-ID:</b> {device.product_id or 'Unbekannt'}</p>
        <p><b>Vendor-ID:</b> {device.vendor_id or 'Unbekannt'}</p>
        <p><b>Treiber-Version:</b> {device.driver_version or 'Unbekannt'}</p>
        <p><b>Leistungsaufnahme:</b> {device.power_consumption or 'Unbekannt'}</p>
        <p><b>Status:</b> {device.connection_status}</p>
        <p><b>Erstmals gesehen:</b> {device.first_seen.strftime('%d.%m.%Y %H:%M:%S') if device.first_seen else 'Unbekannt'}</p>
        <p><b>Zuletzt gesehen:</b> {device.last_seen.strftime('%d.%m.%Y %H:%M:%S') if device.last_seen else 'Unbekannt'}</p>
        """
        
        QMessageBox.information(self, "USB-Gerät Details", details_text)
