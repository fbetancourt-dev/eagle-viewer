# EAGLE CAD Standalone Interactive Web & Vector Viewer (`eagle-viewer`)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![CLI](https://img.shields.io/badge/CLI-Standalone-green.svg)](https://github.com/fbetancourt-dev/eagle-viewer)
[![Companion Skill](https://img.shields.io/badge/Agentic_Skill-eagle--cad--skill-purple.svg)](https://github.com/fbetancourt-dev/eagle-cad-skill)

A standalone, zero-dependency Python CLI tool and interactive web visualizer for **Autodesk & CadSoft EAGLE CAD** schematic (`.sch`) and printed circuit board layout (`.brd`) XML files.

Designed to be executed directly as a first-class engineering CLI application (with full parameter customization) or orchestrated autonomously by AI coding agents via [eagle-cad-skill](https://github.com/fbetancourt-dev/eagle-cad-skill).

---

## 🏛️ Architecture & Pipeline

```mermaid
flowchart TD
    subgraph Inputs ["Input Files & CLI Flags"]
        SCH[".sch Schematic XML"]
        BRD[".brd Layout XML"]
        Flags["CLI Flags\n(-o, --export-svg, --no-open, --json-only)"]
    end

    subgraph CoreEngine ["Core Engine (eagle_viewer)"]
        Resolver["Smart Companion Resolver\n(auto-detects .sch/.brd pairs)"]
        Parser["EagleParser\n(native XML topologic extractor)"]
        SVGGen["EagleToSvg\n(scale-independent vector renderer)"]
        HTMLBuilder["Template Engine\n(injected self-contained HTML)"]
    end

    subgraph Outputs ["Outputs & Integrations"]
        Web["Interactive Web Canvas\n(Zoom/Pan, Layers, BOM, Ratsnest)"]
        SVGs["Vector SVG Files\n(schematic.svg & board.svg)"]
        JSON["Structured JSON\n(UNIX pipelines & agent automation)"]
    end

    Inputs --> Resolver --> Parser
    Flags --> CoreEngine
    Parser --> SVGGen --> SVGs
    Parser --> HTMLBuilder --> Web
    Parser --> JSON
```

---

## ✨ Features

- **Interactive Canvas & Smooth Zoom/Pan Engine:** Real-time panning with mouse-drag (attached to window to prevent freeze on rapid movement), wheel zoom centered at cursor position, touch gesture support, and visible on-screen `[+]`, `[-]`, and `[⛶ Centrar]` (auto-fit bounding box) controls.
- **Ratsnest Copper Pour Mode:** Visualizes polygon ground and power planes with 38% opacity and solid borders, allowing inspection of copper fills and return paths without obscuring signal tracks.
- **Quick Layer Isolation & Flip X:** One-click presets for `[Top]`, `[Bottom]` (with realistic horizontal reflection matching a physical PCB back side), `[Ambas]` (combined view), and manual flip toggle.
- **Smart Companion Auto-Discovery:** Pointing to `circuit.brd` automatically locates and loads `circuit.sch` in the same directory (and vice-versa).
- **Vector SVG & High-Res PNG Exporter:** Generates high-resolution, scale-independent vector SVGs and crisp 1600x1000 PNG previews for both schematic and board layers for documentation, reports, and artifact embedding.
- **Clean UNIX Pipeline Compatibility:** Output topology JSON directly to `stdout` (`--json-only`) with graceful broken pipe handling for tools like `jq`, `grep`, and headless CI automation.
- **Autodesk EAGLE 7.7.0 Automation:** Full compatibility with native EAGLE scripts (`top.scr`, `bottom.scr`, `both.scr`, `all.scr`), keybindings (`Ctrl+T`, `Ctrl+B`, `Ctrl+A`), and headless batch export with `-N-` flag.
- **Zero Heavy Web Dependencies:** Self-contained, single-file HTML generation without requiring Node.js, npm, Webpack, or external web runtimes.
- **Skill-Ready Architecture:** Clean separation of concerns allowing seamless use as a standalone command-line tool or as the visual engine for [eagle-cad-skill](https://github.com/fbetancourt-dev/eagle-cad-skill).

---

## 📥 Installation & Setup

### 1. Global User Binary (Recommended)
Link the executable script directly to your user PATH:
```bash
ln -sf $(pwd)/main.py ~/.local/bin/eagle-viewer
chmod +x ~/.local/bin/eagle-viewer
```

Verify the installation:
```bash
eagle-viewer --version
```

### 2. Pip Editable Mode
Install locally into your active Python environment:
```bash
pip install -e .
```

---

## 💻 CLI Reference

```bash
eagle-viewer [files ...] [options]
```

### Options

| Flag | Type | Description |
| :--- | :--- | :--- |
| `files` | `positional` | Path to `.sch` and/or `.brd` files, or circuit name without extension. |
| `--sch <path>` | `string` | Explicit path to EAGLE schematic XML file (`.sch`). |
| `--brd <path>` | `string` | Explicit path to EAGLE board XML file (`.brd`). |
| `-o, --output <path>` | `string` | Custom path for generated HTML viewer (default: `<name>_viewer.html`). |
| `--export-svg [dir]` | `string?` | Export schematic and PCB vector SVGs (optional target directory). |
| `--export-png [dir]` | `string?` | Export schematic and PCB PNG previews via headless Chrome (target directory). |
| `--no-open` | `flag` | Generate viewer and assets without launching default web browser. |
| `--json-only` | `flag` | Print parsed circuit topology JSON to stdout and exit. |
| `--json [file]` | `string?` | Save parsed circuit topology JSON to a file (or stdout if `-`). |
| `--theme {dark,classic}` | `choice` | Default viewer theme (default: `dark`). |
| `-v, --version` | `flag` | Show program version. |
| `-h, --help` | `flag` | Show help and argument summary. |

---

## 🕹️ Navigation Controls

| Action | Control | Description |
| :--- | :--- | :--- |
| **Zoom In / Out** | `[+]` / `[−]` Buttons | Smoothly magnify or de-magnify schematic or board canvas. |
| **Wheel Zoom** | `Mouse Wheel` | Continuous scaling centered precisely at the mouse cursor position. |
| **Auto-Fit / Center** | `[⛶ Centrar]` Button | Computes the exact bounding box and centers the circuit with optimal scale. |
| **Pan (Move Canvas)** | `Left-click Drag` | Fluid panning with window-level mouse capture and touch screen support. |
| **Top Layer Only** | `[Top]` Button | Isolates Layer 1 Top copper, pads, vias, dimension, and top silkscreen. |
| **Bottom Layer Only** | `[Bottom]` Button | Isolates Layer 16 Bottom copper with physical horizontal mirroring (`Flip X`). |
| **Both Layers** | `[Ambas]` Button | Combined transparent view of both copper layers for routing inspection. |
| **Flip Board** | `[Voltear 🔄]` Button | Manually toggle horizontal reflection at any time. |

---

## 🦅 Native Autodesk EAGLE 7.7.0 Automation

The viewer suite integrates seamlessly with local Autodesk EAGLE installations:
- **Layer Isolation Scripts (`~/Applications/eagle-7.7.0/scr/`):**
  - `top.scr`: `DISPLAY NONE 1 17 18 19 20 21 23 25 45 51; RATSNEST;`
  - `bottom.scr`: `DISPLAY NONE 16 17 18 19 20 22 24 26 45 52; RATSNEST;`
  - `both.scr`: `DISPLAY 1 16 17 18 19 20 21 22 23 24 25 26 45 51 52; RATSNEST;`
  - `all.scr`: `DISPLAY ALL; RATSNEST;`
- **Permanent Shortcuts (`eagle.scr`):** `Ctrl+T` (Top), `Ctrl+B` (Bottom), `Ctrl+A` (Both), `Ctrl+Shift+A` (All).
- **Headless Batch Export with `-N-`:** Always use the `-N-` flag to suppress modal save confirmation prompts:
  ```bash
  eagle -N- -C "SCRIPT top.scr; EXPORT IMAGE 'top.png' 300; QUIT;" circuit.brd
  ```
- **Desktop DOM Automation (`dogtail`):** Use AT-SPI accessibility tree to catch and handle any unhandled GUI dialogs programmatically.

---

## 🚀 Examples

### 1. Open Interactive Viewer for Schematic and PCB
```bash
eagle-viewer usb_c_charger.sch usb_c_charger.brd
```

### 2. Auto-discover Companion File
Passing only the board automatically finds and loads the matching schematic:
```bash
eagle-viewer usb_c_charger.brd
```

### 3. Headless SVG Export for CI / Documentation
```bash
eagle-viewer usb_c_charger.brd --export-svg ./svg_assets/ --no-open -o ./docs/index.html
```

### 4. Extract Circuit JSON for UNIX Pipelines
```bash
eagle-viewer usb_c_charger.brd --json-only | jq '.board.elements[] | {name: .name, value: .value}'
```

---

## 🔗 Related Projects

- **[`eagle-cad-skill`](https://github.com/fbetancourt-dev/eagle-cad-skill):** Autonomous AI agent skill providing ERC/DRC auditing, hybrid autorouting, BOM extraction, and programmatic editing for EAGLE CAD files.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.  
Created by **Francisco Betancourt** & **Antigravity (Sam)**.
