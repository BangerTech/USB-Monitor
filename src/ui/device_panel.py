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
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PyQt6.QtGui import QFont, QColor, QBrush

from core.device_monitor import DeviceMonitor, USBDevice
from core.speed_test import USBSpeedTester, SpeedTestResult
from utils.config import Config
from ui.icons import get_device_icon, get_status_icon


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
        self.search_text = ""
        self.group_by = "Keine"
        
        # Spalten-Header
        self.headers = [
            "Status", "Name", "Hersteller", "Gerätetyp", "USB-Version",
            "Stromverbrauch", "Max. Leistung", "Übertragungsgeschw.", 
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
            
            # Suchfilter
            if self.search_text and not self._device_matches_search(device, self.search_text):
                continue
            
            self.filtered_devices.append(device)
        
        # Gruppierung anwenden
        self._apply_grouping()
        
        # Tabelle aktualisieren
        self.layoutChanged.emit()
    
    def _apply_grouping(self) -> None:
        """Wendet die Gruppierung an."""
        if self.group_by == "Keine":
            return
        
        # Geräte nach Gruppierungskriterium sortieren
        if self.group_by == "Status":
            self.filtered_devices.sort(key=lambda d: (not d.is_connected, d.name.lower()))
        elif self.group_by == "Hersteller":
            self.filtered_devices.sort(key=lambda d: ((d.manufacturer or "Unbekannt").lower(), d.name.lower()))
        elif self.group_by == "Gerätetyp":
            self.filtered_devices.sort(key=lambda d: ((d.device_type or "USB Device").lower(), d.name.lower()))
        elif self.group_by == "USB-Version":
            self.filtered_devices.sort(key=lambda d: ((d.usb_version or "Unbekannt").lower(), d.name.lower()))
    
    def _device_matches_search(self, device: USBDevice, search_text: str) -> bool:
        """Prüft, ob ein Gerät dem Suchtext entspricht."""
        search_lower = search_text.lower()
        
        # In verschiedenen Feldern suchen
        fields_to_search = [
            device.name or "",
            device.manufacturer or "",
            device.device_type or "",
            device.usb_version or "",
            device.power_consumption or "",
            device.max_power or "",
            device.transfer_speed or "",
            device.serial_number or "",
            device.product_id or "",
            device.vendor_id or "",
            device.driver_version or "",
            device.device_class or ""
        ]
        
        return any(search_lower in field.lower() for field in fields_to_search)
    
    def set_show_disconnected(self, show: bool) -> None:
        """Setzt den Filter für getrennte Geräte."""
        self.show_disconnected = show
        self._apply_filters()
    
    def set_show_hubs(self, show: bool) -> None:
        """Setzt den Filter für USB-Hubs."""
        self.show_hubs = show
        self._apply_filters()
    
    def set_search_text(self, text: str) -> None:
        """Setzt den Suchtext."""
        self.search_text = text
        self._apply_filters()
    
    def set_grouping(self, group_by: str) -> None:
        """Setzt die Gruppierung."""
        self.group_by = group_by
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
        elif role == Qt.ItemDataRole.DecorationRole:
            return self._get_icon(device, column)
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
            return "Verbunden" if device.is_connected else "Getrennt"
        elif column == 1:  # Name
            return device.name or "Unbekannt"
        elif column == 2:  # Hersteller
            return device.manufacturer or "Unbekannt"
        elif column == 3:  # Gerätetyp
            return device.device_type or "USB Device"
        elif column == 4:  # USB-Version
            return device.usb_version or "Unbekannt"
        elif column == 5:  # Stromverbrauch
            return device.power_consumption or "Unbekannt"
        elif column == 6:  # Max. Leistung
            power_info = []
            if device.max_power:
                power_info.append(f"Max: {device.max_power}")
            if device.current_available:
                power_info.append(f"Verfügbar: {device.current_available}")
            return " | ".join(power_info) if power_info else "Unbekannt"
        elif column == 7:  # Übertragungsgeschwindigkeit
            speed_info = []
            if device.transfer_speed:
                speed_info.append(f"Aktuell: {device.transfer_speed}")
            if device.max_transfer_speed and device.max_transfer_speed != device.transfer_speed:
                speed_info.append(f"Max: {device.max_transfer_speed}")
            return " | ".join(speed_info) if speed_info else "Unbekannt"
        elif column == 8:  # Seriennummer
            return device.serial_number or "Keine"
        elif column == 9:  # Produkt-ID
            return device.product_id or "Unbekannt"
        elif column == 10:  # Vendor-ID
            return device.vendor_id or "Unbekannt"
        elif column == 11:  # Treiber
            return device.driver_version or "Unbekannt"
        elif column == 12:  # Erstmals gesehen
            if device.first_seen:
                return device.first_seen.strftime("%d.%m.%Y %H:%M")
            return "Unbekannt"
        
        return ""
    
    def _get_icon(self, device: USBDevice, column: int):
        """Gibt das Icon für eine Spalte zurück."""
        if column == 0:  # Status
            return get_status_icon(device.is_connected)
        elif column == 1:  # Name - Gerätetyp-Icon
            return get_device_icon(device.name, device.device_type)
        
        return None
    
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
    
    def sort(self, column: int, order: Qt.SortOrder) -> None:
        """Sortiert die Tabelle nach der angegebenen Spalte."""
        self.layoutAboutToBeChanged.emit()
        
        reverse = order == Qt.SortOrder.DescendingOrder
        
        if column == 0:  # Status
            self.filtered_devices.sort(key=lambda d: d.is_connected, reverse=reverse)
        elif column == 1:  # Name
            self.filtered_devices.sort(key=lambda d: d.name.lower(), reverse=reverse)
        elif column == 2:  # Hersteller
            self.filtered_devices.sort(key=lambda d: (d.manufacturer or "").lower(), reverse=reverse)
        elif column == 3:  # Gerätetyp
            self.filtered_devices.sort(key=lambda d: (d.device_type or "").lower(), reverse=reverse)
        elif column == 4:  # USB-Version
            self.filtered_devices.sort(key=lambda d: (d.usb_version or "").lower(), reverse=reverse)
        elif column == 5:  # Stromverbrauch
            self.filtered_devices.sort(key=lambda d: (d.power_consumption or "").lower(), reverse=reverse)
        elif column == 6:  # Max. Leistung
            self.filtered_devices.sort(key=lambda d: (d.max_power or "").lower(), reverse=reverse)
        elif column == 7:  # Übertragungsgeschwindigkeit
            self.filtered_devices.sort(key=lambda d: (d.transfer_speed or "").lower(), reverse=reverse)
        elif column == 8:  # Seriennummer
            self.filtered_devices.sort(key=lambda d: (d.serial_number or "").lower(), reverse=reverse)
        elif column == 9:  # Produkt-ID
            self.filtered_devices.sort(key=lambda d: (d.product_id or "").lower(), reverse=reverse)
        elif column == 10:  # Vendor-ID
            self.filtered_devices.sort(key=lambda d: (d.vendor_id or "").lower(), reverse=reverse)
        elif column == 11:  # Treiber
            self.filtered_devices.sort(key=lambda d: (d.driver_version or "").lower(), reverse=reverse)
        elif column == 12:  # Erstmals gesehen
            self.filtered_devices.sort(key=lambda d: d.first_seen or datetime.min, reverse=reverse)
        
        self.layoutChanged.emit()


class DevicePanel(QWidget):
    """Panel für die Anzeige und Verwaltung von USB-Geräten."""
    
    def __init__(self, device_monitor: DeviceMonitor, config: Config):
        """Initialisiert das Device Panel."""
        super().__init__()
        
        self.device_monitor = device_monitor
        self.config = config
        
        # Speed-Tester
        self.speed_tester = USBSpeedTester()
        self.speed_tester.on_test_started = self._on_speed_test_started
        self.speed_tester.on_test_progress = self._on_speed_test_progress
        self.speed_tester.on_test_completed = self._on_speed_test_completed
        
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
        
        # Gruppierung
        group_label = QLabel("Gruppieren nach:")
        filter_layout.addWidget(group_label)
        
        self.group_combo = QComboBox()
        self.group_combo.addItems(["Keine", "Status", "Hersteller", "Gerätetyp", "USB-Version"])
        self.group_combo.currentTextChanged.connect(self._on_grouping_changed)
        filter_layout.addWidget(self.group_combo)
        
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
        
        # Spaltenbreiten anpassbar machen
        header = self.device_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionsMovable(True)  # Spalten verschiebbar
        
        # Standardbreiten setzen, aber anpassbar lassen
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)   # Status
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)       # Name (dehnt sich aus)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)   # Hersteller
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)   # Gerätetyp
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)   # USB-Version
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)   # Stromverbrauch
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)   # Max. Leistung
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Interactive)   # Übertragungsgeschw.
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Interactive)   # Seriennummer
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Interactive)   # Produkt-ID
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.Interactive)  # Vendor-ID
        header.setSectionResizeMode(11, QHeaderView.ResizeMode.Interactive)  # Treiber
        header.setSectionResizeMode(12, QHeaderView.ResizeMode.Interactive)  # Erstmals gesehen
        
        # Standardbreiten setzen
        header.resizeSection(0, 80)    # Status
        header.resizeSection(2, 120)   # Hersteller
        header.resizeSection(3, 100)   # Gerätetyp
        header.resizeSection(4, 100)   # USB-Version
        header.resizeSection(5, 110)   # Stromverbrauch
        header.resizeSection(6, 120)   # Max. Leistung
        header.resizeSection(7, 140)   # Übertragungsgeschw.
        header.resizeSection(8, 120)   # Seriennummer
        header.resizeSection(9, 80)    # Produkt-ID
        header.resizeSection(10, 80)   # Vendor-ID
        header.resizeSection(11, 100)  # Treiber
        header.resizeSection(12, 120)  # Erstmals gesehen
        
        # Zeilenhöhe
        self.device_table.verticalHeader().setDefaultSectionSize(30)
        
        parent_layout.addWidget(self.device_table)
    
    def _create_button_section(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt den Button-Bereich."""
        button_layout = QHBoxLayout()
        
        # Aktualisieren-Button
        from ui.icons import get_icon
        self.refresh_button = QPushButton("Aktualisieren")
        self.refresh_button.setIcon(get_icon("refresh"))
        self.refresh_button.clicked.connect(self._refresh_devices)
        button_layout.addWidget(self.refresh_button)
        
        # Export-Button
        self.export_button = QPushButton("Exportieren")
        self.export_button.setIcon(get_icon("export"))
        self.export_button.clicked.connect(self._export_devices)
        button_layout.addWidget(self.export_button)
        
        # Verlauf löschen-Button
        self.clear_history_button = QPushButton("Verlauf löschen")
        self.clear_history_button.setIcon(get_icon("close"))
        self.clear_history_button.clicked.connect(self._clear_history)
        button_layout.addWidget(self.clear_history_button)
        
        # Speed-Test-Button
        self.speed_test_button = QPushButton("🚀 Speed-Test")
        self.speed_test_button.setIcon(get_icon("play"))
        self.speed_test_button.clicked.connect(self._start_speed_test)
        button_layout.addWidget(self.speed_test_button)
        
        button_layout.addStretch()
        
        # Automatische Aktualisierung wird vom Hauptfenster gesteuert
        pass
        
        parent_layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """Verbindet alle Signale."""
        # Filter-Änderungen
        self.show_disconnected_cb.toggled.connect(self._on_filter_changed)
        self.show_hubs_cb.toggled.connect(self._on_filter_changed)
        
        # Auto-Refresh wird vom Hauptfenster gesteuert
        pass
    
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
        if self.table_model:
            self.table_model.set_search_text(text)
    
    def _on_grouping_changed(self, group_by: str) -> None:
        """Wird aufgerufen, wenn sich die Gruppierung ändert."""
        if self.table_model:
            self.table_model.set_grouping(group_by)
    
    # Auto-Refresh wird vom Hauptfenster gesteuert
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
        <h4>📋 Grundinformationen</h4>
        <p><b>Name:</b> {device.name}</p>
        <p><b>Beschreibung:</b> {device.description or 'Keine'}</p>
        <p><b>Hersteller:</b> {device.manufacturer or 'Unbekannt'}</p>
        <p><b>Gerätetyp:</b> {device.device_type or 'USB Device'}</p>
        <p><b>USB-Version:</b> {device.usb_version or 'Unbekannt'}</p>
        
        <h4>⚡ Stromverbrauch & Leistung</h4>
        <p><b>Stromverbrauch:</b> {device.power_consumption or 'Unbekannt'}</p>
        <p><b>Max. Leistung:</b> {device.max_power or 'Unbekannt'}</p>
        <p><b>Strom benötigt:</b> {device.current_required or 'Unbekannt'}</p>
        <p><b>Strom verfügbar:</b> {device.current_available or 'Unbekannt'}</p>
        
        <h4>🚀 Übertragungsgeschwindigkeit</h4>
        <p><b>Aktuelle Geschwindigkeit:</b> {device.transfer_speed or 'Unbekannt'}</p>
        <p><b>Max. Geschwindigkeit:</b> {device.max_transfer_speed or 'Unbekannt'}</p>
        
        <h4>🔧 Technische Details</h4>
        <p><b>Seriennummer:</b> {device.serial_number or 'Keine'}</p>
        <p><b>Produkt-ID:</b> {device.product_id or 'Unbekannt'}</p>
        <p><b>Vendor-ID:</b> {device.vendor_id or 'Unbekannt'}</p>
        <p><b>Device Class:</b> {device.device_class or 'Unbekannt'}</p>
        <p><b>Treiber-Version:</b> {device.driver_version or 'Unbekannt'}</p>
        
        <h4>📊 Status & Verlauf</h4>
        <p><b>Status:</b> {device.connection_status}</p>
        <p><b>Erstmals gesehen:</b> {device.first_seen.strftime('%d.%m.%Y %H:%M:%S') if device.first_seen else 'Unbekannt'}</p>
        <p><b>Zuletzt gesehen:</b> {device.last_seen.strftime('%d.%m.%Y %H:%M:%S') if device.last_seen else 'Unbekannt'}</p>
        """
        
        QMessageBox.information(self, "USB-Gerät Details", details_text)
    
    def _start_speed_test(self) -> None:
        """Startet einen USB-Geschwindigkeitstest für das ausgewählte Gerät."""
        selected_device = self.get_selected_device()
        if not selected_device:
            QMessageBox.warning(self, "Kein Gerät ausgewählt", 
                              "Bitte wählen Sie ein USB-Gerät aus der Tabelle aus.")
            return
        
        # Prüfen ob es ein Storage-Gerät ist
        if "storage" not in selected_device.device_type.lower() and \
           "card reader" not in selected_device.name.lower():
            reply = QMessageBox.question(
                self, "Kein Storage-Gerät", 
                f"'{selected_device.name}' scheint kein Storage-Gerät zu sein.\n\n"
                "Speed-Tests funktionieren nur mit USB-Festplatten, USB-Sticks oder Kartenlesern.\n\n"
                "Trotzdem fortfahren?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Verfügbare testbare Geräte abrufen
        testable_devices = self.speed_tester.get_testable_devices()
        
        if not testable_devices:
            QMessageBox.warning(self, "Keine testbaren Geräte", 
                              "Es wurden keine testbaren USB-Storage-Geräte gefunden.\n\n"
                              "Stellen Sie sicher, dass:\n"
                              "• Ein USB-Stick oder eine USB-Festplatte angeschlossen ist\n"
                              "• Das Gerät gemountet und zugänglich ist\n"
                              "• Sie Schreibrechte auf dem Gerät haben")
            return
        
        # Gerät auswählen Dialog
        from PyQt6.QtWidgets import QInputDialog
        device_names = list(testable_devices.values())
        device_paths = list(testable_devices.keys())
        
        device_name, ok = QInputDialog.getItem(
            self, "USB-Gerät auswählen", 
            "Wählen Sie das zu testende USB-Gerät:",
            device_names, 0, False
        )
        
        if ok and device_name:
            device_path = device_paths[device_names.index(device_name)]
            
            # Test-Größe Dialog
            test_size, ok = QInputDialog.getDouble(
                self, "Test-Größe", 
                "Test-Datei-Größe (MB):",
                100.0, 1.0, 1000.0, 1
            )
            
            if ok:
                # Speed-Test starten
                self.speed_test_button.setEnabled(False)
                self.speed_test_button.setText("⏳ Teste...")
                self.speed_tester.start_speed_test(device_path, device_name, test_size)
    
    def _on_speed_test_started(self, device_name: str) -> None:
        """Wird aufgerufen, wenn ein Speed-Test startet."""
        QTimer.singleShot(0, lambda: self._update_speed_test_ui(f"🚀 Teste {device_name}..."))
    
    def _on_speed_test_progress(self, device_name: str, progress: float) -> None:
        """Wird aufgerufen, wenn sich der Test-Fortschritt ändert."""
        QTimer.singleShot(0, lambda: self._update_speed_test_ui(f"⏳ {device_name}: {progress:.0f}%"))
    
    def _on_speed_test_completed(self, result: SpeedTestResult) -> None:
        """Wird aufgerufen, wenn ein Speed-Test abgeschlossen ist."""
        QTimer.singleShot(0, lambda: self._show_speed_test_results(result))
    
    def _update_speed_test_ui(self, text: str) -> None:
        """Aktualisiert die Speed-Test-UI."""
        self.speed_test_button.setText(text)
    
    def _show_speed_test_results(self, result: SpeedTestResult) -> None:
        """Zeigt die Speed-Test-Ergebnisse an."""
        self.speed_test_button.setEnabled(True)
        self.speed_test_button.setText("🚀 Speed-Test")
        
        if result.success:
            # Kabel-Qualität bewerten (falls USB-Version verfügbar)
            selected_device = self.get_selected_device()
            cable_quality = "❓ Unbekannt"
            if selected_device and selected_device.usb_version:
                cable_quality = self.speed_tester.detect_cable_quality(
                    selected_device.usb_version, result.average_speed_mbps
                )
            
            speed_rating = self.speed_tester.get_usb_speed_rating(result.average_speed_mbps)
            
            results_text = f"""
            <h3>🚀 USB-Geschwindigkeitstest Ergebnisse</h3>
            
            <h4>📊 Geräteinformationen</h4>
            <p><b>Gerät:</b> {result.device_name}</p>
            <p><b>Pfad:</b> {result.device_path}</p>
            <p><b>Test-Größe:</b> {result.test_file_size_mb:.1f} MB</p>
            <p><b>Test-Dauer:</b> {result.test_duration_seconds:.1f} Sekunden</p>
            
            <h4>⚡ Geschwindigkeitsergebnisse</h4>
            <p><b>Schreibgeschwindigkeit:</b> {result.write_speed_mbps:.1f} MB/s</p>
            <p><b>Lesegeschwindigkeit:</b> {result.read_speed_mbps:.1f} MB/s</p>
            <p><b>Durchschnitt:</b> {result.average_speed_mbps:.1f} MB/s</p>
            
            <h4>📈 Bewertung</h4>
            <p><b>Geschwindigkeits-Rating:</b> {speed_rating}</p>
            <p><b>Kabel-Qualität:</b> {cable_quality}</p>
            
            <h4>💡 Tipps</h4>
            <p>• USB 2.0 theoretisch: ~60 MB/s</p>
            <p>• USB 3.0 theoretisch: ~625 MB/s</p>
            <p>• Bei schlechten Werten: Kabel oder Port wechseln</p>
            """
            
            QMessageBox.information(self, "Speed-Test Ergebnisse", results_text)
        else:
            QMessageBox.warning(self, "Speed-Test Fehler", 
                              f"Der Speed-Test ist fehlgeschlagen:\n\n{result.error_message}")
    
    def closeEvent(self, event) -> None:
        """Wird aufgerufen, wenn das Panel geschlossen wird."""
        # Speed-Test stoppen falls aktiv
        if hasattr(self, 'speed_tester'):
            self.speed_tester.stop_speed_test()
        event.accept()
