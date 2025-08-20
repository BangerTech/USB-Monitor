"""
COM-Port-Panel für USB-Monitor.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QLabel, QFrame, QHeaderView, QAbstractItemView, QMessageBox,
    QCheckBox, QComboBox, QLineEdit, QGroupBox, QSplitter,
    QTabWidget, QTextEdit, QProgressBar, QSpinBox, QDialog,
    QDialogButtonBox, QFormLayout, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QFont, QColor, QBrush

from core.port_monitor import PortMonitor, COMPort
from utils.config import Config


class COMPortTableModel(QAbstractTableModel):
    """Tabellenmodell für COM-Ports."""
    
    def __init__(self, port_monitor: PortMonitor):
        """Initialisiert das Tabellenmodell."""
        super().__init__()
        self.port_monitor = port_monitor
        self.ports: List[COMPort] = []
        self.filtered_ports: List[COMPort] = []
        self.show_unavailable = True
        
        # Spalten-Header
        self.headers = [
            "Status", "Port-Name", "Gerätename", "Beschreibung", "Baud-Rate",
            "Datenbits", "Stop-Bits", "Parität", "Hersteller", "Erstellt"
        ]
        
        # Portliste aktualisieren
        self._update_ports()
    
    def _update_ports(self) -> None:
        """Aktualisiert die Portliste."""
        self.ports = self.port_monitor.get_all_ports()
        self._apply_filters()
    
    def _apply_filters(self) -> None:
        """Wendet die aktuellen Filter an."""
        self.filtered_ports = []
        
        for port in self.ports:
            # Filter für nicht verfügbare Ports
            if not self.show_unavailable and not port.is_available:
                continue
            
            self.filtered_ports.append(port)
        
        # Tabelle aktualisieren
        self.layoutChanged.emit()
    
    def set_show_unavailable(self, show: bool) -> None:
        """Setzt den Filter für nicht verfügbare Ports."""
        self.show_unavailable = show
        self._apply_filters()
    
    def refresh(self) -> None:
        """Aktualisiert die Portliste."""
        self._update_ports()
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Gibt die Anzahl der Zeilen zurück."""
        return len(self.filtered_ports)
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Gibt die Anzahl der Spalten zurück."""
        return len(self.headers)
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Gibt die Daten für den angegebenen Index zurück."""
        if not index.isValid():
            return None
        
        if index.row() >= len(self.filtered_ports):
            return None
        
        port = self.filtered_ports[index.row()]
        column = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_data(port, column)
        elif role == Qt.ItemDataRole.BackgroundRole:
            return self._get_background_color(port)
        elif role == Qt.ItemDataRole.FontRole:
            return self._get_font(port)
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Gibt die Header-Daten zurück."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if section < len(self.headers):
                return self.headers[section]
        return None
    
    def _get_display_data(self, port: COMPort, column: int) -> str:
        """Gibt die Anzeigedaten für eine Spalte zurück."""
        if column == 0:  # Status
            if port.is_open:
                return "🔓 Geöffnet"
            elif port.is_available:
                return "🟢 Verfügbar"
            else:
                return "🔴 Nicht verfügbar"
        elif column == 1:  # Port-Name
            return port.port_name
        elif column == 2:  # Gerätename
            return port.device_name or "Unbekannt"
        elif column == 3:  # Beschreibung
            return port.description or "Keine"
        elif column == 4:  # Baud-Rate
            return str(port.baud_rate) if port.baud_rate else "9600"
        elif column == 5:  # Datenbits
            return str(port.data_bits) if port.data_bits else "8"
        elif column == 6:  # Stop-Bits
            return str(port.stop_bits) if port.stop_bits else "1"
        elif column == 7:  # Parität
            return port.parity if port.parity else "N"
        elif column == 8:  # Hersteller
            return port.manufacturer or "Unbekannt"
        elif column == 9:  # Erstellt
            if port.created_at:
                return port.created_at.strftime("%d.%m.%Y %H:%M")
            return "Unbekannt"
        
        return ""
    
    def _get_background_color(self, port: COMPort) -> QBrush:
        """Gibt die Hintergrundfarbe für eine Zeile zurück."""
        if not port.is_available:
            return QBrush(QColor(64, 64, 64))  # Dunkelgrau für nicht verfügbare Ports
        elif port.is_open:
            return QBrush(QColor(0, 100, 0, 50))  # Leicht grün für geöffnete Ports
        return QBrush()
    
    def _get_font(self, port: COMPort) -> QFont:
        """Gibt die Schriftart für eine Zeile zurück."""
        font = QFont()
        if not port.is_available:
            font.setItalic(True)
        elif port.is_open:
            font.setBold(True)
        return font


class PortSettingsDialog(QDialog):
    """Dialog für COM-Port-Einstellungen."""
    
    def __init__(self, parent=None, port: COMPort = None):
        """Initialisiert den Dialog."""
        super().__init__(parent)
        
        self.port = port
        self.settings = {}
        
        self.setWindowTitle("COM-Port-Einstellungen")
        self.setModal(True)
        self.resize(400, 300)
        
        self._create_ui()
        self._load_port_settings()
    
    def _create_ui(self) -> None:
        """Erstellt die Benutzeroberfläche."""
        layout = QVBoxLayout(self)
        
        # Formular
        form_layout = QFormLayout()
        
        # Baud-Rate
        self.baud_rate_combo = QComboBox()
        self.baud_rate_combo.addItems(["110", "300", "600", "1200", "2400", "4800", "9600", "14400", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        form_layout.addRow("Baud-Rate:", self.baud_rate_combo)
        
        # Datenbits
        self.data_bits_combo = QComboBox()
        self.data_bits_combo.addItems(["5", "6", "7", "8"])
        form_layout.addRow("Datenbits:", self.data_bits_combo)
        
        # Stop-Bits
        self.stop_bits_combo = QComboBox()
        self.stop_bits_combo.addItems(["1", "1.5", "2"])
        form_layout.addRow("Stop-Bits:", self.stop_bits_combo)
        
        # Parität
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["N", "E", "O"])
        form_layout.addRow("Parität:", self.parity_combo)
        
        # Flow-Control
        self.flow_control_combo = QComboBox()
        self.flow_control_combo.addItems(["None", "XON/XOFF", "RTS/CTS"])
        form_layout.addRow("Flow-Control:", self.flow_control_combo)
        
        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(1)
        self.timeout_spin.setSuffix(" Sekunden")
        form_layout.addRow("Timeout:", self.timeout_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _load_port_settings(self) -> None:
        """Lädt die aktuellen Port-Einstellungen."""
        if self.port:
            # Baud-Rate
            baud_rate = str(self.port.baud_rate) if self.port.baud_rate else "9600"
            index = self.baud_rate_combo.findText(baud_rate)
            if index >= 0:
                self.baud_rate_combo.setCurrentIndex(index)
            
            # Datenbits
            data_bits = str(self.port.data_bits) if self.port.data_bits else "8"
            index = self.data_bits_combo.findText(data_bits)
            if index >= 0:
                self.data_bits_combo.setCurrentIndex(index)
            
            # Stop-Bits
            stop_bits = str(self.port.stop_bits) if self.port.stop_bits else "1"
            index = self.stop_bits_combo.findText(stop_bits)
            if index >= 0:
                self.data_bits_combo.setCurrentIndex(index)
            
            # Parität
            parity = self.port.parity if self.port.parity else "N"
            index = self.parity_combo.findText(parity)
            if index >= 0:
                self.parity_combo.setCurrentIndex(index)
            
            # Flow-Control
            flow_control = self.port.flow_control if self.port.flow_control else "None"
            index = self.flow_control_combo.findText(flow_control)
            if index >= 0:
                self.flow_control_combo.setCurrentIndex(index)
    
    def get_settings(self) -> Dict[str, Any]:
        """Gibt die aktuellen Einstellungen zurück."""
        return {
            "baud_rate": int(self.baud_rate_combo.currentText()),
            "data_bits": int(self.data_bits_combo.currentText()),
            "stop_bits": float(self.stop_bits_combo.currentText()),
            "parity": self.parity_combo.currentText(),
            "flow_control": self.flow_control_combo.currentText(),
            "timeout": self.timeout_spin.value()
        }


class PortPanel(QWidget):
    """Panel für die Anzeige und Verwaltung von COM-Ports."""
    
    def __init__(self, port_monitor: PortMonitor, config: Config):
        """Initialisiert das Port Panel."""
        super().__init__()
        
        self.port_monitor = port_monitor
        self.config = config
        
        # UI-Komponenten
        self.table_model: Optional[COMPortTableModel] = None
        self.port_table: Optional[QTableView] = None
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
        
        # Porttabelle
        self._create_port_table(main_layout)
        
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
        
        # Nicht verfügbare Ports anzeigen
        self.show_unavailable_cb = QCheckBox("Nicht verfügbare Ports anzeigen")
        self.show_unavailable_cb.setChecked(True)
        self.show_unavailable_cb.toggled.connect(self._on_filter_changed)
        filter_layout.addWidget(self.show_unavailable_cb)
        
        # Suchfeld
        search_label = QLabel("Suche:")
        filter_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Port-Name, Gerätename...")
        self.search_input.textChanged.connect(self._on_search_changed)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addStretch()
        
        parent_layout.addWidget(self.filter_frame)
    
    def _create_stats_section(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt den Statistiken-Bereich."""
        self.stats_frame = QFrame()
        self.stats_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        stats_layout = QHBoxLayout(self.stats_frame)
        
        # COM-Port-Statistiken
        self.total_ports_label = QLabel("Gesamt: 0")
        self.available_ports_label = QLabel("Verfügbar: 0")
        self.unavailable_ports_label = QLabel("Nicht verfügbar: 0")
        self.open_ports_label = QLabel("Geöffnet: 0")
        
        stats_layout.addWidget(self.total_ports_label)
        stats_layout.addWidget(self.available_ports_label)
        stats_layout.addWidget(self.unavailable_ports_label)
        stats_layout.addWidget(self.open_ports_label)
        
        stats_layout.addStretch()
        
        # Letzte Aktualisierung
        self.last_refresh_label = QLabel("Letzte Aktualisierung: --")
        stats_layout.addWidget(self.last_refresh_label)
        
        parent_layout.addWidget(self.stats_frame)
    
    def _create_port_table(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt die Porttabelle."""
        # Tabellenmodell
        self.table_model = COMPortTableModel(self.port_monitor)
        
        # Tabelle
        self.port_table = QTableView()
        self.port_table.setModel(self.table_model)
        self.port_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.port_table.setAlternatingRowColors(True)
        self.port_table.setSortingEnabled(True)
        self.port_table.setWordWrap(False)
        
        # Spaltenbreiten anpassbar machen
        header = self.port_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionsMovable(True)  # Spalten verschiebbar
        
        # Standardbreiten setzen, aber anpassbar lassen
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Status
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # Port-Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)      # Gerätename (dehnt sich aus)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # Beschreibung
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)  # Baud-Rate
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)  # Datenbits
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)  # Stop-Bits
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Interactive)  # Parität
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Interactive)  # Hersteller
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.Interactive)  # Erstellt
        
        # Standardbreiten setzen
        header.resizeSection(0, 80)   # Status
        header.resizeSection(1, 100)  # Port-Name
        header.resizeSection(3, 150)  # Beschreibung
        header.resizeSection(4, 80)   # Baud-Rate
        header.resizeSection(5, 70)   # Datenbits
        header.resizeSection(6, 70)   # Stop-Bits
        header.resizeSection(7, 60)   # Parität
        header.resizeSection(8, 120)  # Hersteller
        header.resizeSection(9, 120)  # Erstellt
        
        # Zeilenhöhe
        self.port_table.verticalHeader().setDefaultSectionSize(30)
        
        # Doppelklick für Details
        self.port_table.doubleClicked.connect(self._on_port_double_clicked)
        
        parent_layout.addWidget(self.port_table)
    
    def _create_button_section(self, parent_layout: QVBoxLayout) -> None:
        """Erstellt den Button-Bereich."""
        button_layout = QHBoxLayout()
        
        # Aktualisieren-Button
        self.refresh_button = QPushButton("Aktualisieren")
        self.refresh_button.clicked.connect(self._refresh_ports)
        button_layout.addWidget(self.refresh_button)
        
        # Port öffnen-Button
        self.open_port_button = QPushButton("Port öffnen")
        self.open_port_button.clicked.connect(self._open_port)
        button_layout.addWidget(self.open_port_button)
        
        # Port schließen-Button
        self.close_port_button = QPushButton("Port schließen")
        self.close_port_button.clicked.connect(self._close_port)
        button_layout.addWidget(self.close_port_button)
        
        # Port testen-Button
        self.test_port_button = QPushButton("Port testen")
        self.test_port_button.clicked.connect(self._test_port)
        button_layout.addWidget(self.test_port_button)
        
        # Export-Button
        self.export_button = QPushButton("Exportieren")
        self.export_button.clicked.connect(self._export_ports)
        button_layout.addWidget(self.export_button)
        
        button_layout.addStretch()
        
        # Automatische Aktualisierung wird vom Hauptfenster gesteuert
        pass
        
        parent_layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """Verbindet alle Signale."""
        # Filter-Änderungen
        self.show_unavailable_cb.toggled.connect(self._on_filter_changed)
        
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
            self.table_model.set_show_unavailable(self.show_unavailable_cb.isChecked())
    
    def _on_search_changed(self, text: str) -> None:
        """Wird aufgerufen, wenn sich der Suchtext ändert."""
        # TODO: Suchfunktionalität implementieren
        pass
    
    # Auto-Refresh wird vom Hauptfenster gesteuert
    pass
    
    def _auto_refresh(self) -> None:
        """Führt eine automatische Aktualisierung durch."""
        if self.auto_refresh_cb.isChecked():
            self._refresh_ports()
    
    def _refresh_ports(self) -> None:
        """Aktualisiert die Portliste."""
        try:
            # Portliste aktualisieren
            self.port_monitor.refresh_ports()
            
            # Tabellenmodell aktualisieren
            if self.table_model:
                self.table_model.refresh()
            
            # Statistiken aktualisieren
            self._update_statistics()
            
            # Zeitstempel aktualisieren
            current_time = datetime.now().strftime("%H:%M:%S")
            self.last_refresh_label.setText(f"Letzte Aktualisierung: {current_time}")
            
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Aktualisieren der Portliste: {e}")
    
    def _update_statistics(self) -> None:
        """Aktualisiert die Statistiken."""
        try:
            stats = self.port_monitor.get_port_statistics()
            
            self.total_ports_label.setText(f"Gesamt: {stats['total_ports']}")
            self.available_ports_label.setText(f"Verfügbar: {stats['available_ports']}")
            self.unavailable_ports_label.setText(f"Nicht verfügbar: {stats['unavailable_ports']}")
            self.open_ports_label.setText(f"Geöffnet: {stats['open_ports']}")
            
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Statistiken: {e}")
    
    def _on_port_double_clicked(self, index: QModelIndex) -> None:
        """Wird aufgerufen, wenn auf einen Port doppelgeklickt wird."""
        if not index.isValid():
            return
        
        row = index.row()
        if row < len(self.table_model.filtered_ports):
            port = self.table_model.filtered_ports[row]
            self._show_port_details(port)
    
    def _show_port_details(self, port: COMPort) -> None:
        """Zeigt Details zu einem COM-Port an."""
        if not port:
            return
        
        details_text = f"""
        <h3>COM-Port Details</h3>
        <p><b>Port-Name:</b> {port.port_name}</p>
        <p><b>Gerätename:</b> {port.device_name or 'Unbekannt'}</p>
        <p><b>Beschreibung:</b> {port.description or 'Keine'}</p>
        <p><b>Baud-Rate:</b> {port.baud_rate}</p>
        <p><b>Datenbits:</b> {port.data_bits}</p>
        <p><b>Stop-Bits:</b> {port.stop_bits}</p>
        <p><b>Parität:</b> {port.parity}</p>
        <p><b>Flow-Control:</b> {port.flow_control}</p>
        <p><b>Hersteller:</b> {port.manufacturer or 'Unbekannt'}</p>
        <p><b>Produkt-ID:</b> {port.product_id or 'Unbekannt'}</p>
        <p><b>Vendor-ID:</b> {port.vendor_id or 'Unbekannt'}</p>
        <p><b>Seriennummer:</b> {port.serial_number or 'Keine'}</p>
        <p><b>Verfügbar:</b> {'Ja' if port.is_available else 'Nein'}</p>
        <p><b>Geöffnet:</b> {'Ja' if port.is_open else 'Nein'}</p>
        <p><b>Erstellt:</b> {port.created_at.strftime('%d.%m.%Y %H:%M:%S') if port.created_at else 'Unbekannt'}</p>
        <p><b>Zuletzt verwendet:</b> {port.last_used.strftime('%d.%m.%Y %H:%M:%S') if port.last_used else 'Nie'}</p>
        """
        
        QMessageBox.information(self, "COM-Port Details", details_text)
    
    def _open_port(self) -> None:
        """Öffnet den ausgewählten COM-Port."""
        port = self._get_selected_port()
        if not port:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie einen Port aus.")
            return
        
        if not port.is_available:
            QMessageBox.warning(self, "Warnung", "Der ausgewählte Port ist nicht verfügbar.")
            return
        
        if port.is_open:
            QMessageBox.information(self, "Information", "Der Port ist bereits geöffnet.")
            return
        
        try:
            # Einstellungsdialog anzeigen
            dialog = PortSettingsDialog(self, port)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                settings = dialog.get_settings()
                
                # Port öffnen
                serial_connection = self.port_monitor.open_port(port.port_name, **settings)
                
                if serial_connection:
                    QMessageBox.information(self, "Erfolg", f"Port {port.port_name} erfolgreich geöffnet.")
                    self._refresh_ports()
                else:
                    QMessageBox.warning(self, "Fehler", f"Fehler beim Öffnen des Ports {port.port_name}.")
                    
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Öffnen des Ports: {e}")
    
    def _close_port(self) -> None:
        """Schließt den ausgewählten COM-Port."""
        port = self._get_selected_port()
        if not port:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie einen Port aus.")
            return
        
        if not port.is_open:
            QMessageBox.information(self, "Information", "Der ausgewählte Port ist nicht geöffnet.")
            return
        
        try:
            if self.port_monitor.close_port(port.port_name):
                QMessageBox.information(self, "Erfolg", f"Port {port.port_name} erfolgreich geschlossen.")
                self._refresh_ports()
            else:
                QMessageBox.warning(self, "Fehler", f"Fehler beim Schließen des Ports {port.port_name}.")
                
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Schließen des Ports: {e}")
    
    def _test_port(self) -> None:
        """Testet den ausgewählten COM-Port."""
        port = self._get_selected_port()
        if not port:
            QMessageBox.warning(self, "Warnung", "Bitte wählen Sie einen Port aus.")
            return
        
        if not port.is_available:
            QMessageBox.warning(self, "Warnung", "Der ausgewählte Port ist nicht verfügbar.")
            return
        
        try:
            # Port testen
            if self.port_monitor.test_port(port.port_name):
                QMessageBox.information(self, "Erfolg", f"Port {port.port_name} erfolgreich getestet.")
            else:
                QMessageBox.warning(self, "Fehler", f"Port {port.port_name} konnte nicht geöffnet werden.")
                
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Testen des Ports: {e}")
    
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
                    QMessageBox.information(self, "Erfolg", f"COM-Ports erfolgreich exportiert nach:\n{filename}")
                else:
                    QMessageBox.warning(self, "Fehler", "Fehler beim Exportieren der COM-Ports")
                    
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Exportieren: {e}")
    
    def _get_selected_port(self) -> Optional[COMPort]:
        """Gibt den aktuell ausgewählten COM-Port zurück."""
        if not self.port_table or not self.table_model:
            return None
        
        current_index = self.port_table.currentIndex()
        if current_index.isValid():
            row = current_index.row()
            if row < len(self.table_model.filtered_ports):
                return self.table_model.filtered_ports[row]
        
        return None
    
    def refresh(self) -> None:
        """Öffentliche Methode zum Aktualisieren der Anzeige."""
        self._refresh_ports()
