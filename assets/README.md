# USB-Monitor Assets

## App-Icons

### Erforderliche Dateien:

1. **`app_icon.png`** - Hauptanwendungs-Icon
   - **Größe**: 512x512 px oder 1024x1024 px
   - **Format**: PNG mit transparentem Hintergrund
   - **Verwendung**: Fenster-Icon, Taskbar, macOS Dock

2. **`logo.png`** - GitHub/README Logo
   - **Größe**: 200x200 px oder größer
   - **Format**: PNG
   - **Verwendung**: README Header, GitHub Repository

### Icon-Anforderungen:

- **Stil**: Modern, minimalistisch
- **Farben**: Passend zum USB-Theme (blau/grau/schwarz)
- **Symbole**: USB-Stecker, Monitor/Display, Verbindungslinien
- **Kompatibilität**: Gut sichtbar in Hell- und Dunkel-Modi

### Automatische Integration:

Die Icons werden automatisch erkannt und verwendet:
- App startet mit eigenem Icon (falls `app_icon.png` vorhanden)
- Fallback auf System-USB-Icon
- PyInstaller Build verwendet das Icon automatisch

### Beispiel-Platzierung:

```
assets/
├── icons/
│   ├── app_icon.png     ← Dein App-Icon hier
│   ├── logo.png         ← Dein GitHub-Logo hier
│   └── README.md        ← Diese Datei
```
