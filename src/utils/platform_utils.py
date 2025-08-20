"""
Plattform-spezifische Hilfsfunktionen für USB-Monitor.
"""

import platform
import sys
from typing import List, Dict, Any, Optional
import subprocess
import re


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
        
        try:
            import wmi
            c = wmi.WMI()
            
            # Alle USB-Geräte abrufen (nicht nur Hubs)
            for device in c.Win32_USBControllerDevice():
                try:
                    # Das angeschlossene Gerät abrufen
                    dependent = device.Dependent
                    if dependent:
                        device_info = {
                            "name": dependent.Name or "Unbekannt",
                            "description": dependent.Description or "",
                            "device_id": dependent.DeviceID or "",
                            "manufacturer": dependent.Manufacturer or "",
                            "status": dependent.Status or "OK",
                            "is_connected": True,
                            "device_type": "USB Device",
                            "usb_version": "USB 2.0/3.0",
                            "product_id": "",
                            "vendor_id": "",
                            "serial_number": "",
                            "driver": dependent.Name or "",
                            # Erweiterte Informationen (Windows-spezifisch)
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
                        
                        # Zusätzliche Informationen aus dem DeviceID extrahieren
                        if dependent.DeviceID:
                            # USB\VID_xxxx&PID_xxxx\SerialNumber
                            parts = dependent.DeviceID.split("\\")
                            if len(parts) >= 2:
                                vid_pid = parts[1]
                                if "VID_" in vid_pid and "PID_" in vid_pid:
                                    vid_match = re.search(r"VID_([A-F0-9]{4})", vid_pid)
                                    pid_match = re.search(r"PID_([A-F0-9]{4})", vid_pid)
                                    if vid_match:
                                        device_info["vendor_id"] = vid_match.group(1)
                                    if pid_match:
                                        device_info["product_id"] = pid_match.group(1)
                                
                                if len(parts) >= 3:
                                    device_info["serial_number"] = parts[2]
                        
                        devices.append(device_info)
                except Exception as e:
                    # Einzelne Geräte überspringen, wenn Fehler auftreten
                    continue
                    
        except ImportError:
            # Fallback: Registry abfragen
            try:
                import winreg
                # USB-Geräte aus der Registry abrufen
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SYSTEM\CurrentControlSet\Enum\USB")
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        
                        try:
                            # Gerätename und Beschreibung abrufen
                            device_name = winreg.QueryValueEx(subkey, "DeviceDesc")[0]
                            device_info = {
                                "name": device_name,
                                "description": device_name,
                                "device_id": subkey_name,
                                "manufacturer": "",
                                "status": "OK",
                                "is_connected": True,
                                "device_type": "USB Device",
                                "usb_version": "USB 2.0/3.0",
                                "product_id": "",
                                "vendor_id": "",
                                "serial_number": "",
                                "driver": ""
                            }
                            devices.append(device_info)
                        except:
                            pass
                        finally:
                            winreg.CloseKey(subkey)
                        i += 1
                    except WindowsError:
                        break
                winreg.CloseKey(key)
            except:
                pass
            
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
