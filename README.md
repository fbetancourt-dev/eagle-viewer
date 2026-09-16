# EAGLE CAD Standalone Interactive Web & Vector Viewer (`eagle-viewer`)

A standalone, zero-dependency Python CLI tool and interactive web visualizer for Autodesk and CadSoft EAGLE CAD schematic (`.sch`) and printed circuit board layout (`.brd`) XML files.

---

## Features

- **Interactive Canvas & SVG Web Viewer:** Real-time panning, zooming, layer filtering (Top, Bottom, Silkscreen, Pads, Vias, Dimension), and ratsnest visualization in modern browsers.
- **Companion Auto-Discovery:** Pointing to `circuit.brd` automatically finds and loads `circuit.sch` in the same directory (and vice versa).
- **Vector SVG Exporter:** Export high-resolution, scale-independent vector SVGs of schematics and PCB layouts.
- **JSON Topology Dumping:** Dump parsed circuits directly to structured JSON for automation scripts, pipelines, and AI agents.
- **Zero Heavy Web Dependencies:** Self-contained, single-file HTML generation without Node.js or web build steps required.
- **Skill-Ready Architecture:** Designed to work standalone or integrated seamlessly with Antigravity / Gemini EDA skills.

---

## Installation & Setup

### Local User Binary
Link or copy `main.py` to your user PATH:
```bash
ln -sf $(pwd)/main.py ~/.local/bin/eagle-viewer
```

Or install in editable mode with pip:
```bash
pip install -e .
```

---

## CLI Usage

```bash
eagle-viewer [files ...] [options]
```

### Options

| Flag | Description |
|------|-------------|
| `files` | Path to `.sch` and/or `.brd` files, or circuit name without extension. |
| `--sch <path>` | Explicit path to EAGLE schematic XML file (`.sch`). |
| `--brd <path>` | Explicit path to EAGLE board XML file (`.brd`). |
| `-o, --output <path>` | Custom path for generated HTML viewer (default: `<name>_viewer.html`). |
| `--export-svg [dir]` | Export schematic and PCB vector SVGs (optional target directory). |
| `--no-open` | Generate viewer and assets without opening the default web browser. |
| `--json-only` | Print parsed circuit topology JSON to stdout and exit. |
| `--json [file]` | Save parsed circuit topology JSON to a file (or stdout if `-`). |
| `--theme {dark,classic}` | Default viewer theme (default: `dark`). |
| `-v, --version` | Show program version. |

---

## Examples

### 1. View Schematic and Board
```bash
eagle-viewer usb_c_charger.sch usb_c_charger.brd
```

### 2. Auto-discover Companion File
```bash
eagle-viewer usb_c_charger.brd
```

### 3. Headless Export for CI/Agents
```bash
eagle-viewer usb_c_charger.brd --export-svg ./svgs/ --no-open -o ./public/index.html
```

### 4. Extract Circuit JSON for Scripting
```bash
eagle-viewer usb_c_charger.brd --json-only > circuit.json
```

---

## License
MIT License. Created by Francisco Betancourt & Antigravity (Sam).
