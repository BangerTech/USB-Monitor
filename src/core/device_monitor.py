"""
USB-Geräte-Überwachung für USB-Monitor.
"""

import time
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging

from utils.platform_utils import PlatformUtils


@dataclass
class USBDevice:
    """Repräsentiert ein USB-Gerät."""
    
    # Grundlegende Informationen
    name: str
    description: str = ""
    device_id: str = ""
    manufacturer: str = ""
    product_id: str = ""
    vendor_id: str = ""
    serial_number: str = ""
    
    # Technische Details
    device_type: str = ""
    usb_version: str = ""
    power_consumption: str = ""
    max_power: str = ""
    current_required: str = ""
    current_available: str = ""
    transfer_speed: str = ""
    max_transfer_speed: str = ""
    driver_version: str = ""
    device_class: str = ""
    device_subclass: str = ""
    device_protocol: str = ""
    
    # Status-Informationen
    is_connected: bool = True
    connection_status: str = "Connected"
    port_number: str = ""
    
    # Zeitstempel
    first_seen: datetime = None
    last_seen: datetime = None
    
    def __post_init__(self):
        """Initialisiert Standardwerte nach der Erstellung."""
        if self.first_seen is None:
            self.first_seen = datetime.now()
        if self.last_seen is None:
            self.last_seen = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Gerät in ein Dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "device_id": self.device_id,
            "manufacturer": self.manufacturer,
            "product_id": self.product_id,
            "vendor_id": self.vendor_id,
            "serial_number": self.serial_number,
            "device_type": self.device_type,
            "usb_version": self.usb_version,
            "power_consumption": self.power_consumption,
            "max_power": self.max_power,
            "current_required": self.current_required,
            "current_available": self.current_available,
            "transfer_speed": self.transfer_speed,
            "max_transfer_speed": self.max_transfer_speed,
            "driver_version": self.driver_version,
            "device_class": self.device_class,
            "device_subclass": self.device_subclass,
            "device_protocol": self.device_protocol,
            "is_connected": self.is_connected,
            "connection_status": self.connection_status,
            "port_number": self.port_number,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'USBDevice':
        """Erstellt ein USBDevice aus einem Dictionary."""
        # Zeitstempel konvertieren
        if "first_seen" in data and data["first_seen"]:
            try:
                data["first_seen"] = datetime.fromisoformat(data["first_seen"])
            except ValueError:
                data["first_seen"] = None
                
        if "last_seen" in data and data["last_seen"]:
            try:
                data["last_seen"] = datetime.fromisoformat(data["last_seen"])
            except ValueError:
                data["last_seen"] = None
        
        return cls(**data)


class DeviceMonitor:
    """Überwacht USB-Geräte und deren Status-Änderungen."""
    
    def __init__(self, config: Any = None):
        """Initialisiert den Device Monitor."""
        self.config = config
        self.devices: List[USBDevice] = []
        self.device_history: List[USBDevice] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_interval = 2.0  # Sekunden
        
        # Callbacks für Status-Änderungen
        self.on_device_connected: Optional[Callable[[USBDevice], None]] = None
        self.on_device_disconnected: Optional[Callable[[USBDevice], None]] = None
        self.on_device_updated: Optional[Callable[[USBDevice], None]] = None
        
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
        try:
            # WMI für Windows
            import wmi
            self.wmi_connection = wmi.WMI()
            self.logger.info("Windows WMI-Verbindung hergestellt")
        except ImportError:
            self.logger.warning("WMI nicht verfügbar, verwende Registry-Fallback")
            self.wmi_connection = None
    
    def _init_macos(self) -> None:
        """macOS-spezifische Initialisierung."""
        self.logger.info("macOS-USB-Monitoring initialisiert")
    
    def _init_linux(self) -> None:
        """Linux-spezifische Initialisierung."""
        self.logger.info("Linux-USB-Monitoring initialisiert")
    
    def start_monitoring(self) -> None:
        """Startet die Geräte-Überwachung."""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("USB-Geräte-Überwachung gestartet")
    
    def stop_monitoring(self) -> None:
        """Stoppt die Geräte-Überwachung."""
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        self.logger.info("USB-Geräte-Überwachung gestoppt")
    
    def _monitor_loop(self) -> None:
        """Hauptschleife für die Geräte-Überwachung."""
        while self.is_monitoring:
            try:
                self._scan_devices()
                time.sleep(self.monitor_interval)
            except Exception as e:
                self.logger.error(f"Fehler in der Überwachungsschleife: {e}")
                time.sleep(self.monitor_interval)
    
    def _scan_devices(self) -> None:
        """Scannt alle verfügbaren USB-Geräte."""
        try:
            current_devices = self._get_current_devices()
            self._update_device_list(current_devices)
        except Exception as e:
            self.logger.error(f"Fehler beim Scannen der Geräte: {e}")
    
    def _get_current_devices(self) -> List[USBDevice]:
        """Ermittelt die aktuell angeschlossenen USB-Geräte."""
        platform = PlatformUtils.get_platform()
        
        if platform == "windows":
            return self._get_windows_devices()
        elif platform == "macos":
            return self._get_macos_devices()
        elif platform == "linux":
            return self._get_linux_devices()
        else:
            return []
    
    def _get_windows_devices(self) -> List[USBDevice]:
        """Ermittelt USB-Geräte unter Windows."""
        devices = []
        
        try:
            # PlatformUtils verwenden (mit Debug-Ausgaben)
            raw_devices = PlatformUtils.get_usb_devices()
            
            print(f"   📊 DeviceMonitor: {len(raw_devices)} Geräte von PlatformUtils erhalten")
            
            for raw_device in raw_devices:
                usb_device = USBDevice(
                    name=raw_device.get("name", "Unknown USB Device"),
                    description=raw_device.get("description", ""),
                    device_id=raw_device.get("device_id", ""),
                    manufacturer=raw_device.get("manufacturer", ""),
                    product_id=raw_device.get("product_id", ""),
                    vendor_id=raw_device.get("vendor_id", ""),
                    serial_number=raw_device.get("serial_number", ""),
                    device_type=raw_device.get("device_type", "USB Device"),
                    usb_version=raw_device.get("usb_version", ""),
                    power_consumption=raw_device.get("power_consumption", ""),
                    max_power=raw_device.get("max_power", ""),
                    current_required=raw_device.get("current_required", ""),
                    current_available=raw_device.get("current_available", ""),
                    transfer_speed=raw_device.get("transfer_speed", ""),
                    max_transfer_speed=raw_device.get("max_transfer_speed", ""),
                    device_class=raw_device.get("device_class", ""),
                    device_subclass=raw_device.get("device_subclass", ""),
                    device_protocol=raw_device.get("device_protocol", ""),
                    is_connected=raw_device.get("is_connected", True),
                    connection_status=raw_device.get("status", "OK")
                )
                devices.append(usb_device)
                print(f"   ✅ DeviceMonitor: USB-Gerät hinzugefügt: {usb_device.name}")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Windows-USB-Geräte: {e}")
            print(f"   ❌ DeviceMonitor: Fehler beim Abrufen der Windows-USB-Geräte: {e}")
            
        print(f"   📊 DeviceMonitor: Insgesamt {len(devices)} USB-Geräte für GUI bereit")
        return devices
    
    def _get_windows_devices_registry(self) -> List[USBDevice]:
        """Ermittelt USB-Geräte über die Windows-Registry."""
        devices = []
        
        try:
            import winreg
            
            # USB-Controller
            key_path = r"SYSTEM\CurrentControlSet\Services\USBSTOR\Enum"
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                i = 0
                while True:
                    try:
                        device_id = winreg.EnumValue(key, i)[1]
                        usb_device = USBDevice(
                            name=f"USB Storage Device {i+1}",
                            device_id=device_id,
                            device_type="Storage",
                            is_connected=True
                        )
                        devices.append(usb_device)
                        i += 1
                    except WindowsError:
                        break
                winreg.CloseKey(key)
            except WindowsError:
                pass
                
        except Exception as e:
            self.logger.error(f"Fehler beim Registry-Zugriff: {e}")
            
        return devices
    
    def _get_macos_devices(self) -> List[USBDevice]:
        """Ermittelt USB-Geräte unter macOS."""
        devices = []
        
        try:
            # PlatformUtils verwenden, da es bereits funktioniert
            raw_devices = PlatformUtils.get_usb_devices()
            
            for raw_device in raw_devices:
                usb_device = USBDevice(
                    name=raw_device.get("name", "Unknown USB Device"),
                    description=raw_device.get("description", ""),
                    device_id=raw_device.get("device_id", ""),
                    manufacturer=raw_device.get("manufacturer", ""),
                    product_id=raw_device.get("product_id", ""),
                    vendor_id=raw_device.get("vendor_id", ""),
                    serial_number=raw_device.get("serial_number", ""),
                    device_type=raw_device.get("device_type", "USB Device"),
                    usb_version=raw_device.get("usb_version", ""),
                    power_consumption=raw_device.get("power_consumption", ""),
                    max_power=raw_device.get("max_power", ""),
                    current_required=raw_device.get("current_required", ""),
                    current_available=raw_device.get("current_available", ""),
                    transfer_speed=raw_device.get("transfer_speed", ""),
                    max_transfer_speed=raw_device.get("max_transfer_speed", ""),
                    device_class=raw_device.get("device_class", ""),
                    device_subclass=raw_device.get("device_subclass", ""),
                    device_protocol=raw_device.get("device_protocol", ""),
                    is_connected=raw_device.get("is_connected", True)
                )
                devices.append(usb_device)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der macOS-USB-Geräte: {e}")
            
        return devices
    
    def _create_macos_device(self, device_data: Dict[str, str]) -> USBDevice:
        """Erstellt ein USBDevice aus macOS-Gerätedaten."""
        return USBDevice(
            name=f"USB Device {device_data.get('product_id', 'Unknown')}",
            manufacturer=device_data.get('manufacturer', ''),
            product_id=device_data.get('product_id', ''),
            vendor_id=device_data.get('vendor_id', ''),
            serial_number=device_data.get('serial_number', ''),
            device_type="USB Device",
            usb_version=device_data.get('version', ''),
            is_connected=True
        )
    
    def _get_linux_devices(self) -> List[USBDevice]:
        """Ermittelt USB-Geräte unter Linux."""
        devices = []
        
        try:
            # /proc/bus/usb/devices lesen
            with open("/proc/bus/usb/devices", "r") as f:
                content = f.read()
                
            # USB-Geräte parsen
            device_blocks = content.split("\n\n")
            
            for block in device_blocks:
                if not block.strip():
                    continue
                    
                device_info = {}
                lines = block.split("\n")
                
                for line in lines:
                    if line.startswith("S:"):
                        device_info["serial"] = line.split("=", 1)[1] if "=" in line else ""
                    elif line.startswith("P:"):
                        device_info["product"] = line.split("=", 1)[1] if "=" in line else ""
                    elif line.startswith("M:"):
                        device_info["manufacturer"] = line.split("=", 1)[1] if "=" in line else ""
                        
                if device_info:
                    usb_device = USBDevice(
                        name=device_info.get("product", "Linux USB Device"),
                        manufacturer=device_info.get("manufacturer", ""),
                        serial_number=device_info.get("serial", ""),
                        device_type="USB Device",
                        is_connected=True
                    )
                    devices.append(usb_device)
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Linux-USB-Geräte: {e}")
            
        return devices
    
    def _update_device_list(self, current_devices: List[USBDevice]) -> None:
        """Aktualisiert die Geräteliste und erkennt Änderungen."""
        # Neue Geräte hinzufügen
        for current_device in current_devices:
            existing_device = self._find_device_by_id(current_device.device_id)
            
            if existing_device is None:
                # Neues Gerät
                self.devices.append(current_device)
                self.device_history.append(current_device)
                
                if self.on_device_connected:
                    self.on_device_connected(current_device)
                    
                self.logger.info(f"Neues USB-Gerät verbunden: {current_device.name}")
                
            else:
                # Bestehendes Gerät aktualisieren
                if existing_device.is_connected != current_device.is_connected:
                    existing_device.is_connected = current_device.is_connected
                    existing_device.connection_status = "Connected" if current_device.is_connected else "Disconnected"
                    
                    if current_device.is_connected and self.on_device_connected:
                        self.on_device_connected(existing_device)
                    elif not current_device.is_connected and self.on_device_disconnected:
                        self.on_device_disconnected(existing_device)
                        
                existing_device.last_seen = datetime.now()
                
                if self.on_device_updated:
                    self.on_device_updated(existing_device)
        
        # Nicht mehr verbundene Geräte markieren
        for existing_device in self.devices:
            if not any(d.device_id == existing_device.device_id for d in current_devices):
                if existing_device.is_connected:
                    existing_device.is_connected = False
                    existing_device.connection_status = "Disconnected"
                    
                    if self.on_device_disconnected:
                        self.on_device_disconnected(existing_device)
                        
                    self.logger.info(f"USB-Gerät getrennt: {existing_device.name}")
    
    def _find_device_by_id(self, device_id: str) -> Optional[USBDevice]:
        """Findet ein Gerät anhand seiner ID."""
        for device in self.devices:
            if device.device_id == device_id:
                return device
        return None
    
    def get_connected_devices(self) -> List[USBDevice]:
        """Gibt alle verbundenen USB-Geräte zurück."""
        return [device for device in self.devices if device.is_connected]
    
    def get_disconnected_devices(self) -> List[USBDevice]:
        """Gibt alle getrennten USB-Geräte zurück."""
        return [device for device in self.devices if not device.is_connected]
    
    def get_all_devices(self) -> List[USBDevice]:
        """Gibt alle USB-Geräte zurück."""
        return self.devices.copy()
    
    def get_device_by_name(self, name: str) -> Optional[USBDevice]:
        """Findet ein Gerät anhand seines Namens."""
        for device in self.devices:
            if device.name == name:
                return device
        return None
    
    def refresh_devices(self) -> None:
        """Aktualisiert die Geräteliste manuell."""
        try:
            current_devices = self._get_current_devices()
            self._update_device_list(current_devices)
            self.logger.info("Geräteliste manuell aktualisiert")
        except Exception as e:
            self.logger.error(f"Fehler beim manuellen Aktualisieren: {e}")
    
    def clear_history(self) -> None:
        """Löscht den Geräteverlauf."""
        self.device_history.clear()
        self.logger.info("Geräteverlauf gelöscht")
    
    def export_devices(self, filename: str) -> bool:
        """Exportiert die Geräteliste in eine Datei."""
        try:
            import json
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([device.to_dict() for device in self.devices], f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Geräteliste exportiert nach: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Exportieren: {e}")
            return False
    
    def get_device_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über die USB-Geräte zurück."""
        total_devices = len(self.devices)
        connected_devices = len(self.get_connected_devices())
        disconnected_devices = len(self.get_disconnected_devices())
        
        # Gerätetypen zählen
        device_types = {}
        for device in self.devices:
            device_type = device.device_type or "Unknown"
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        # Hersteller zählen
        manufacturers = {}
        for device in self.devices:
            manufacturer = device.manufacturer or "Unknown"
            manufacturers[manufacturer] = manufacturers.get(manufacturer, 0) + 1
        
        return {
            "total_devices": total_devices,
            "connected_devices": connected_devices,
            "disconnected_devices": disconnected_devices,
            "device_types": device_types,
            "manufacturers": manufacturers,
            "last_scan": datetime.now().isoformat()
        }
