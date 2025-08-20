"""
Debug-Panel für USB-Monitor.
"""

import sys
from typing import Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QCheckBox, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

from utils.config import Config
from ui.styles import Styles
from ui.icons import get_icon


class DebugConsole:
    """Singleton Debug-Konsole für die Anwendung."""
    
    _instance: Optional['DebugConsole'] = None
    _messages = []
    _panels = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def add_message(self, message: str, level: str = "INFO"):
        """Fügt eine Debug-Nachricht hinzu."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        formatted_message = f"[{timestamp}] {level}: {message}"
        
        self._messages.append(formatted_message)
        
        # Benachrichtige alle registrierten Panels
        for panel in self._panels:
            panel.add_message(formatted_message)
    
    def register_panel(self, panel):
        """Registriert ein Debug-Panel."""
        if panel not in self._panels:
            self._panels.append(panel)
            # Sende alle bisherigen Nachrichten an das neue Panel
            for message in self._messages:
                panel.add_message(message)
    
    def unregister_panel(self, panel):
        """Entfernt ein Debug-Panel."""
        if panel in self._panels:
            self._panels.remove(panel)
    
    def clear(self):
        """Löscht alle Debug-Nachrichten."""
        self._messages.clear()
        for panel in self._panels:
            panel.clear_messages()


class DebugPanel(QWidget):
    """Debug-Panel für die Anzeige von Debug-Informationen."""
    
    def __init__(self, config: Config, parent=None):
        """Initialisiert das Debug-Panel."""
        super().__init__(parent)
        self.config = config
        self.debug_console = DebugConsole()
        self.auto_scroll = True
        
        self._setup_ui()
        self._connect_signals()
        
        # Bei Debug-Konsole registrieren
        self.debug_console.register_panel(self)
    
    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🔍 Debug-Konsole")
        title_label.setFont(QFont("", 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Auto-Scroll Checkbox
        self.auto_scroll_cb = QCheckBox("Auto-Scroll")
        self.auto_scroll_cb.setChecked(self.auto_scroll)
        self.auto_scroll_cb.toggled.connect(self._on_auto_scroll_changed)
        header_layout.addWidget(self.auto_scroll_cb)
        
        # Log-Level Combo
        level_label = QLabel("Level:")
        header_layout.addWidget(level_label)
        
        self.level_combo = QComboBox()
        self.level_combo.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR"])
        self.level_combo.setCurrentText("INFO")
        header_layout.addWidget(self.level_combo)
        
        # Clear Button
        self.clear_btn = QPushButton("Löschen")
        self.clear_btn.setIcon(get_icon("clear"))
        self.clear_btn.clicked.connect(self._clear_log)
        header_layout.addWidget(self.clear_btn)
        
        # Export Button
        self.export_btn = QPushButton("Exportieren")
        self.export_btn.setIcon(get_icon("export"))
        self.export_btn.clicked.connect(self._export_log)
        header_layout.addWidget(self.export_btn)
        
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Debug-Text-Area
        self.debug_text = QTextEdit()
        self.debug_text.setFont(QFont("Consolas, Monaco, monospace", 9))
        self.debug_text.setReadOnly(True)
        self.debug_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.debug_text.setPlaceholderText("Debug-Ausgaben erscheinen hier...")
        
        # Styling für Debug-Text
        self.debug_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        
        layout.addWidget(self.debug_text)
        
        # Status-Bar
        status_layout = QHBoxLayout()
        
        self.message_count_label = QLabel("Nachrichten: 0")
        status_layout.addWidget(self.message_count_label)
        
        status_layout.addStretch()
        
        self.last_update_label = QLabel("Letzte Aktualisierung: Nie")
        status_layout.addWidget(self.last_update_label)
        
        layout.addLayout(status_layout)
        
        # Theme anwenden
        self._apply_theme()
    
    def _connect_signals(self):
        """Verbindet Signale."""
        pass
    
    def _apply_theme(self):
        """Wendet das aktuelle Theme an."""
        stylesheet = Styles.get_main_stylesheet()
        self.setStyleSheet(stylesheet)
    
    def add_message(self, message: str):
        """Fügt eine Debug-Nachricht zur Anzeige hinzu."""
        # Filter nach Log-Level (vereinfacht)
        current_level = self.level_combo.currentText()
        if current_level != "ALL":
            if current_level not in message:
                return
        
        # Nachricht hinzufügen
        self.debug_text.append(message)
        
        # Auto-Scroll
        if self.auto_scroll:
            cursor = self.debug_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.debug_text.setTextCursor(cursor)
        
        # Status aktualisieren
        self._update_status()
    
    def clear_messages(self):
        """Löscht alle Nachrichten."""
        self.debug_text.clear()
        self._update_status()
    
    def _update_status(self):
        """Aktualisiert die Status-Anzeige."""
        # Anzahl Nachrichten
        text = self.debug_text.toPlainText()
        line_count = len(text.split('\n')) if text.strip() else 0
        self.message_count_label.setText(f"Nachrichten: {line_count}")
        
        # Letzte Aktualisierung
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_update_label.setText(f"Letzte Aktualisierung: {current_time}")
    
    def _on_auto_scroll_changed(self, checked: bool):
        """Wird aufgerufen, wenn sich der Auto-Scroll-Status ändert."""
        self.auto_scroll = checked
        self.config.set("debug_auto_scroll", checked)
    
    def _clear_log(self):
        """Löscht das Debug-Log."""
        self.debug_console.clear()
    
    def _export_log(self):
        """Exportiert das Debug-Log."""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Debug-Log exportieren",
            f"usb_monitor_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            "Log-Dateien (*.log);;Text-Dateien (*.txt);;Alle Dateien (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.debug_text.toPlainText())
                
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Export erfolgreich",
                    f"Debug-Log wurde erfolgreich exportiert:\n{filename}"
                )
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "Export fehlgeschlagen",
                    f"Fehler beim Exportieren des Debug-Logs:\n{str(e)}"
                )
    
    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Panel geschlossen wird."""
        self.debug_console.unregister_panel(self)
        super().closeEvent(event)


# Globale Debug-Funktionen
def debug_print(message: str, level: str = "INFO"):
    """Globale Debug-Print-Funktion."""
    console = DebugConsole()
    console.add_message(message, level)
    
    # Auch in normale Konsole ausgeben (falls vorhanden)
    print(f"[{level}] {message}")


def debug_info(message: str):
    """Debug-Info-Nachricht."""
    debug_print(message, "INFO")


def debug_warning(message: str):
    """Debug-Warning-Nachricht."""
    debug_print(message, "WARNING")


def debug_error(message: str):
    """Debug-Error-Nachricht."""
    debug_print(message, "ERROR")
