"""
COM-Port-Überwachung für USB-Monitor.
"""

import time
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging

from utils.platform_utils import PlatformUtils


@dataclass
class COMPort:
    """Repräsentiert einen COM-Port."""
    
    # Grundlegende Informationen
    port_name: str
    device_name: str = ""
    description: str = ""
    
    # Serielle Port-Einstellungen
    baud_rate: int = 9600
    data_bits: int = 8
    stop_bits: int = 1
    parity: str = "N"  # N, E, O
    flow_control: str = "None"  # None, XON/XOFF, RTS/CTS
    
    # Status-Informationen
    is_available: bool = True
    is_open: bool = False
    last_used: Optional[datetime] = None
    
    # Zusätzliche Informationen
    manufacturer: str = ""
    product_id: str = ""
    vendor_id: str = ""
    serial_number: str = ""
    
    # Zeitstempel
    created_at: datetime = None
    
    def __post_init__(self):
        """Initialisiert Standardwerte nach der Erstellung."""
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert den Port in ein Dictionary."""
        return {
            "port_name": self.port_name,
            "device_name": self.device_name,
            "description": self.description,
            "baud_rate": self.baud_rate,
            "data_bits": self.data_bits,
            "stop_bits": self.stop_bits,
            "parity": self.parity,
            "flow_control": self.flow_control,
            "is_available": self.is_available,
            "is_open": self.is_open,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "manufacturer": self.manufacturer,
            "product_id": self.product_id,
            "vendor_id": self.vendor_id,
            "serial_number": self.serial_number,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'COMPort':
        """Erstellt einen COMPort aus einem Dictionary."""
        # Zeitstempel konvertieren
        if "last_used" in data and data["last_used"]:
            try:
                data["last_used"] = datetime.fromisoformat(data["last_used"])
            except ValueError:
                data["last_used"] = None
                
        if "created_at" in data and data["created_at"]:
            try:
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            except ValueError:
                data["created_at"] = None
        
        return cls(**data)


class PortMonitor:
    """Überwacht COM-Ports und deren Status-Änderungen."""
    
    def __init__(self, config: Any = None):
        """Initialisiert den Port Monitor."""
        self.config = config
        self.ports: List[COMPort] = []
        self.port_history: List[COMPort] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_interval = 3.0  # Sekunden
        
        # Callbacks für Status-Änderungen
        self.on_port_added: Optional[Callable[[COMPort], None]] = None
        self.on_port_removed: Optional[Callable[[COMPort], None]] = None
        self.on_port_status_changed: Optional[Callable[[COMPort], None]] = None
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Plattform-spezifische Initialisierung
        self._init_platform_specific()
    
    def _init_platform_specific(self) -> None:
        """Initialisiert plattformspezifische Komponenten."""
        platform = PlatformUtils.get_platform()
        
        if platform == "windows":
            self._init_windows()
        elif platform == "macos":
            self._init_macos()
        elif platform == "linux":
            self._init_linux()
    
    def _init_windows(self) -> None:
        """Windows-spezifische Initialisierung."""
        self.logger.info("Windows COM-Port-Monitoring initialisiert")
    
    def _init_macos(self) -> None:
        """macOS-spezifische Initialisierung."""
        self.logger.info("macOS COM-Port-Monitoring initialisiert")
    
    def _init_linux(self) -> None:
        """Linux-spezifische Initialisierung."""
        self.logger.info("Linux COM-Port-Monitoring initialisiert")
    
    def start_monitoring(self) -> None:
        """Startet die Port-Überwachung."""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("COM-Port-Überwachung gestartet")
    
    def stop_monitoring(self) -> None:
        """Stoppt die Port-Überwachung."""
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        self.logger.info("COM-Port-Überwachung gestoppt")
    
    def _monitor_loop(self) -> None:
        """Hauptschleife für die Port-Überwachung."""
        while self.is_monitoring:
            try:
                self._scan_ports()
                time.sleep(self.monitor_interval)
            except Exception as e:
                self.logger.error(f"Fehler in der Port-Überwachungsschleife: {e}")
                time.sleep(self.monitor_interval)
    
    def _scan_ports(self) -> None:
        """Scannt alle verfügbaren COM-Ports."""
        try:
            current_ports = self._get_current_ports()
            self._update_port_list(current_ports)
        except Exception as e:
            self.logger.error(f"Fehler beim Scannen der Ports: {e}")
    
    def _get_current_ports(self) -> List[COMPort]:
        """Ermittelt die aktuell verfügbaren COM-Ports."""
        platform = PlatformUtils.get_platform()
        
        if platform == "windows":
            return self._get_windows_ports()
        elif platform == "macos":
            return self._get_macos_ports()
        elif platform == "linux":
            return self._get_linux_ports()
        else:
            return []
    
    def _get_windows_ports(self) -> List[COMPort]:
        """Ermittelt COM-Ports unter Windows."""
        ports = []
        
        try:
            import serial.tools.list_ports
            
            for port_info in serial.tools.list_ports.comports():
                # pyserial ListPortInfo attribute names are: vid, pid, manufacturer, product, serial_number
                vid = getattr(port_info, 'vid', None)
                pid = getattr(port_info, 'pid', None)
                manufacturer = getattr(port_info, 'manufacturer', '') or ''
                product = getattr(port_info, 'product', '') or ''
                serial_number = getattr(port_info, 'serial_number', '') or ''

                com_port = COMPort(
                    port_name=port_info.device,
                    device_name=getattr(port_info, 'name', '') or '',
                    description=getattr(port_info, 'description', '') or '',
                    manufacturer=manufacturer,
                    product_id=(f"{pid:04X}" if isinstance(pid, int) else str(pid or '')),
                    vendor_id=(f"{vid:04X}" if isinstance(vid, int) else str(vid or '')),
                    serial_number=serial_number,
                    is_available=True
                )
                ports.append(com_port)
                
        except ImportError:
            # Fallback: Plattform-Utils verwenden
            port_names = PlatformUtils.get_available_com_ports()
            for port_name in port_names:
                com_port = COMPort(
                    port_name=port_name,
                    device_name=f"Device on {port_name}",
                    is_available=True
                )
                ports.append(com_port)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Windows-COM-Ports: {e}")
            
        return ports
    
    def _get_macos_ports(self) -> List[COMPort]:
        """Ermittelt COM-Ports unter macOS."""
        ports = []
        
        try:
            import serial.tools.list_ports
            
            for port_info in serial.tools.list_ports.comports():
                vid = getattr(port_info, 'vid', None)
                pid = getattr(port_info, 'pid', None)
                manufacturer = getattr(port_info, 'manufacturer', '') or ''
                product = getattr(port_info, 'product', '') or ''
                serial_number = getattr(port_info, 'serial_number', '') or ''

                com_port = COMPort(
                    port_name=port_info.device,
                    device_name=getattr(port_info, 'name', '') or '',
                    description=getattr(port_info, 'description', '') or '',
                    manufacturer=manufacturer,
                    product_id=(f"{pid:04X}" if isinstance(pid, int) else str(pid or '')),
                    vendor_id=(f"{vid:04X}" if isinstance(vid, int) else str(vid or '')),
                    serial_number=serial_number,
                    is_available=True
                )
                ports.append(com_port)
                
        except ImportError:
            # Fallback: Plattform-Utils verwenden
            port_names = PlatformUtils.get_available_com_ports()
            for port_name in port_names:
                com_port = COMPort(
                    port_name=port_name,
                    device_name=f"Device on {port_name}",
                    is_available=True
                )
                ports.append(com_port)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der macOS-COM-Ports: {e}")
            
        return ports
    
    def _get_linux_ports(self) -> List[COMPort]:
        """Ermittelt COM-Ports unter Linux."""
        ports = []
        
        try:
            import serial.tools.list_ports
            
            for port_info in serial.tools.list_ports.comports():
                vid = getattr(port_info, 'vid', None)
                pid = getattr(port_info, 'pid', None)
                manufacturer = getattr(port_info, 'manufacturer', '') or ''
                product = getattr(port_info, 'product', '') or ''
                serial_number = getattr(port_info, 'serial_number', '') or ''

                com_port = COMPort(
                    port_name=port_info.device,
                    device_name=getattr(port_info, 'name', '') or '',
                    description=getattr(port_info, 'description', '') or '',
                    manufacturer=manufacturer,
                    product_id=(f"{pid:04X}" if isinstance(pid, int) else str(pid or '')),
                    vendor_id=(f"{vid:04X}" if isinstance(vid, int) else str(vid or '')),
                    serial_number=serial_number,
                    is_available=True
                )
                ports.append(com_port)
                
        except ImportError:
            # Fallback: Plattform-Utils verwenden
            port_names = PlatformUtils.get_available_com_ports()
            for port_name in port_names:
                com_port = COMPort(
                    port_name=port_name,
                    device_name=f"Device on {port_name}",
                    is_available=True
                )
                ports.append(com_port)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Linux-COM-Ports: {e}")
            
        return ports
    
    def _update_port_list(self, current_ports: List[COMPort]) -> None:
        """Aktualisiert die Portliste und erkennt Änderungen."""
        # Neue Ports hinzufügen
        for current_port in current_ports:
            existing_port = self._find_port_by_name(current_port.port_name)
            
            if existing_port is None:
                # Neuer Port
                self.ports.append(current_port)
                self.port_history.append(current_port)
                
                if self.on_port_added:
                    self.on_port_added(current_port)
                    
                self.logger.info(f"Neuer COM-Port gefunden: {current_port.port_name}")
                
            else:
                # Bestehenden Port aktualisieren
                if existing_port.is_available != current_port.is_available:
                    existing_port.is_available = current_port.is_available
                    
                    if self.on_port_status_changed:
                        self.on_port_status_changed(existing_port)
                        
                # Weitere Informationen aktualisieren
                existing_port.device_name = current_port.device_name
                existing_port.description = current_port.description
                existing_port.manufacturer = current_port.manufacturer
                existing_port.product_id = current_port.product_id
                existing_port.vendor_id = current_port.vendor_id
                existing_port.serial_number = current_port.serial_number
        
        # Nicht mehr verfügbare Ports markieren
        for existing_port in self.ports:
            if not any(p.port_name == existing_port.port_name for p in current_ports):
                if existing_port.is_available:
                    existing_port.is_available = False
                    
                    if self.on_port_status_changed:
                        self.on_port_status_changed(existing_port)
                        
                    self.logger.info(f"COM-Port nicht mehr verfügbar: {existing_port.port_name}")
    
    def _find_port_by_name(self, port_name: str) -> Optional[COMPort]:
        """Findet einen Port anhand seines Namens."""
        for port in self.ports:
            if port.port_name == port_name:
                return port
        return None
    
    def get_available_ports(self) -> List[COMPort]:
        """Gibt alle verfügbaren COM-Ports zurück."""
        return [port for port in self.ports if port.is_available]
    
    def get_unavailable_ports(self) -> List[COMPort]:
        """Gibt alle nicht verfügbaren COM-Ports zurück."""
        return [port for port in self.ports if not port.is_available]
    
    def get_all_ports(self) -> List[COMPort]:
        """Gibt alle COM-Ports zurück."""
        return self.ports.copy()
    
    def get_port_by_name(self, port_name: str) -> Optional[COMPort]:
        """Findet einen Port anhand seines Namens."""
        return self._find_port_by_name(port_name)
    
    def test_port(self, port_name: str, baud_rate: int = 9600) -> bool:
        """Testet, ob ein Port geöffnet werden kann."""
        try:
            import serial
            
            with serial.Serial(port_name, baud_rate, timeout=1) as ser:
                return True
                
        except Exception as e:
            self.logger.debug(f"Port-Test fehlgeschlagen für {port_name}: {e}")
            return False
    
    def open_port(self, port_name: str, **kwargs) -> Optional[Any]:
        """Öffnet einen COM-Port."""
        try:
            import serial
            
            # Standardwerte aus der Konfiguration
            if self.config:
                baud_rate = kwargs.get('baud_rate', self.config.get('default_baud_rate', 9600))
                data_bits = kwargs.get('data_bits', self.config.get('default_data_bits', 8))
                stop_bits = kwargs.get('stop_bits', self.config.get('default_stop_bits', 1))
                parity = kwargs.get('parity', self.config.get('default_parity', 'N'))
            else:
                baud_rate = kwargs.get('baud_rate', 9600)
                data_bits = kwargs.get('data_bits', 8)
                stop_bits = kwargs.get('stop_bits', 1)
                parity = kwargs.get('parity', 'N')
            
            # Parity konvertieren
            parity_map = {'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN, 'O': serial.PARITY_ODD}
            parity_value = parity_map.get(parity, serial.PARITY_NONE)
            
            # Port öffnen
            ser = serial.Serial(
                port=port_name,
                baudrate=baud_rate,
                bytesize=data_bits,
                stopbits=stop_bits,
                parity=parity_value,
                timeout=kwargs.get('timeout', 1)
            )
            
            # Port-Status aktualisieren
            port = self.get_port_by_name(port_name)
            if port:
                port.is_open = True
                port.last_used = datetime.now()
                
                if self.on_port_status_changed:
                    self.on_port_status_changed(port)
            
            return ser
            
        except Exception as e:
            self.logger.error(f"Fehler beim Öffnen des Ports {port_name}: {e}")
            return None
    
    def close_port(self, port_name: str) -> bool:
        """Schließt einen COM-Port."""
        try:
            port = self.get_port_by_name(port_name)
            if port:
                port.is_open = False
                
                if self.on_port_status_changed:
                    self.on_port_status_changed(port)
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Schließen des Ports {port_name}: {e}")
            return False
    
    def refresh_ports(self) -> None:
        """Aktualisiert die Portliste manuell."""
        try:
            current_ports = self._get_current_ports()
            self._update_port_list(current_ports)
            self.logger.info("Portliste manuell aktualisiert")
        except Exception as e:
            self.logger.error(f"Fehler beim manuellen Aktualisieren: {e}")
    
    def clear_history(self) -> None:
        """Löscht den Portverlauf."""
        self.port_history.clear()
        self.logger.info("Portverlauf gelöscht")
    
    def export_ports(self, filename: str) -> bool:
        """Exportiert die Portliste in eine Datei."""
        try:
            import json
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([port.to_dict() for port in self.ports], f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Portliste exportiert nach: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Exportieren: {e}")
            return False
    
    def get_port_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über die COM-Ports zurück."""
        total_ports = len(self.ports)
        available_ports = len(self.get_available_ports())
        unavailable_ports = len(self.get_unavailable_ports())
        open_ports = len([port for port in self.ports if port.is_open])
        
        # Port-Typen zählen (basierend auf Namen)
        port_types = {}
        for port in self.ports:
            if "USB" in port.port_name.upper():
                port_type = "USB Serial"
            elif "COM" in port.port_name.upper():
                port_type = "Windows COM"
            elif "TTY" in port.port_name.upper():
                port_type = "TTY"
            else:
                port_type = "Other"
                
            port_types[port_type] = port_types.get(port_type, 0) + 1
        
        return {
            "total_ports": total_ports,
            "available_ports": available_ports,
            "unavailable_ports": unavailable_ports,
            "open_ports": open_ports,
            "port_types": port_types,
            "last_scan": datetime.now().isoformat()
        }
    
    def get_baud_rates(self) -> List[int]:
        """Gibt eine Liste der verfügbaren Baud-Raten zurück."""
        return [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
    
    def get_data_bits(self) -> List[int]:
        """Gibt eine Liste der verfügbaren Datenbits zurück."""
        return [5, 6, 7, 8]
    
    def get_stop_bits(self) -> List[float]:
        """Gibt eine Liste der verfügbaren Stop-Bits zurück."""
        return [1, 1.5, 2]
    
    def get_parity_options(self) -> List[str]:
        """Gibt eine Liste der verfügbaren Paritätsoptionen zurück."""
        return ["N", "E", "O"]
