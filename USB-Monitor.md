# USB-Monitor

Ein modernes, plattformübergreifendes Programm zur Überwachung und Verwaltung von USB-Geräten und COM-Ports.

## Projektübersicht

USB-Monitor ist eine elegante Anwendung, die USB-Geräte und serielle COM-Ports in Echtzeit überwacht. Die Benutzeroberfläche folgt dem modernen macOS-Design und bietet eine intuitive Bedienung für Benutzer beider Plattformen.

## Features

### Kernfunktionen
- **USB-Geräte-Erkennung**: Automatische Erkennung aller angeschlossenen USB-Geräte
- **COM-Port-Überwachung**: Auflistung aller verfügbaren seriellen Ports
- **Echtzeit-Überwachung**: Kontinuierliche Überwachung von Verbindungsänderungen
- **Detaillierte Informationen**: Treiber, Geschwindigkeit, Hersteller, Produkt-ID, etc.

### Benutzeroberfläche
- **Moderne macOS-Ästhetik**: Elegantes, minimalistisches Design
- **Responsive Layout**: Passt sich verschiedenen Bildschirmgrößen an
- **Intuitive Navigation**: Klare Struktur und einfache Bedienung
- **Dunkler/heller Modus**: Unterstützung für beide Design-Varianten

### Plattformunterstützung
- **Windows**: Vollständige Unterstützung für Windows 10/11
- **macOS**: Native macOS-Integration mit System-APIs
- **Kreuzkompatibilität**: Einheitliche Codebasis für beide Plattformen

## Technische Architektur

### Technologie-Stack
- **Python 3.9+**: Hauptprogrammiersprache
- **PyQt6**: Moderne GUI-Framework
- **pyserial**: Serielle Port-Kommunikation
- **pyusb**: USB-Geräte-Erkennung
- **psutil**: System-Informationen

### Projektstruktur
```
USB-Monitor/
├── src/
│   ├── main.py              # Hauptanwendung
│   ├── ui/                  # Benutzeroberfläche
│   │   ├── main_window.py   # Hauptfenster
│   │   ├── device_panel.py  # Geräte-Panel
│   │   ├── port_panel.py    # Port-Panel
│   │   └── styles.py        # CSS-Styles
│   ├── core/                # Kernlogik
│   │   ├── device_monitor.py # USB-Geräte-Überwachung
│   │   ├── port_monitor.py  # COM-Port-Überwachung
│   │   └── system_info.py   # System-Informationen
│   └── utils/               # Hilfsfunktionen
│       ├── platform_utils.py # Plattformspezifische Funktionen
│       └── config.py        # Konfiguration
├── requirements.txt          # Python-Abhängigkeiten
├── README.md                # Projektbeschreibung
└── USB-Monitor.md           # Diese Datei
```

## Datenbankschema

### USB-Geräte-Tabelle
```sql
CREATE TABLE usb_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_name TEXT NOT NULL,
    description TEXT,
    vendor_id TEXT,
    product_id TEXT,
    serial_number TEXT,
    device_type TEXT,
    connection_status TEXT,
    driver_version TEXT,
    usb_version TEXT,
    power_consumption TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_connected BOOLEAN DEFAULT TRUE
);
```

### COM-Port-Tabelle
```sql
CREATE TABLE com_ports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    port_name TEXT NOT NULL,
    device_name TEXT,
    baud_rate INTEGER,
    data_bits INTEGER,
    stop_bits INTEGER,
    parity TEXT,
    flow_control TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Verbindungsprotokoll
```sql
CREATE TABLE connection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER,
    port_id INTEGER,
    event_type TEXT NOT NULL, -- 'connected', 'disconnected', 'error'
    event_description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES usb_devices(id),
    FOREIGN KEY (port_id) REFERENCES com_ports(id)
);
```

## Installation und Setup

### Voraussetzungen
- Python 3.9 oder höher
- pip (Python Package Manager)
- Plattformspezifische USB-Treiber

### Installation
```bash
# Repository klonen
git clone https://github.com/username/USB-Monitor.git
cd USB-Monitor

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
python src/main.py
```

## Verwendung

### Hauptfunktionen
1. **Geräte-Überwachung**: Automatische Erkennung aller USB-Geräte
2. **Port-Management**: Verwaltung und Überwachung von COM-Ports
3. **Echtzeit-Updates**: Kontinuierliche Aktualisierung der Gerätestatus
4. **Detaillierte Ansicht**: Umfassende Informationen zu jedem Gerät

### Tastenkombinationen
- `Ctrl/Cmd + R`: Geräteliste aktualisieren
- `Ctrl/Cmd + S`: Einstellungen öffnen
- `Ctrl/Cmd + Q`: Anwendung beenden
- `F5`: Aktualisieren

## Entwicklung

### Code-Standards
- **PEP 8**: Python-Codestil
- **Type Hints**: Vollständige Typisierung
- **Docstrings**: Umfassende Dokumentation
- **Unit Tests**: Testabdeckung >90%

### Beitragen
1. Fork des Repositories
2. Feature-Branch erstellen
3. Änderungen implementieren
4. Tests hinzufügen
5. Pull Request einreichen

## Lizenz

MIT License - Siehe LICENSE-Datei für Details.

## Changelog

### Version 1.0.0 (Geplant)
- Grundlegende USB-Geräte-Erkennung
- COM-Port-Überwachung
- Moderne Benutzeroberfläche
- Plattformübergreifende Unterstützung

## Bekannte Probleme

- Keine bekannten Probleme zum aktuellen Zeitpunkt

## Support

Bei Fragen oder Problemen:
- GitHub Issues verwenden
- Dokumentation konsultieren
- Community-Forum besuchen
