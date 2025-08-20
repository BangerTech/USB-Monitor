"""
Plattform-spezifische Hilfsfunktionen für USB-Monitor.
"""

import platform
import sys
from typing import List, Dict, Any, Optional
import subprocess
import re

# Debug-Funktionen importieren
try:
    from ui.debug_panel import debug_info, debug_warning, debug_error
except ImportError:
    # Fallback für den Fall, dass Debug-Panel nicht verfügbar ist
    def debug_info(msg): print(f"[INFO] {msg}")
    def debug_warning(msg): print(f"[WARNING] {msg}")
    def debug_error(msg): print(f"[ERROR] {msg}")


class PlatformUtils:
    """Plattform-spezifische Hilfsfunktionen."""
    
    @staticmethod
    def get_platform() -> str:
        """Ermittelt die aktuelle Plattform."""
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        else:
            return "unknown"
    
    @staticmethod
    def is_macos() -> bool:
        """Prüft, ob die Anwendung auf macOS läuft."""
        return PlatformUtils.get_platform() == "macos"
    
    @staticmethod
    def is_windows() -> bool:
        """Prüft, ob die Anwendung auf Windows läuft."""
        return PlatformUtils.get_platform() == "windows"
    
    @staticmethod
    def is_linux() -> bool:
        """Prüft, ob die Anwendung auf Linux läuft."""
        return PlatformUtils.get_platform() == "linux"
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Ermittelt detaillierte System-Informationen."""
        info = {
            "platform": PlatformUtils.get_platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }
        
        if PlatformUtils.is_macos():
            info.update(PlatformUtils._get_macos_info())
        elif PlatformUtils.is_windows():
            info.update(PlatformUtils._get_windows_info())
        elif PlatformUtils.is_linux():
            info.update(PlatformUtils._get_linux_info())
            
        return info
    
    @staticmethod
    def _get_macos_info() -> Dict[str, Any]:
        """Ermittelt macOS-spezifische Informationen."""
        info = {}
        
        try:
            # macOS-Version
            result = subprocess.run(["sw_vers", "-productVersion"], 
                                  capture_output=True, text=True, check=True)
            info["macos_version"] = result.stdout.strip()
            
            # Build-Nummer
            result = subprocess.run(["sw_vers", "-buildVersion"], 
                                  capture_output=True, text=True, check=True)
            info["build_version"] = result.stdout.strip()
            
            # Produktname
            result = subprocess.run(["sw_vers", "-productName"], 
                                  capture_output=True, text=True, check=True)
            info["product_name"] = result.stdout.strip()
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        return info
    
    @staticmethod
    def _get_windows_info() -> Dict[str, Any]:
        """Ermittelt Windows-spezifische Informationen."""
        info = {}
        
        try:
            # Windows-Version
            result = subprocess.run(["ver"], 
                                  capture_output=True, text=True, check=True, shell=True)
            info["windows_version"] = result.stdout.strip()
            
            # Systeminfo
            result = subprocess.run(["systeminfo"], 
                                  capture_output=True, text=True, check=True, shell=True)
            info["system_info"] = result.stdout.strip()
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        return info
    
    @staticmethod
    def _get_linux_info() -> Dict[str, Any]:
        """Ermittelt Linux-spezifische Informationen."""
        info = {}
        
        try:
            # Linux-Distribution
            with open("/etc/os-release", "r") as f:
                content = f.read()
                for line in content.split("\n"):
                    if line.startswith("PRETTY_NAME="):
                        info["distribution"] = line.split("=", 1)[1].strip('"')
                        break
                        
            # Kernel-Version
            result = subprocess.run(["uname", "-r"], 
                                  capture_output=True, text=True, check=True)
            info["kernel_version"] = result.stdout.strip()
            
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
            
        return info
    
    @staticmethod
    def get_available_com_ports() -> List[str]:
        """Ermittelt alle verfügbaren COM-Ports."""
        if PlatformUtils.is_windows():
            return PlatformUtils._get_windows_com_ports()
        elif PlatformUtils.is_macos():
            return PlatformUtils._get_macos_com_ports()
        elif PlatformUtils.is_linux():
            return PlatformUtils._get_linux_com_ports()
        else:
            return []
    
    @staticmethod
    def _get_windows_com_ports() -> List[str]:
        """Ermittelt COM-Ports unter Windows."""
        ports = []
        
        try:
            # Windows Management Instrumentation (WMI) verwenden
            import wmi
            c = wmi.WMI()
            for item in c.Win32_SerialPort():
                ports.append(item.DeviceID)
        except ImportError:
            # Fallback: Registry abfragen
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"HARDWARE\DEVICEMAP\SERIALCOMM")
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        if value.startswith("COM"):
                            ports.append(value)
                        i += 1
                    except WindowsError:
                        break
                winreg.CloseKey(key)
            except:
                pass
                
        return sorted(ports)
    
    @staticmethod
    def _get_macos_com_ports() -> List[str]:
        """Ermittelt COM-Ports unter macOS."""
        ports = []
        
        try:
            # System Profiler verwenden
            result = subprocess.run(["system_profiler", "SPUSBDataType"], 
                                  capture_output=True, text=True, check=True)
            
            # Nach seriellen Ports suchen
            lines = result.stdout.split("\n")
            for line in lines:
                if "Serial Number:" in line or "Product ID:" in line:
                    # Port-Namen extrahieren
                    port_match = re.search(r"tty\.usbserial-[a-zA-Z0-9]+", line)
                    if port_match:
                        ports.append(port_match.group())
                        
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        # Auch /dev Verzeichnis durchsuchen
        try:
            import glob
            tty_ports = glob.glob("/dev/tty.usbserial-*")
            ports.extend(tty_ports)
        except:
            pass
            
        return sorted(list(set(ports)))
    
    @staticmethod
    def _get_linux_com_ports() -> List[str]:
        """Ermittelt COM-Ports unter Linux."""
        ports = []
        
        try:
            import glob
            # Verschiedene serielle Port-Patterns
            patterns = [
                "/dev/ttyUSB*",
                "/dev/ttyACM*",
                "/dev/ttyS*",
                "/dev/ttyAMA*"
            ]
            
            for pattern in patterns:
                ports.extend(glob.glob(pattern))
                
        except:
            pass
            
        return sorted(ports)
    
    @staticmethod
    def get_usb_devices() -> List[Dict[str, Any]]:
        """Ermittelt alle USB-Geräte."""
        if PlatformUtils.is_windows():
            return PlatformUtils._get_windows_usb_devices()
        elif PlatformUtils.is_macos():
            return PlatformUtils._get_macos_usb_devices()
        elif PlatformUtils.is_linux():
            return PlatformUtils._get_linux_usb_devices()
        else:
            return []
    
    @staticmethod
    def _get_windows_usb_devices() -> List[Dict[str, Any]]:
        """Ermittelt USB-Geräte unter Windows."""
        devices = []
        
        debug_info("🔍 Starte Windows USB-Geräte-Erkennung...")
        
        # Methode 1: Windows Registry (zuverlässiger als WMI)
        devices.extend(PlatformUtils._get_windows_usb_devices_registry())
        
        # Methode 2: COM-Ports als USB-Geräte
        devices.extend(PlatformUtils._get_windows_usb_devices_com_ports())
        
        # Methode 3: WMI als Fallback (falls verfügbar)
        try:
            import wmi
            import pythoncom
            debug_info("✅ WMI verfügbar - verwende als zusätzliche Quelle")
            
            devices.extend(PlatformUtils._get_windows_usb_devices_wmi())
        except ImportError:
            debug_warning("⚠️ WMI nicht verfügbar - verwende nur Registry/COM-Port-Methoden")
        
        # Duplikate entfernen
        unique_devices = []
        seen_ids = set()
        
        for device in devices:
            device_id = device.get("device_id", "")
            if device_id and device_id not in seen_ids:
                unique_devices.append(device)
                seen_ids.add(device_id)
            elif not device_id:  # Geräte ohne ID trotzdem hinzufügen
                unique_devices.append(device)
        
        # Zusätzlich: USB-Controller-Informationen sammeln für bessere Geschwindigkeitserkennung
        controller_info = PlatformUtils._get_usb_controller_info()
        debug_info(f"USB-Controller gefunden: {controller_info}")
        
        # USB-Versionen basierend auf Controller-Info korrigieren
        for device in unique_devices:
            device_corrected = PlatformUtils._correct_usb_version_by_controller(device, controller_info)
            if device_corrected:
                device.update(device_corrected)
        
        debug_info(f"📊 Insgesamt {len(unique_devices)} eindeutige USB-Geräte gefunden")
        return unique_devices
    
    @staticmethod
    def _get_windows_usb_devices_wmi() -> List[Dict[str, Any]]:
        """Ermittelt USB-Geräte über WMI (falls verfügbar)."""
        devices = []
        
        try:
            import wmi
            import pythoncom
            
            # COM initialisieren
            pythoncom.CoInitialize()
            
            try:
                c = wmi.WMI()
                print("   🔍 Suche nach WMI USB-Geräten...")
                
                # Win32_PnPEntity für USB-Geräte
                for device in c.Win32_PnPEntity():
                    if device.DeviceID and "USB" in device.DeviceID:
                        device_info = {
                            "name": device.Name or "WMI USB Device",
                            "description": device.Description or "",
                            "device_id": device.DeviceID or "",
                            "manufacturer": device.Manufacturer or "",
                            "status": device.Status or "OK",
                            "is_connected": True,
                            "device_type": "USB Device",
                            "usb_version": "USB 2.0/3.0",
                            "product_id": "",
                            "vendor_id": "",
                            "serial_number": "",
                            "driver": device.Name or "",
                            "power_consumption": "Standard",
                            "max_power": "500 mA",
                            "current_required": "Unknown",
                            "current_available": "500 mA",
                            "transfer_speed": "Unknown",
                            "max_transfer_speed": "480 Mb/s",
                            "device_class": "Unknown",
                            "device_subclass": "",
                            "device_protocol": ""
                        }
                        
                        # VID/PID extrahieren
                        if device.DeviceID:
                            parts = device.DeviceID.split("\\")
                            if len(parts) >= 2:
                                vid_pid = parts[1]
                                if "VID_" in vid_pid and "PID_" in vid_pid:
                                    vid_match = re.search(r"VID_([A-F0-9]{4})", vid_pid)
                                    pid_match = re.search(r"PID_([A-F0-9]{4})", vid_pid)
                                    if vid_match:
                                        device_info["vendor_id"] = vid_match.group(1)
                                    if pid_match:
                                        device_info["product_id"] = pid_match.group(1)
                        
                        devices.append(device_info)
                        print(f"   ✅ WMI-USB-Gerät gefunden: {device.Name}")
                        
            finally:
                pythoncom.CoUninitialize()
                
        except Exception as e:
            print(f"   ❌ WMI-Zugriff fehlgeschlagen: {e}")
        
        print(f"   📊 {len(devices)} WMI-USB-Geräte gefunden")
        return devices
    
    @staticmethod
    def _get_macos_usb_devices() -> List[Dict[str, Any]]:
        """Ermittelt USB-Geräte unter macOS."""
        devices = []
        
        try:
            # System Profiler verwenden
            result = subprocess.run(["system_profiler", "SPUSBDataType"], 
                                  capture_output=True, text=True, check=True)
            
            lines = result.stdout.split("\n")
            
            # Einfache Methode: Alle Zeilen mit Product ID und Vendor ID finden
            product_lines = []
            vendor_lines = []
            
            for line in lines:
                line = line.strip()
                if line.startswith("Product ID:"):
                    product_lines.append(line)
                elif line.startswith("Vendor ID:"):
                    vendor_lines.append(line)
            
            # Alle Geräte mit Product ID und Vendor ID erstellen
            for i in range(min(len(product_lines), len(vendor_lines))):
                product_id = product_lines[i].split(":", 1)[1].strip()
                vendor_id = vendor_lines[i].split(":", 1)[1].strip()
                
                # Vendor ID bereinigen (nur Hex-Code)
                if "(" in vendor_id:
                    vendor_id = vendor_id.split("(")[0].strip()
                
                # Echten Gerätenamen und weitere Informationen extrahieren
                device_name = f"USB Device {i+1}"
                manufacturer = "Unknown"
                usb_version = "USB 2.0/3.0"
                serial_number = ""
                speed = ""
                
                # Versuche, alle Geräteinformationen zu finden
                for j, line in enumerate(lines):
                    if line.strip().startswith("Product ID:") and line.strip().endswith(product_id):
                        # Schaue nach oben nach dem Gerätenamen (nur 1-5 Zeilen)
                        for k in range(j-1, max(0, j-6), -1):
                            potential_line = lines[k].strip()
                            if potential_line and not potential_line.startswith(("Product ID:", "Vendor ID:", "Version:", "Speed:", "Manufacturer:", "Location ID:", "PCI Vendor ID:", "PCI Device ID:", "PCI Revision ID:", "Current Available", "Current Required", "Extra Operating", "Serial Number:")):
                                # Prüfe, ob es ein Gerätename ist (endet mit ":")
                                if ":" in potential_line and potential_line.endswith(":"):
                                    candidate_name = potential_line.rstrip(":")
                                    # Erlaube auch "Controller" für Bluetooth-Geräte, aber filtere Hubs
                                    if not any(skip in candidate_name.lower() for skip in ["hub", "host", "bus", "built-in"]):
                                        device_name = candidate_name
                                        break
                        
                        # Schaue nach unten nach weiteren Informationen (5-15 Zeilen für erweiterte Infos)
                        max_power = ""
                        current_required = ""
                        current_available = ""
                        transfer_speed = ""
                        max_transfer_speed = ""
                        device_class = ""
                        
                        for k in range(j+1, min(len(lines), j+15)):
                            line_content = lines[k].strip()
                            if line_content.startswith("Manufacturer:"):
                                manufacturer = line_content.split(":", 1)[1].strip()
                            elif line_content.startswith("Version:"):
                                usb_version = line_content.split(":", 1)[1].strip()
                            elif line_content.startswith("Serial Number:"):
                                serial_number = line_content.split(":", 1)[1].strip()
                            elif line_content.startswith("Speed:"):
                                speed = line_content.split(":", 1)[1].strip()
                                transfer_speed = speed
                                max_transfer_speed = speed
                                # USB-Version aus Speed ableiten
                                if "5 Gb/s" in speed or "10 Gb/s" in speed:
                                    usb_version = f"USB 3.x ({speed})"
                                elif "480 Mb/s" in speed:
                                    usb_version = f"USB 2.0 ({speed})"
                                elif "12 Mb/s" in speed or "1.5 Mb/s" in speed:
                                    usb_version = f"USB 1.x ({speed})"
                                else:
                                    usb_version = f"USB ({speed})"
                            elif line_content.startswith("Current Available:"):
                                current_available = line_content.split(":", 1)[1].strip()
                            elif line_content.startswith("Current Required:"):
                                current_required = line_content.split(":", 1)[1].strip()
                            elif line_content.startswith("Extra Operating Current:"):
                                max_power = line_content.split(":", 1)[1].strip()
                            elif line_content.startswith("Device Class:"):
                                device_class = line_content.split(":", 1)[1].strip()
                        break
                
                # Gerätetyp aus Namen ableiten
                device_type = "USB Device"
                if "keyboard" in device_name.lower():
                    device_type = "Keyboard"
                elif "mouse" in device_name.lower():
                    device_type = "Mouse"
                elif "audio" in device_name.lower() or "codec" in device_name.lower():
                    device_type = "Audio Device"
                elif "card reader" in device_name.lower():
                    device_type = "Storage"
                elif "serial" in device_name.lower():
                    device_type = "Serial Device"
                elif "bluetooth" in device_name.lower():
                    device_type = "Bluetooth Device"
                elif "controller" in device_name.lower():
                    device_type = "Controller"
                elif "lighting" in device_name.lower() or "rgb" in device_name.lower():
                    device_type = "Lighting Control"
                elif "composite" in device_name.lower():
                    device_type = "Composite Device"
                
                # Stromverbrauch berechnen
                power_consumption = ""
                if current_required and current_available:
                    try:
                        required_ma = int(current_required.replace(" mA", ""))
                        available_ma = int(current_available.replace(" mA", ""))
                        power_consumption = f"{required_ma} mA / {available_ma} mA"
                    except:
                        power_consumption = f"{current_required} / {current_available}"
                elif current_required:
                    power_consumption = current_required
                
                device = {
                    "name": device_name,
                    "description": device_name,
                    "device_id": f"{vendor_id}_{product_id}",
                    "manufacturer": manufacturer,
                    "status": "OK",
                    "is_connected": True,
                    "device_type": device_type,
                    "usb_version": usb_version,
                    "product_id": product_id,
                    "vendor_id": vendor_id,
                    "serial_number": serial_number,
                    "driver": "macOS",
                    # Erweiterte Informationen
                    "power_consumption": power_consumption,
                    "max_power": max_power,
                    "current_required": current_required,
                    "current_available": current_available,
                    "transfer_speed": transfer_speed,
                    "max_transfer_speed": max_transfer_speed,
                    "device_class": device_class,
                    "device_subclass": "",
                    "device_protocol": ""
                }
                devices.append(device)
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
            
        return devices
    
    @staticmethod
    def _get_linux_usb_devices() -> List[Dict[str, Any]]:
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
                    devices.append(device_info)
                    
        except FileNotFoundError:
            pass
            
        return devices
    
    @staticmethod
    def _get_windows_usb_devices_registry() -> List[Dict[str, Any]]:
        """Ermittelt USB-Geräte über die Windows-Registry."""
        devices = []
        
        try:
            import winreg
            debug_info("🔍 Durchsuche Windows Registry nach USB-Geräten...")
            
            # USB-Geräte aus verschiedenen Registry-Pfaden
            registry_paths = [
                r"SYSTEM\CurrentControlSet\Enum\USB",
                r"SYSTEM\CurrentControlSet\Enum\USBSTOR", 
                r"SYSTEM\CurrentControlSet\Enum\HID"
            ]
            
            for registry_path in registry_paths:
                try:
                    debug_info(f"🔍 Durchsuche {registry_path}...")
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
                    
                    # Alle USB-Geräte-Schlüssel auflisten
                    i = 0
                    while True:
                        try:
                            device_key_name = winreg.EnumKey(key, i)
                            debug_info(f"🔍 Gefunden: {device_key_name}")
                            
                            # Device-Subkeys durchgehen
                            device_key = winreg.OpenKey(key, device_key_name)
                            j = 0
                            while True:
                                try:
                                    instance_key_name = winreg.EnumKey(device_key, j)
                                    instance_key = winreg.OpenKey(device_key, instance_key_name)
                                    
                                    try:
                                        # Geräteinformationen abrufen
                                        device_desc = ""
                                        friendly_name = ""
                                        manufacturer = ""
                                        
                                        try:
                                            device_desc = winreg.QueryValueEx(instance_key, "DeviceDesc")[0]
                                            if ";" in device_desc:
                                                device_desc = device_desc.split(";")[-1]
                                        except:
                                            pass
                                            
                                        try:
                                            friendly_name = winreg.QueryValueEx(instance_key, "FriendlyName")[0]
                                        except:
                                            pass
                                            
                                        try:
                                            manufacturer = winreg.QueryValueEx(instance_key, "Mfg")[0]
                                            if ";" in manufacturer:
                                                manufacturer = manufacturer.split(";")[-1]
                                        except:
                                            pass
                                        
                                        # Gerätename bestimmen
                                        device_name = friendly_name or device_desc or f"USB-Gerät ({device_key_name})"
                                        
                                        # VID/PID aus Schlüsselname extrahieren
                                        vendor_id = ""
                                        product_id = ""
                                        if "VID_" in device_key_name and "PID_" in device_key_name:
                                            vid_match = re.search(r"VID_([A-F0-9]{4})", device_key_name)
                                            pid_match = re.search(r"PID_([A-F0-9]{4})", device_key_name)
                                            if vid_match:
                                                vendor_id = vid_match.group(1)
                                            if pid_match:
                                                product_id = pid_match.group(1)
                                        
                                        # Gerätetyp bestimmen
                                        device_type = PlatformUtils._determine_device_type(device_name, registry_path)
                                        
                                        # USB-Geschwindigkeit und erweiterte Informationen ermitteln
                                        usb_info = PlatformUtils._get_enhanced_usb_info(device_key_name, vendor_id, product_id, instance_key)
                                        
                                        device_info = {
                                            "name": device_name,
                                            "description": device_desc,
                                            "device_id": f"{device_key_name}\\{instance_key_name}",
                                            "manufacturer": usb_info.get("manufacturer", manufacturer),
                                            "status": "OK",
                                            "is_connected": True,
                                            "device_type": device_type,
                                            "usb_version": usb_info.get("usb_version", "USB 2.0"),
                                            "product_id": product_id,
                                            "vendor_id": vendor_id,
                                            "serial_number": instance_key_name,
                                            "driver": device_name,
                                            "power_consumption": usb_info.get("power_consumption", "Standard"),
                                            "max_power": usb_info.get("max_power", "500 mA"),
                                            "current_required": usb_info.get("current_required", "Unknown"),
                                            "current_available": usb_info.get("current_available", "500 mA"),
                                            "transfer_speed": usb_info.get("transfer_speed", "Unknown"),
                                            "max_transfer_speed": usb_info.get("max_transfer_speed", "480 Mb/s"),
                                            "device_class": usb_info.get("device_class", "Unknown"),
                                            "device_subclass": usb_info.get("device_subclass", ""),
                                            "device_protocol": usb_info.get("device_protocol", "")
                                        }
                                        
                                        devices.append(device_info)
                                        debug_info(f"✅ Registry-USB-Gerät gefunden: {device_name}")
                                        
                                    finally:
                                        winreg.CloseKey(instance_key)
                                    
                                    j += 1
                                except WindowsError:
                                    break
                            
                            winreg.CloseKey(device_key)
                            i += 1
                        except WindowsError:
                            break
                    
                    winreg.CloseKey(key)
                    
                except Exception as e:
                    print(f"   ⚠️ Fehler bei Registry-Pfad {registry_path}: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ❌ Registry-Zugriff fehlgeschlagen: {e}")
        
        print(f"   📊 {len(devices)} Geräte aus Registry gefunden")
        return devices
    
    @staticmethod
    def _get_windows_usb_devices_com_ports() -> List[Dict[str, Any]]:
        """Ermittelt USB-Geräte über COM-Ports."""
        devices = []
        
        try:
            import serial.tools.list_ports
            debug_info("🔍 Durchsuche COM-Ports nach USB-Geräten...")
            
            ports = serial.tools.list_ports.comports()
            
            for port_info in ports:
                # Nur USB-basierte COM-Ports
                if port_info.vid is not None and port_info.pid is not None:
                    device_name = f"{port_info.description} ({port_info.device})"
                    
                    device_info = {
                        "name": device_name,
                        "description": port_info.description or "",
                        "device_id": f"USB\\VID_{port_info.vid:04X}&PID_{port_info.pid:04X}\\{port_info.serial_number or 'Unknown'}",
                        "manufacturer": port_info.manufacturer or "",
                        "status": "OK",
                        "is_connected": True,
                        "device_type": "USB Serial Device",
                        "usb_version": "USB 2.0",
                        "product_id": f"{port_info.pid:04X}",
                        "vendor_id": f"{port_info.vid:04X}",
                        "serial_number": port_info.serial_number or "",
                        "driver": port_info.description or "",
                        "power_consumption": "Standard",
                        "max_power": "500 mA",
                        "current_required": "Unknown",
                        "current_available": "500 mA",
                        "transfer_speed": "Unknown",
                        "max_transfer_speed": "480 Mb/s",
                        "device_class": "Communication Device",
                        "device_subclass": "Serial",
                        "device_protocol": "USB"
                    }
                    
                    devices.append(device_info)
                    debug_info(f"✅ USB-COM-Port gefunden: {device_name}")
                    
        except Exception as e:
            debug_error(f"❌ COM-Port-Zugriff fehlgeschlagen: {e}")
        
        debug_info(f"📊 {len(devices)} USB-COM-Ports gefunden")
        return devices
    
    @staticmethod
    def _determine_device_type(device_name: str, registry_path: str = "") -> str:
        """Bestimmt den Gerätetyp basierend auf Name und Registry-Pfad."""
        device_name_lower = device_name.lower()
        
        # Spezifische Gerätetypen
        if "keyboard" in device_name_lower or "tastatur" in device_name_lower:
            return "Keyboard"
        elif "mouse" in device_name_lower or "maus" in device_name_lower:
            return "Mouse"
        elif "audio" in device_name_lower or "sound" in device_name_lower or "speaker" in device_name_lower or "microphone" in device_name_lower:
            return "Audio Device"
        elif "storage" in device_name_lower or "disk" in device_name_lower or "drive" in device_name_lower or "ssd" in device_name_lower or "hdd" in device_name_lower:
            return "Storage"
        elif "hub" in device_name_lower:
            return "USB Hub"
        elif "camera" in device_name_lower or "webcam" in device_name_lower:
            return "Camera"
        elif "bluetooth" in device_name_lower:
            return "Bluetooth Adapter"
        elif "wifi" in device_name_lower or "wireless" in device_name_lower or "wlan" in device_name_lower:
            return "Wireless Adapter"
        elif "printer" in device_name_lower:
            return "Printer"
        elif "scanner" in device_name_lower:
            return "Scanner"
        elif "gamepad" in device_name_lower or "controller" in device_name_lower or "joystick" in device_name_lower:
            return "Game Controller"
        elif "serial" in device_name_lower or "com" in device_name_lower:
            return "Serial Device"
        elif "hid" in registry_path.lower():
            return "HID Device"
        elif "composite" in device_name_lower:
            return "Composite Device"
        else:
            return "USB Device"
    
    @staticmethod
    def _get_enhanced_usb_info(device_key: str, vendor_id: str, product_id: str, registry_key=None) -> Dict[str, str]:
        """Ermittelt erweiterte USB-Informationen."""
        info = {}
        
        try:
            import winreg
            
            # Zuerst versuchen, USB-Version aus Registry zu lesen
            usb_version_detected = False
            
            if registry_key:
                try:
                    # Versuche verschiedene Registry-Werte zu lesen
                    registry_values_to_check = [
                        "DeviceDesc",
                        "FriendlyName", 
                        "Service",
                        "Class",
                        "ConfigFlags"
                    ]
                    
                    for value_name in registry_values_to_check:
                        try:
                            value_data = winreg.QueryValueEx(registry_key, value_name)[0]
                            if isinstance(value_data, str):
                                value_upper = value_data.upper()
                                
                                # USB 3.0/3.1 Indikatoren
                                if any(indicator in value_upper for indicator in [
                                    "USB 3.0", "USB3.0", "USB30", "SUPERSPEED", "XHCI", 
                                    "USB 3.1", "USB31", "SUPERSPEED+"
                                ]):
                                    if "USB 3.1" in value_upper or "USB31" in value_upper:
                                        info["usb_version"] = "USB 3.1"
                                        info["max_transfer_speed"] = "10 Gb/s"
                                        info["transfer_speed"] = "SuperSpeed+"
                                    else:
                                        info["usb_version"] = "USB 3.0"
                                        info["max_transfer_speed"] = "5 Gb/s"
                                        info["transfer_speed"] = "SuperSpeed"
                                    usb_version_detected = True
                                    debug_info(f"USB 3.x erkannt über Registry-Wert {value_name}: {value_data}")
                                    break
                                
                                # USB 2.0 Indikatoren
                                elif any(indicator in value_upper for indicator in [
                                    "USB 2.0", "USB20", "HIGH SPEED", "EHCI"
                                ]):
                                    info["usb_version"] = "USB 2.0"
                                    info["max_transfer_speed"] = "480 Mb/s"
                                    info["transfer_speed"] = "High Speed"
                                    usb_version_detected = True
                                    debug_info(f"USB 2.0 erkannt über Registry-Wert {value_name}: {value_data}")
                                    break
                        except:
                            continue
                    
                    # Zusätzlich: Parent-Key prüfen für Controller-Informationen
                    if not usb_version_detected:
                        try:
                            # Prüfe auf XHCI (USB 3.0) oder EHCI (USB 2.0) Controller
                            parent_path = registry_key.name.rsplit('\\', 2)[0]  # Gehe zwei Ebenen hoch
                            parent_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, parent_path.replace("HKEY_LOCAL_MACHINE\\", ""))
                            
                            # Durchsuche alle Subkeys nach Controller-Informationen
                            i = 0
                            while True:
                                try:
                                    subkey_name = winreg.EnumKey(parent_key, i)
                                    if any(controller in subkey_name.upper() for controller in ["XHCI", "USB30"]):
                                        info["usb_version"] = "USB 3.0"
                                        info["max_transfer_speed"] = "5 Gb/s"
                                        info["transfer_speed"] = "SuperSpeed"
                                        usb_version_detected = True
                                        debug_info(f"USB 3.0 erkannt über Controller: {subkey_name}")
                                        break
                                    elif any(controller in subkey_name.upper() for controller in ["EHCI", "USB20"]):
                                        info["usb_version"] = "USB 2.0"
                                        info["max_transfer_speed"] = "480 Mb/s"
                                        info["transfer_speed"] = "High Speed"
                                        usb_version_detected = True
                                        debug_info(f"USB 2.0 erkannt über Controller: {subkey_name}")
                                        break
                                    i += 1
                                except WindowsError:
                                    break
                            
                            winreg.CloseKey(parent_key)
                        except:
                            pass
                            
                except Exception as e:
                    debug_warning(f"Fehler beim Lesen der Registry-Werte: {e}")
            
            # Fallback: Device-Key-basierte Erkennung
            if not usb_version_detected:
                device_key_upper = device_key.upper()
                
                if any(indicator in device_key_upper for indicator in ["USB30", "XHCI", "USB3"]):
                    info["usb_version"] = "USB 3.0"
                    info["max_transfer_speed"] = "5 Gb/s"
                    info["transfer_speed"] = "SuperSpeed"
                    debug_info(f"USB 3.0 erkannt über Device-Key: {device_key}")
                elif any(indicator in device_key_upper for indicator in ["USB20", "EHCI"]):
                    info["usb_version"] = "USB 2.0"
                    info["max_transfer_speed"] = "480 Mb/s"
                    info["transfer_speed"] = "High Speed"
                    debug_info(f"USB 2.0 erkannt über Device-Key: {device_key}")
                elif any(indicator in device_key_upper for indicator in ["USB11", "UHCI", "OHCI"]):
                    info["usb_version"] = "USB 1.1"
                    info["max_transfer_speed"] = "12 Mb/s"
                    info["transfer_speed"] = "Full Speed"
                    debug_info(f"USB 1.1 erkannt über Device-Key: {device_key}")
                else:
                    # Intelligente Standard-Annahme: Moderne Systeme haben meist USB 3.0
                    info["usb_version"] = "USB 2.0"
                    info["max_transfer_speed"] = "480 Mb/s"
                    info["transfer_speed"] = "High Speed"
                    debug_info(f"USB-Version nicht eindeutig erkennbar, verwende USB 2.0 als Standard")
            
            # Hersteller basierend auf Vendor ID ermitteln
            manufacturer = PlatformUtils._get_manufacturer_by_vid(vendor_id)
            if manufacturer:
                info["manufacturer"] = manufacturer
            
            # Stromverbrauch basierend auf USB-Version schätzen
            if info["usb_version"] in ["USB 3.0", "USB 3.1"]:
                info["max_power"] = "900 mA"
                info["current_available"] = "900 mA"
                info["power_consumption"] = "High Performance"
            elif info["usb_version"] == "USB 2.0":
                info["max_power"] = "500 mA"
                info["current_available"] = "500 mA"
                info["power_consumption"] = "Standard"
            else:
                info["max_power"] = "100 mA"
                info["current_available"] = "100 mA"
                info["power_consumption"] = "Low Power"
            
            # Device-Klasse basierend auf Vendor/Product ID
            device_class = PlatformUtils._get_device_class_by_ids(vendor_id, product_id)
            if device_class:
                info["device_class"] = device_class
            
        except Exception as e:
            debug_error(f"Fehler bei erweiterten USB-Informationen: {e}")
            # Minimal-Fallback
            info = {
                "usb_version": "USB 2.0",
                "max_transfer_speed": "480 Mb/s",
                "transfer_speed": "High Speed",
                "max_power": "500 mA",
                "current_available": "500 mA",
                "power_consumption": "Standard"
            }
        
        return info
    
    @staticmethod
    def _get_manufacturer_by_vid(vendor_id: str) -> Optional[str]:
        """Ermittelt den Hersteller basierend auf der Vendor ID."""
        # Bekannte Vendor IDs
        vendor_map = {
            "046D": "Logitech",
            "045E": "Microsoft",
            "05AC": "Apple",
            "1D6B": "Linux Foundation",
            "8087": "Intel",
            "0BDA": "Realtek",
            "0424": "Microchip Technology",
            "1A86": "QinHeng Electronics",
            "10C4": "Silicon Labs",
            "0403": "Future Technology Devices International",
            "067B": "Prolific Technology",
            "2341": "Arduino SA",
            "16C0": "Van Ooijen Technische Informatica",
            "0781": "SanDisk",
            "090C": "Silicon Motion",
            "13FE": "Kingston Technology",
            "0951": "Kingston Technology",
            "058F": "Alcor Micro",
            "0930": "Toshiba",
            "04E8": "Samsung Electronics",
            "18A5": "Verbatim",
            "1058": "Western Digital",
            "0BC2": "Seagate",
            "152D": "JMicron Technology",
            "174C": "ASMedia Technology",
            "2109": "VIA Labs",
            "1B1C": "Corsair",
            "046A": "Cherry",
            "04D9": "Holtek Semiconductor",
            "1C4F": "SiGma Micro",
            "0A5C": "Broadcom",
            "8086": "Intel Corporation",
            "1002": "AMD",
            "10DE": "NVIDIA Corporation",
            "0E8D": "MediaTek",
            "2717": "Xiaomi",
            "12D1": "Huawei Technologies",
            "04E6": "SCM Microsystems",
            "0483": "STMicroelectronics"
        }
        
        return vendor_map.get(vendor_id.upper())
    
    @staticmethod
    def _get_device_class_by_ids(vendor_id: str, product_id: str) -> Optional[str]:
        """Ermittelt die Device-Klasse basierend auf Vendor/Product ID."""
        # Bekannte Device-Klassen basierend auf VID/PID
        vid = vendor_id.upper()
        pid = product_id.upper()
        
        # Logitech Geräte
        if vid == "046D":
            if pid in ["C52B", "C534", "C077"]:  # Unifying Receiver, etc.
                return "Human Interface Device"
            elif pid in ["0825", "082D"]:  # Webcams
                return "Video Device"
            elif pid in ["C31C", "C332"]:  # Keyboards
                return "Keyboard"
            elif pid in ["C05A", "C069"]:  # Mice
                return "Mouse"
        
        # Microsoft Geräte
        elif vid == "045E":
            if pid in ["0040", "00DB"]:  # Mice
                return "Mouse"
            elif pid in ["0750", "028E"]:  # Xbox Controller
                return "Game Controller"
        
        # Apple Geräte
        elif vid == "05AC":
            if pid in ["0250", "0252"]:  # Keyboards
                return "Keyboard"
            elif pid in ["030D", "030E"]:  # Mice
                return "Mouse"
        
        # Intel
        elif vid == "8087":
            return "Wireless Controller"
        
        # Default
        return "Communication Device"
    
    @staticmethod
    def _get_usb_controller_info() -> Dict[str, str]:
        """Sammelt Informationen über USB-Controller im System."""
        controller_info = {
            "usb3_controllers": [],
            "usb2_controllers": [],
            "usb1_controllers": []
        }
        
        try:
            import winreg
            
            # USB-Controller in verschiedenen Registry-Pfaden suchen
            controller_paths = [
                r"SYSTEM\CurrentControlSet\Services\xhci",  # USB 3.0
                r"SYSTEM\CurrentControlSet\Services\usbxhci",  # USB 3.0
                r"SYSTEM\CurrentControlSet\Services\ehci",  # USB 2.0
                r"SYSTEM\CurrentControlSet\Services\usbehci",  # USB 2.0
                r"SYSTEM\CurrentControlSet\Services\uhci",  # USB 1.1
                r"SYSTEM\CurrentControlSet\Services\ohci",  # USB 1.1
            ]
            
            for path in controller_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                    
                    # Service-Name lesen
                    try:
                        service_name = winreg.QueryValueEx(key, "DisplayName")[0]
                    except:
                        service_name = path.split("\\")[-1]
                    
                    # Controller-Typ bestimmen
                    service_upper = service_name.upper()
                    path_upper = path.upper()
                    
                    if any(indicator in service_upper or indicator in path_upper for indicator in ["XHCI", "USB3", "SUPERSPEED"]):
                        controller_info["usb3_controllers"].append(service_name)
                        debug_info(f"USB 3.0 Controller gefunden: {service_name}")
                    elif any(indicator in service_upper or indicator in path_upper for indicator in ["EHCI", "USB2", "HIGH"]):
                        controller_info["usb2_controllers"].append(service_name)
                        debug_info(f"USB 2.0 Controller gefunden: {service_name}")
                    elif any(indicator in service_upper or indicator in path_upper for indicator in ["UHCI", "OHCI", "USB1"]):
                        controller_info["usb1_controllers"].append(service_name)
                        debug_info(f"USB 1.x Controller gefunden: {service_name}")
                    
                    winreg.CloseKey(key)
                except:
                    continue
                    
        except Exception as e:
            debug_warning(f"Fehler beim Sammeln der Controller-Informationen: {e}")
        
        return controller_info
    
    @staticmethod
    def _correct_usb_version_by_controller(device: Dict[str, Any], controller_info: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Korrigiert die USB-Version basierend auf verfügbaren Controllern."""
        corrections = {}
        
        try:
            device_name = device.get("name", "").upper()
            device_desc = device.get("description", "").upper()
            device_type = device.get("device_type", "")
            
            # Spezielle Behandlung für USB-Hubs
            if "HUB" in device_name or "HUB" in device_desc:
                # Wenn USB 3.0 Controller verfügbar sind und es ein Hub ist
                if controller_info.get("usb3_controllers"):
                    # Prüfe auf spezifische USB 3.0 Indikatoren
                    if any(indicator in device_name or indicator in device_desc for indicator in [
                        "USB 3.0", "USB3.0", "SUPERSPEED", "ROOT HUB", "XHCI"
                    ]):
                        corrections["usb_version"] = "USB 3.0"
                        corrections["max_transfer_speed"] = "5 Gb/s"
                        corrections["transfer_speed"] = "SuperSpeed"
                        corrections["max_power"] = "900 mA"
                        corrections["current_available"] = "900 mA"
                        corrections["power_consumption"] = "High Performance"
                        debug_info(f"USB-Version für Hub korrigiert: {device_name} -> USB 3.0")
            
            # Spezielle Behandlung für bekannte USB 3.0 Geräte
            elif any(indicator in device_name or indicator in device_desc for indicator in [
                "SUPERSPEED", "USB 3.", "USB3", "5 GB/S", "5GB/S"
            ]):
                if controller_info.get("usb3_controllers"):
                    corrections["usb_version"] = "USB 3.0"
                    corrections["max_transfer_speed"] = "5 Gb/s"
                    corrections["transfer_speed"] = "SuperSpeed"
                    corrections["max_power"] = "900 mA"
                    corrections["current_available"] = "900 mA"
                    corrections["power_consumption"] = "High Performance"
                    debug_info(f"USB-Version korrigiert: {device_name} -> USB 3.0")
            
        except Exception as e:
            debug_error(f"Fehler bei USB-Versions-Korrektur: {e}")
        
        return corrections if corrections else None
