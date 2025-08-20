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
                            "driver": dependent.Name or ""
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
            current_device = {}
            
            for line in lines:
                line = line.strip()
                
                if line.startswith("Product ID:"):
                    if current_device:
                        devices.append(current_device)
                    current_device = {"product_id": line.split(":", 1)[1].strip()}
                    
                elif line.startswith("Vendor ID:"):
                    current_device["vendor_id"] = line.split(":", 1)[1].strip()
                    
                elif line.startswith("Version:"):
                    current_device["version"] = line.split(":", 1)[1].strip()
                    
                elif line.startswith("Serial Number:"):
                    current_device["serial_number"] = line.split(":", 1)[1].strip()
                    
                elif line.startswith("Manufacturer:"):
                    current_device["manufacturer"] = line.split(":", 1)[1].strip()
                    
                elif line.startswith("Location ID:"):
                    current_device["location_id"] = line.split(":", 1)[1].strip()
                    
            # Letztes Gerät hinzufügen
            if current_device:
                devices.append(current_device)
                
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
