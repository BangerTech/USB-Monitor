#!/usr/bin/env python3
"""
Cross-Platform Build Script für USB-Monitor
Erstellt sowohl Windows .exe als auch macOS .app Dateien
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    """Gibt einen formatierten Header aus."""
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()

def check_python():
    """Überprüft die Python-Installation."""
    print("Überprüfe Python-Installation...")
    
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 oder höher ist erforderlich!")
        print(f"   Aktuelle Version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} gefunden")
    return True

def check_pip():
    """Überprüft pip."""
    print("Überprüfe pip...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ pip verfügbar: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip ist nicht verfügbar!")
        return False

def install_dependencies():
    """Installiert die erforderlichen Abhängigkeiten."""
    print("Installiere Abhängigkeiten...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Abhängigkeiten erfolgreich installiert")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Installieren der Abhängigkeiten: {e}")
        return False

def build_for_platform(platform_name, icon_path=None):
    """Erstellt die ausführbare Datei für eine bestimmte Plattform."""
    print(f"Erstelle {platform_name}-Ausführbare Datei...")
    
    # PyInstaller-Befehl
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", f"USB-Monitor-{platform_name}",
        "--distpath", "dist",
        "--workpath", f"build-{platform_name}",
        "--specpath", f"build-{platform_name}",
        "src/main.py"
    ]
    
    # Icon hinzufügen, falls vorhanden
    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
        print(f"   Icon gefunden: {icon_path}")
    
    print(f"   Führe aus: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"✅ {platform_name}-Build erfolgreich abgeschlossen!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {platform_name}-Build fehlgeschlagen: {e}")
        return False

def create_macos_app_bundle():
    """Erstellt eine macOS .app-Bundle."""
    print("Erstelle macOS .app-Bundle...")
    
    app_name = "USB-Monitor.app"
    app_path = Path(app_name)
    
    # Bestehende .app löschen
    if app_path.exists():
        shutil.rmtree(app_path)
    
    # App-Struktur erstellen
    macos_path = app_path / "Contents" / "MacOS"
    resources_path = app_path / "Contents" / "Resources"
    
    macos_path.mkdir(parents=True, exist_ok=True)
    resources_path.mkdir(parents=True, exist_ok=True)
    
    # Executable kopieren
    executable_source = Path("dist") / "USB-Monitor-macOS"
    if executable_source.exists():
        shutil.copy2(executable_source, macos_path / "USB-Monitor")
        os.chmod(macos_path / "USB-Monitor", 0o755)
        print("   ✅ Executable kopiert")
        
        # Zusätzliche Berechtigungen setzen
        try:
            # Setze alle Berechtigungen (Owner, Group, Others)
            os.chmod(macos_path / "USB-Monitor", 0o755)
            # Setze auch die .app-Ordner-Berechtigungen
            os.chmod(app_path, 0o755)
            os.chmod(app_path / "Contents", 0o755)
            os.chmod(macos_path, 0o755)
            print("   ✅ Berechtigungen gesetzt")
        except Exception as e:
            print(f"   ⚠️  Warnung: Konnte nicht alle Berechtigungen setzen: {e}")
    else:
        print("   ❌ Executable nicht gefunden")
        return False
    
    # Icon kopieren
    icon_source = Path("assets/icons/app_icon.icns")
    if icon_source.exists():
        shutil.copy2(icon_source, resources_path / "app_icon.icns")
        print("   ✅ Icon kopiert")
    
    # Info.plist erstellen
    info_plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>USB-Monitor</string>
    <key>CFBundleIdentifier</key>
    <string>com.usbmonitor.app</string>
    <key>CFBundleName</key>
    <string>USB-Monitor</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleIconFile</key>
    <string>app_icon.icns</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
</dict>
</plist>'''
    
    with open(app_path / "Contents" / "Info.plist", "w", encoding="utf-8") as f:
        f.write(info_plist_content)
    
    print("   ✅ Info.plist erstellt")
    print(f"✅ {app_name} erfolgreich erstellt!")
    return True

def cleanup_build_files():
    """Bereinigt temporäre Build-Dateien."""
    print("Bereinige temporäre Build-Dateien...")
    
    dirs_to_clean = ["build-Windows", "build-macOS", "__pycache__"]
    files_to_clean = ["USB-Monitor-Windows.spec", "USB-Monitor-macOS.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   ✅ {dir_name} gelöscht")
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"   ✅ {file_name} gelöscht")
    
    print("✅ Bereinigung abgeschlossen")

def create_download_package():
    """Erstellt ein Download-Paket mit beiden Plattformen."""
    print("Erstelle Download-Paket...")
    
    # Download-Ordner erstellen
    download_dir = Path("downloads")
    if download_dir.exists():
        shutil.rmtree(download_dir)
    
    download_dir.mkdir()
    
    # Windows ausführbare Datei kopieren (kann .exe oder ohne Erweiterung sein)
    windows_exe = Path("dist") / "USB-Monitor-Windows.exe"
    windows_exe_no_ext = Path("dist") / "USB-Monitor-Windows"
    
    if windows_exe.exists():
        shutil.copy2(windows_exe, download_dir / "USB-Monitor.exe")
        print("   ✅ Windows .exe kopiert")
    elif windows_exe_no_ext.exists():
        shutil.copy2(windows_exe_no_ext, download_dir / "USB-Monitor.exe")
        print("   ✅ Windows ausführbare Datei kopiert (als .exe)")
    else:
        print("   ❌ Windows ausführbare Datei nicht gefunden")
    
    # macOS .app kopieren
    macos_app = Path("USB-Monitor.app")
    if macos_app.exists():
        shutil.copytree(macos_app, download_dir / "USB-Monitor.app")
        
        # Berechtigungen für das Download-Paket setzen
        try:
            download_app = download_dir / "USB-Monitor.app"
            os.chmod(download_app, 0o755)
            os.chmod(download_app / "Contents", 0o755)
            os.chmod(download_app / "Contents" / "MacOS", 0o755)
            os.chmod(download_app / "Contents" / "MacOS" / "USB-Monitor", 0o755)
            print("   ✅ macOS .app kopiert und Berechtigungen gesetzt")
        except Exception as e:
            print(f"   ⚠️  Warnung: Konnte nicht alle Berechtigungen setzen: {e}")
    else:
        print("   ❌ macOS .app nicht gefunden")
    
    # README für Benutzer erstellen
    readme_content = """# USB-Monitor - Download-Paket

Dieses Paket enthält USB-Monitor für beide Plattformen.

## Windows
- **USB-Monitor.exe** - Doppelklicken Sie auf diese Datei, um USB-Monitor zu starten
- Keine Installation erforderlich!

## macOS
- **USB-Monitor.app** - Ziehen Sie diese Datei in den Applications-Ordner
- Oder doppelklicken Sie direkt darauf

## macOS - Falls die App nicht startet:

### Methode 1: Über den Finder
1. Öffnen Sie den Finder
2. Navigieren Sie zu diesem downloads-Ordner
3. Rechtsklick auf "USB-Monitor.app"
4. Wählen Sie "Öffnen" aus dem Kontextmenü
5. Bestätigen Sie mit "Öffnen" im Sicherheitsdialog

### Methode 2: Gatekeeper-Einstellungen
1. Öffnen Sie "Systemeinstellungen" → "Sicherheit & Datenschutz"
2. Unter "Allgemein" sollte eine Meldung über "USB-Monitor" stehen
3. Klicken Sie auf "Trotzdem öffnen"

### Methode 3: Terminal (für erfahrene Benutzer)
```bash
# Navigieren Sie zum downloads-Ordner
cd /path/to/downloads

# App direkt starten
./USB-Monitor.app/Contents/MacOS/USB-Monitor
```

## Hinweise
- Die erste Ausführung kann einige Sekunden dauern
- Bei macOS: Falls Sie eine Sicherheitswarnung erhalten, klicken Sie mit der rechten Maustaste und wählen Sie 'Öffnen'
- Alle USB-Geräte und COM-Ports werden automatisch erkannt

## Support
Bei Problemen besuchen Sie: https://github.com/username/USB-Monitor
"""
    
    with open(download_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("   ✅ README.txt erstellt")
    print(f"✅ Download-Paket erstellt in: {download_dir}")
    
    return True

def main():
    """Hauptfunktion."""
    print_header("USB-Monitor Cross-Platform Build")
    print("Dieses Skript erstellt USB-Monitor für Windows und macOS!")
    print()
    
    # Voraussetzungen prüfen
    if not check_python():
        return 1
    
    if not check_pip():
        return 1
    
    print()
    
    # Abhängigkeiten installieren
    if not install_dependencies():
        return 1
    
    print()
    
    # Beide Plattformen bauen
    print("🚀 Starte Cross-Platform Build...")
    print()
    
    # Windows Build
    windows_success = build_for_platform("Windows", "assets/icons/app_icon.ico")
    print()
    
    # macOS Build
    macos_success = build_for_platform("macOS", "assets/icons/app_icon.icns")
    print()
    
    if not windows_success or not macos_success:
        print("❌ Ein oder mehrere Builds sind fehlgeschlagen!")
        return 1
    
    # macOS .app Bundle erstellen
    if macos_success:
        if not create_macos_app_bundle():
            return 1
        print()
    
    # Download-Paket erstellen
    if not create_download_package():
        return 1
    
    print()
    
    # Bereinigung
    cleanup_build_files()
    
    print()
    print_header("Cross-Platform Build erfolgreich abgeschlossen!")
    
    print("🎉 Beide ausführbaren Dateien wurden erstellt!")
    print()
    print("📁 Windows: dist/USB-Monitor-Windows.exe")
    print("📁 macOS: USB-Monitor.app")
    print("📦 Download-Paket: downloads/")
    print()
    print("💡 Sie können jetzt:")
    print("   - Die .exe-Datei an Windows-Benutzer weitergeben")
    print("   - Die .app-Datei an macOS-Benutzer weitergeben")
    print("   - Das gesamte downloads/ Verzeichnis verteilen")
    print()
    print("🚀 Endbenutzer müssen nur doppelklicken - keine Installation erforderlich!")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Build durch Benutzer abgebrochen")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unerwarteter Fehler: {e}")
        sys.exit(1)
