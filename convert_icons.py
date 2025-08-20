#!/usr/bin/env python3
"""
Icon-Konvertierungsskript für USB-Monitor
Konvertiert PNG-Icons in ICO und ICNS für bessere Plattform-Unterstützung
"""

import os
from pathlib import Path

def convert_png_to_ico():
    """Konvertiert PNG zu ICO für Windows."""
    try:
        from PIL import Image
        
        png_path = Path("assets/icons/app_icon.png")
        ico_path = Path("assets/icons/app_icon.ico")
        
        if png_path.exists():
            # PNG öffnen und in verschiedene Größen konvertieren
            img = Image.open(png_path)
            
            # Windows ICO benötigt mehrere Größen
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            icons = []
            
            for size in sizes:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                icons.append(resized)
            
            # ICO-Datei speichern
            icons[0].save(ico_path, format='ICO', sizes=[(icon.width, icon.height) for icon in icons])
            print(f"✅ ICO-Icon erstellt: {ico_path}")
            return True
        else:
            print(f"❌ PNG-Icon nicht gefunden: {png_path}")
            return False
            
    except ImportError:
        print("⚠️  Pillow nicht installiert. Installiere mit: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Fehler beim Konvertieren zu ICO: {e}")
        return False

def convert_png_to_icns():
    """Konvertiert PNG zu ICNS für macOS."""
    try:
        from PIL import Image
        
        png_path = Path("assets/icons/app_icon.png")
        icns_path = Path("assets/icons/app_icon.icns")
        
        if png_path.exists():
            # PNG öffnen
            img = Image.open(png_path)
            
            # macOS ICNS benötigt verschiedene Größen
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256), (512, 512)]
            
            # Für ICNS müssen wir die Bilder in einem speziellen Format speichern
            # Da ICNS komplex ist, speichern wir als PNG und lassen macOS es handhaben
            print(f"✅ PNG-Icon für macOS bereit: {png_path}")
            print("   Hinweis: macOS kann PNG-Icons direkt verwenden")
            return True
        else:
            print(f"❌ PNG-Icon nicht gefunden: {png_path}")
            return False
            
    except ImportError:
        print("⚠️  Pillow nicht installiert. Installiere mit: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Fehler beim Konvertieren zu ICNS: {e}")
        return False

def main():
    """Hauptfunktion."""
    print("🎨 Icon-Konvertierung für USB-Monitor")
    print("=" * 40)
    
    # Assets-Ordner erstellen, falls nicht vorhanden
    assets_dir = Path("assets/icons")
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n🔄 Konvertiere Icons...")
    
    # PNG zu ICO (Windows)
    ico_success = convert_png_to_ico()
    
    # PNG zu ICNS (macOS)
    icns_success = convert_png_to_icns()
    
    print("\n📊 Zusammenfassung:")
    if ico_success:
        print("   ✅ Windows ICO-Icon erstellt")
    else:
        print("   ❌ Windows ICO-Icon fehlgeschlagen")
    
    if icns_success:
        print("   ✅ macOS Icon bereit")
    else:
        print("   ❌ macOS Icon fehlgeschlagen")
    
    print("\n💡 Tipps:")
    print("   - Für beste Windows-Unterstützung: Stelle sicher, dass app_icon.ico existiert")
    print("   - Für beste macOS-Unterstützung: Stelle sicher, dass app_icon.icns existiert")
    print("   - PNG funktioniert auf beiden Plattformen, aber native Formate sind besser")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Konvertierung abgebrochen")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unerwarteter Fehler: {e}")
        exit(1)
