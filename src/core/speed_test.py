"""
USB-Geschwindigkeitstest für USB-Monitor.
Testet die tatsächliche Übertragungsgeschwindigkeit von USB-Storage-Geräten.
"""

import os
import time
import tempfile
import threading
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import logging


@dataclass
class SpeedTestResult:
    """Ergebnis eines USB-Geschwindigkeitstests."""
    
    device_path: str
    device_name: str
    test_file_size_mb: float
    write_speed_mbps: float
    read_speed_mbps: float
    average_speed_mbps: float
    test_duration_seconds: float
    success: bool
    error_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Ergebnis in ein Dictionary."""
        return {
            "device_path": self.device_path,
            "device_name": self.device_name,
            "test_file_size_mb": self.test_file_size_mb,
            "write_speed_mbps": self.write_speed_mbps,
            "read_speed_mbps": self.read_speed_mbps,
            "average_speed_mbps": self.average_speed_mbps,
            "test_duration_seconds": self.test_duration_seconds,
            "success": self.success,
            "error_message": self.error_message
        }


class USBSpeedTester:
    """USB-Geschwindigkeitstester für Storage-Geräte."""
    
    def __init__(self):
        """Initialisiert den Speed-Tester."""
        self.logger = logging.getLogger(__name__)
        self.is_testing = False
        self.current_test_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.on_test_started: Optional[Callable[[str], None]] = None
        self.on_test_progress: Optional[Callable[[str, float], None]] = None
        self.on_test_completed: Optional[Callable[[SpeedTestResult], None]] = None
        
    def get_testable_devices(self) -> Dict[str, str]:
        """Ermittelt alle testbaren USB-Storage-Geräte."""
        devices = {}
        
        try:
            from utils.platform_utils import PlatformUtils
            
            if PlatformUtils.is_macos():
                devices = self._get_macos_storage_devices()
            elif PlatformUtils.is_windows():
                devices = self._get_windows_storage_devices()
            elif PlatformUtils.is_linux():
                devices = self._get_linux_storage_devices()
                
        except Exception as e:
            self.logger.error(f"Fehler beim Ermitteln der testbaren Geräte: {e}")
            
        return devices
    
    def _get_macos_storage_devices(self) -> Dict[str, str]:
        """Ermittelt macOS USB-Storage-Geräte."""
        devices = {}
        
        try:
            # Alle gemounteten Volumes durchsuchen
            volumes_path = Path("/Volumes")
            if volumes_path.exists():
                for volume in volumes_path.iterdir():
                    if volume.is_dir() and not volume.name.startswith('.'):
                        # Prüfen ob es ein USB-Device ist
                        if self._is_usb_volume_macos(str(volume)):
                            devices[str(volume)] = volume.name
                            
        except Exception as e:
            self.logger.error(f"Fehler beim Ermitteln der macOS Storage-Geräte: {e}")
            
        return devices
    
    def _is_usb_volume_macos(self, volume_path: str) -> bool:
        """Prüft, ob ein Volume ein USB-Device ist (macOS)."""
        try:
            import subprocess
            result = subprocess.run(
                ["diskutil", "info", volume_path],
                capture_output=True, text=True, check=True
            )
            
            # Nach USB-spezifischen Informationen suchen
            output = result.stdout.lower()
            return any(keyword in output for keyword in [
                "usb", "external", "removable"
            ])
            
        except:
            return False
    
    def _get_windows_storage_devices(self) -> Dict[str, str]:
        """Ermittelt Windows USB-Storage-Geräte."""
        devices = {}
        
        try:
            import wmi
            c = wmi.WMI()
            
            # USB-Storage-Geräte abrufen
            for disk in c.Win32_LogicalDisk():
                if disk.DriveType == 2:  # Removable disk
                    drive_letter = disk.DeviceID
                    if drive_letter and os.path.exists(drive_letter):
                        devices[drive_letter] = f"USB Drive ({drive_letter})"
                        
        except ImportError:
            # Fallback: Alle verfügbaren Laufwerke prüfen
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        # Prüfen ob es ein Wechseldatenträger ist
                        import win32file
                        drive_type = win32file.GetDriveType(drive)
                        if drive_type == win32file.DRIVE_REMOVABLE:
                            devices[drive] = f"USB Drive ({letter}:)"
                    except:
                        pass
                        
        except Exception as e:
            self.logger.error(f"Fehler beim Ermitteln der Windows Storage-Geräte: {e}")
            
        return devices
    
    def _get_linux_storage_devices(self) -> Dict[str, str]:
        """Ermittelt Linux USB-Storage-Geräte."""
        devices = {}
        
        try:
            # /media und /mnt durchsuchen
            for mount_point in ["/media", "/mnt"]:
                mount_path = Path(mount_point)
                if mount_path.exists():
                    for user_dir in mount_path.iterdir():
                        if user_dir.is_dir():
                            for device in user_dir.iterdir():
                                if device.is_dir() and self._is_usb_device_linux(str(device)):
                                    devices[str(device)] = device.name
                                    
        except Exception as e:
            self.logger.error(f"Fehler beim Ermitteln der Linux Storage-Geräte: {e}")
            
        return devices
    
    def _is_usb_device_linux(self, device_path: str) -> bool:
        """Prüft, ob ein Device ein USB-Device ist (Linux)."""
        try:
            import subprocess
            result = subprocess.run(
                ["findmnt", "-n", "-o", "SOURCE", device_path],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                source = result.stdout.strip()
                # Prüfen ob es ein USB-Device ist
                return "/dev/sd" in source or "/dev/usb" in source
                
        except:
            pass
            
        return False
    
    def start_speed_test(self, device_path: str, device_name: str, 
                        test_size_mb: float = 100.0) -> None:
        """Startet einen Geschwindigkeitstest."""
        if self.is_testing:
            self.logger.warning("Ein Test läuft bereits")
            return
            
        self.is_testing = True
        self.current_test_thread = threading.Thread(
            target=self._run_speed_test,
            args=(device_path, device_name, test_size_mb),
            daemon=True
        )
        self.current_test_thread.start()
    
    def stop_speed_test(self) -> None:
        """Stoppt den aktuellen Geschwindigkeitstest."""
        self.is_testing = False
        if self.current_test_thread and self.current_test_thread.is_alive():
            self.current_test_thread.join(timeout=2.0)
    
    def _run_speed_test(self, device_path: str, device_name: str, test_size_mb: float) -> None:
        """Führt den eigentlichen Geschwindigkeitstest durch."""
        start_time = time.time()
        
        try:
            if self.on_test_started:
                self.on_test_started(device_name)
            
            # Testdatei erstellen
            test_data = self._generate_test_data(test_size_mb)
            test_file_path = os.path.join(device_path, "usb_speed_test.tmp")
            
            # Write-Test
            if self.on_test_progress:
                self.on_test_progress(device_name, 25.0)
                
            write_start = time.time()
            self._write_test_file(test_file_path, test_data)
            write_time = time.time() - write_start
            
            if not self.is_testing:
                return
            
            # Read-Test
            if self.on_test_progress:
                self.on_test_progress(device_name, 75.0)
                
            read_start = time.time()
            self._read_test_file(test_file_path)
            read_time = time.time() - read_start
            
            # Testdatei löschen
            try:
                os.remove(test_file_path)
            except:
                pass
            
            if not self.is_testing:
                return
            
            # Geschwindigkeiten berechnen
            write_speed_mbps = (test_size_mb / write_time) if write_time > 0 else 0
            read_speed_mbps = (test_size_mb / read_time) if read_time > 0 else 0
            average_speed_mbps = (write_speed_mbps + read_speed_mbps) / 2
            
            total_time = time.time() - start_time
            
            result = SpeedTestResult(
                device_path=device_path,
                device_name=device_name,
                test_file_size_mb=test_size_mb,
                write_speed_mbps=write_speed_mbps,
                read_speed_mbps=read_speed_mbps,
                average_speed_mbps=average_speed_mbps,
                test_duration_seconds=total_time,
                success=True
            )
            
            if self.on_test_progress:
                self.on_test_progress(device_name, 100.0)
                
            if self.on_test_completed:
                self.on_test_completed(result)
                
        except Exception as e:
            error_msg = f"Fehler beim Geschwindigkeitstest: {e}"
            self.logger.error(error_msg)
            
            result = SpeedTestResult(
                device_path=device_path,
                device_name=device_name,
                test_file_size_mb=test_size_mb,
                write_speed_mbps=0,
                read_speed_mbps=0,
                average_speed_mbps=0,
                test_duration_seconds=time.time() - start_time,
                success=False,
                error_message=error_msg
            )
            
            if self.on_test_completed:
                self.on_test_completed(result)
                
        finally:
            self.is_testing = False
    
    def _generate_test_data(self, size_mb: float) -> bytes:
        """Generiert Testdaten der angegebenen Größe."""
        size_bytes = int(size_mb * 1024 * 1024)
        # Pseudo-zufällige Daten generieren für realistischen Test
        return os.urandom(min(size_bytes, 1024 * 1024)) * (size_bytes // (1024 * 1024) + 1)[:size_bytes]
    
    def _write_test_file(self, file_path: str, data: bytes) -> None:
        """Schreibt die Testdatei und misst die Geschwindigkeit."""
        with open(file_path, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())  # Sicherstellen, dass alles geschrieben wurde
    
    def _read_test_file(self, file_path: str) -> bytes:
        """Liest die Testdatei und misst die Geschwindigkeit."""
        with open(file_path, 'rb') as f:
            return f.read()
    
    def get_usb_speed_rating(self, speed_mbps: float) -> str:
        """Gibt eine Bewertung der USB-Geschwindigkeit zurück."""
        if speed_mbps >= 400:
            return "🚀 Excellent (USB 3.0+)"
        elif speed_mbps >= 200:
            return "⚡ Very Good (USB 3.0)"
        elif speed_mbps >= 60:
            return "✅ Good (USB 2.0 High-Speed)"
        elif speed_mbps >= 10:
            return "⚠️ Moderate (USB 2.0)"
        elif speed_mbps >= 1:
            return "🐌 Slow (USB 1.1)"
        else:
            return "❌ Very Slow"
    
    def detect_cable_quality(self, theoretical_speed: str, actual_speed: float) -> str:
        """Erkennt die Kabelqualität basierend auf theoretischer vs. tatsächlicher Geschwindigkeit."""
        # Theoretische Geschwindigkeiten extrahieren
        theoretical_mbps = 0
        if "480 Mb/s" in theoretical_speed:
            theoretical_mbps = 60  # USB 2.0 theoretisch ~60 MB/s
        elif "5 Gb/s" in theoretical_speed:
            theoretical_mbps = 625  # USB 3.0 theoretisch ~625 MB/s
        elif "10 Gb/s" in theoretical_speed:
            theoretical_mbps = 1250  # USB 3.1 theoretisch ~1250 MB/s
        
        if theoretical_mbps == 0:
            return "❓ Unbekannt"
        
        efficiency = (actual_speed / theoretical_mbps) * 100
        
        if efficiency >= 80:
            return "🟢 Excellent Cable (>80% efficiency)"
        elif efficiency >= 60:
            return "🟡 Good Cable (60-80% efficiency)"
        elif efficiency >= 40:
            return "🟠 Moderate Cable (40-60% efficiency)"
        elif efficiency >= 20:
            return "🔴 Poor Cable (20-40% efficiency)"
        else:
            return "❌ Bad Cable (<20% efficiency)"
