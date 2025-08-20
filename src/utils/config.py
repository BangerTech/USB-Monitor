"""
Konfigurationsmodul für USB-Monitor.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class AppConfig:
    """Anwendungskonfiguration."""
    
    # Allgemeine Einstellungen
    theme: str = "auto"  # "light", "dark", "auto"
    language: str = "de"  # "de", "en"
    auto_refresh: bool = True
    refresh_interval: int = 5000  # Millisekunden
    
    # Fenster-Einstellungen
    window_width: int = 1200
    window_height: int = 800
    window_x: int = 100
    window_y: int = 100
    maximized: bool = False
    
    # USB-Monitor-Einstellungen
    show_disconnected_devices: bool = True
    show_usb_hubs: bool = True
    show_driver_info: bool = True
    show_power_info: bool = True
    
    # COM-Port-Einstellungen
    show_available_ports_only: bool = False
    default_baud_rate: int = 9600
    default_data_bits: int = 8
    default_stop_bits: int = 1
    default_parity: str = "N"
    
    # Benachrichtigungen
    enable_notifications: bool = True
    notify_device_connect: bool = True
    notify_device_disconnect: bool = True
    notify_port_changes: bool = True
    
    # Logging
    enable_logging: bool = True
    log_level: str = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR"
    log_file: str = "usb_monitor.log"
    max_log_size: int = 10  # MB
    max_log_files: int = 5


class Config:
    """Konfigurationsverwaltung für USB-Monitor."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialisiert die Konfiguration."""
        if config_file is None:
            # Standard-Konfigurationsdatei
            config_dir = self._get_config_directory()
            config_file = config_dir / "config.json"
            
        self.config_file = Path(config_file)
        self.config = AppConfig()
        self.load_config()
    
    def _get_config_directory(self) -> Path:
        """Ermittelt das Konfigurationsverzeichnis."""
        if os.name == "nt":  # Windows
            config_dir = Path.home() / "AppData" / "Local" / "USB-Monitor"
        else:  # macOS/Linux
            config_dir = Path.home() / ".config" / "usb-monitor"
            
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def load_config(self) -> None:
        """Lädt die Konfiguration aus der Datei."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    
                # Konfiguration aktualisieren
                for key, value in config_data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                        
        except (json.JSONDecodeError, IOError) as e:
            print(f"Fehler beim Laden der Konfiguration: {e}")
            # Standard-Konfiguration verwenden
            pass
    
    def save_config(self) -> None:
        """Speichert die aktuelle Konfiguration."""
        try:
            # Konfigurationsverzeichnis erstellen
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Konfiguration speichern
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
                
        except IOError as e:
            print(f"Fehler beim Speichern der Konfiguration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Ermittelt einen Konfigurationswert."""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Setzt einen Konfigurationswert."""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save_config()
    
    def update(self, **kwargs) -> None:
        """Aktualisiert mehrere Konfigurationswerte."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.save_config()
    
    def reset_to_defaults(self) -> None:
        """Setzt die Konfiguration auf Standardwerte zurück."""
        self.config = AppConfig()
        self.save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """Gibt alle Konfigurationswerte zurück."""
        return asdict(self.config)
    
    def export_config(self, export_file: str) -> bool:
        """Exportiert die Konfiguration in eine Datei."""
        try:
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def import_config(self, import_file: str) -> bool:
        """Importiert eine Konfiguration aus einer Datei."""
        try:
            with open(import_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                
            # Konfiguration aktualisieren
            for key, value in config_data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    
            self.save_config()
            return True
            
        except (json.JSONDecodeError, IOError):
            return False
    
    def get_theme_colors(self) -> Dict[str, str]:
        """Gibt die Farben für das aktuelle Theme zurück."""
        theme = self.get("theme", "auto")
        
        if theme == "auto":
            # Automatische Theme-Erkennung basierend auf System
            import platform
            if platform.system() == "Darwin":  # macOS
                theme = "dark" if self._is_macos_dark_mode() else "light"
            else:
                theme = "light"
        
        if theme == "dark":
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
        else:  # light theme
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
    
    def _is_macos_dark_mode(self) -> bool:
        """Ermittelt, ob macOS im Dark Mode läuft."""
        try:
            import subprocess
            result = subprocess.run(["defaults", "read", "-g", "AppleInterfaceStyle"], 
                                  capture_output=True, text=True)
            return result.stdout.strip() == "Dark"
        except:
            return False
    
    def get_language_file(self) -> Optional[str]:
        """Ermittelt den Pfad zur Sprachdatei."""
        language = self.get("language", "de")
        config_dir = self._get_config_directory()
        lang_file = config_dir / "languages" / f"{language}.json"
        
        if lang_file.exists():
            return str(lang_file)
        return None
    
    def get_log_file_path(self) -> Path:
        """Ermittelt den Pfad zur Log-Datei."""
        config_dir = self._get_config_directory()
        return config_dir / self.get("log_file", "usb_monitor.log")
    
    def validate_config(self) -> bool:
        """Validiert die aktuelle Konfiguration."""
        try:
            # Überprüfe kritische Werte
            if self.get("refresh_interval", 0) < 1000:
                self.set("refresh_interval", 1000)
                
            if self.get("window_width", 0) < 800:
                self.set("window_width", 800)
                
            if self.get("window_height", 0) < 600:
                self.set("window_height", 600)
                
            return True
            
        except Exception:
            return False
