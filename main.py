#!/usr/bin/env python3
"""
===============================================================================
EAGLE CAD Standalone Interactive Web & Vector Viewer CLI (eagle-viewer)
===============================================================================
Author: Francisco Betancourt & Antigravity (Sam)
Description:
    Standalone CLI application to parse Autodesk and CadSoft EAGLE CAD
    schematic (.sch) and board layout (.brd) XML files into an interactive,
    zero-dependency web visualizer and vector SVG exports.
"""

import sys
import os
import json
import argparse
import webbrowser
from typing import Optional, Tuple, Dict, Any

# Ensure local modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eagle_parser import EagleParser
from eagle_to_svg import EagleToSvg

__version__ = "1.0.0"


def resolve_files(
    positional_files: list,
    explicit_sch: Optional[str] = None,
    explicit_brd: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Intelligently resolves schematic and board paths from positional and explicit arguments.
    Supports auto-detecting companion .sch / .brd files when only one is provided.
    """
    sch_path = explicit_sch
    brd_path = explicit_brd

    for f in positional_files:
        if not f:
            continue
        lower = f.lower()
        if lower.endswith(".sch") and not sch_path:
            sch_path = f
        elif lower.endswith(".brd") and not brd_path:
            brd_path = f
        elif not sch_path and not brd_path:
            # Check if base name without extension was provided
            base = os.path.splitext(f)[0]
            candidate_sch = f"{base}.sch"
            candidate_brd = f"{base}.brd"
            if os.path.exists(candidate_sch):
                sch_path = candidate_sch
            if os.path.exists(candidate_brd):
                brd_path = candidate_brd
            if not sch_path and not brd_path:
                # Assign as is if existing file
                if os.path.exists(f):
                    if lower.endswith(".sch"):
                        sch_path = f
                    elif lower.endswith(".brd"):
                        brd_path = f

    # Companion auto-discovery: if only one file was provided, look for the other in the same dir
    if sch_path and not brd_path:
        companion_brd = os.path.splitext(sch_path)[0] + ".brd"
        if os.path.exists(companion_brd):
            brd_path = companion_brd

    if brd_path and not sch_path:
        companion_sch = os.path.splitext(brd_path)[0] + ".sch"
        if os.path.exists(companion_sch):
            sch_path = companion_sch

    return sch_path, brd_path


def build_viewer_html(circuit_data: Dict[str, Any], template_path: str) -> str:
    """Injects parsed circuit JSON into the viewer HTML template."""
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Viewer HTML template not found at '{template_path}'")

    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    json_str = json.dumps(circuit_data, indent=2)
    return html_content.replace("/*EAGLE_DATA_PLACEHOLDER*/", json_str)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="eagle-viewer",
        description="EAGLE CAD Standalone Interactive Web & Vector Viewer CLI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Open interactive viewer for schematic and board:
  eagle-viewer usb_c_charger.sch usb_c_charger.brd

  # Auto-discover companion file (.sch or .brd in same directory):
  eagle-viewer usb_c_charger.brd

  # Generate HTML silently without opening the browser:
  eagle-viewer usb_c_charger.brd --no-open -o /tmp/charger_viewer.html

  # Export vector SVGs for schematic and PCB:
  eagle-viewer usb_c_charger.brd --export-svg ./svg_output/ --no-open

  # Dump parsed circuit topology to JSON:
  eagle-viewer usb_c_charger.brd --json-only > circuit.json
"""
    )

    parser.add_argument(
        "files",
        nargs="*",
        help="Path to .sch and/or .brd files, or a base name without extension."
    )
    parser.add_argument(
        "--sch",
        type=str,
        default=None,
        help="Explicit path to EAGLE schematic XML file (.sch)."
    )
    parser.add_argument(
        "--brd",
        type=str,
        default=None,
        help="Explicit path to EAGLE board XML file (.brd)."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output path for the generated interactive HTML viewer (default: <name>_viewer.html)."
    )
    parser.add_argument(
        "--export-svg",
        nargs="?",
        const=".",
        default=None,
        metavar="DIR",
        help="Export vector SVG files for schematic and/or PCB. Optional directory target."
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Generate viewer and exports without opening default web browser."
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Print parsed circuit topology JSON to stdout and exit."
    )
    parser.add_argument(
        "--json",
        type=str,
        nargs="?",
        const="-",
        default=None,
        metavar="FILE",
        help="Save parsed circuit topology JSON to a file (or stdout if '-')."
    )
    parser.add_argument(
        "--theme",
        choices=["dark", "classic"],
        default="dark",
        help="Default viewer theme (default: dark)."
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    sch_path, brd_path = resolve_files(args.files, args.sch, args.brd)

    if not sch_path and not brd_path:
        print("Error: No EAGLE schematic (.sch) or board (.brd) files specified.", file=sys.stderr)
        print("Run 'eagle-viewer --help' for usage and options.", file=sys.stderr)
        sys.exit(1)

    if sch_path and not os.path.exists(sch_path):
        print(f"Error: Schematic file not found: '{sch_path}'", file=sys.stderr)
        sys.exit(1)

    if brd_path and not os.path.exists(brd_path):
        print(f"Error: Board file not found: '{brd_path}'", file=sys.stderr)
        sys.exit(1)

    # Determine circuit design name
    circuit_name = "eagle_design"
    if brd_path:
        circuit_name = os.path.splitext(os.path.basename(brd_path))[0]
    elif sch_path:
        circuit_name = os.path.splitext(os.path.basename(sch_path))[0]

    # Parse files
    if not args.json_only:
        print(f"-> Parsing EAGLE design '{circuit_name}'...")
        if sch_path:
            print(f"   Schematic: {sch_path}")
        if brd_path:
            print(f"   Board:     {brd_path}")

    try:
        parser = EagleParser(sch_path or "", brd_path or "")
        circuit_data = parser.parse()
        circuit_data["name"] = circuit_name
    except Exception as e:
        print(f"Error parsing EAGLE XML files: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle --json-only or --json
    if args.json_only:
        try:
            print(json.dumps(circuit_data, indent=2))
        except BrokenPipeError:
            sys.stderr.close()
        sys.exit(0)

    if args.json:
        json_output_str = json.dumps(circuit_data, indent=2)
        if args.json == "-":
            print(json_output_str)
        else:
            with open(args.json, "w", encoding="utf-8") as f:
                f.write(json_output_str)
            print(f"-> Parsed circuit JSON saved to: {args.json}")

    # Handle SVG export if requested
    if args.export_svg is not None:
        target_dir = args.export_svg
        if target_dir == ".":
            target_dir = os.getcwd()
        os.makedirs(target_dir, exist_ok=True)

        exporter = EagleToSvg(circuit_data)
        if sch_path and circuit_data.get("schematic", {}).get("instances"):
            sch_svg = os.path.join(target_dir, f"{circuit_name}_schematic.svg")
            exporter.export_schematic(sch_svg)
            print(f"-> Exported Schematic SVG: {sch_svg}")

        if brd_path and (circuit_data.get("board", {}).get("elements") or circuit_data.get("board", {}).get("dimension")):
            brd_svg = os.path.join(target_dir, f"{circuit_name}_board.svg")
            exporter.export_board(brd_svg)
            print(f"-> Exported Board PCB SVG: {brd_svg}")

    # Determine HTML output path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "templates", "viewer.html")

    output_path = args.output
    if not output_path:
        output_path = os.path.join(os.getcwd(), f"{circuit_name}_viewer.html")

    try:
        rendered_html = build_viewer_html(circuit_data, template_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)
        print(f"-> Interactive viewer generated successfully: {output_path}")
    except Exception as e:
        print(f"Error generating viewer HTML: {e}", file=sys.stderr)
        sys.exit(1)

    # Launch browser unless --no-open was passed
    if not args.no_open:
        abs_output = os.path.abspath(output_path)
        file_url = f"file://{abs_output}"
        print(f"-> Opening viewer in default browser: {file_url}")
        webbrowser.open(file_url)


if __name__ == "__main__":
    main()
