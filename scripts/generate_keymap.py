#!/usr/bin/env python3
"""
Parses a ZMK keymap file and generates a markdown visualization.
"""

import re
import sys
from pathlib import Path

# Key display mappings for common ZMK keycodes
KEY_DISPLAY = {
    # Letters
    "kp A": "A", "kp B": "B", "kp C": "C", "kp D": "D", "kp E": "E",
    "kp F": "F", "kp G": "G", "kp H": "H", "kp I": "I", "kp J": "J",
    "kp K": "K", "kp L": "L", "kp M": "M", "kp N": "N", "kp O": "O",
    "kp P": "P", "kp Q": "Q", "kp R": "R", "kp S": "S", "kp T": "T",
    "kp U": "U", "kp V": "V", "kp W": "W", "kp X": "X", "kp Y": "Y",
    "kp Z": "Z",
    # Numbers
    "kp N0": "0", "kp N1": "1", "kp N2": "2", "kp N3": "3", "kp N4": "4",
    "kp N5": "5", "kp N6": "6", "kp N7": "7", "kp N8": "8", "kp N9": "9",
    # Modifiers
    "kp TAB": "Tab", "kp ESCAPE": "Esc", "kp ESC": "Esc",
    "kp LEFT_CONTROL": "Ctrl", "kp LCTRL": "Ctrl", "kp RIGHT_CONTROL": "Ctrl",
    "kp LEFT_SHIFT": "Shift", "kp LSHFT": "Shift", "kp RIGHT_SHIFT": "Shift",
    "kp LEFT_ALT": "Alt", "kp LALT": "Alt", "kp RIGHT_ALT": "AltGr",
    "kp LGUI": "GUI", "kp RGUI": "GUI",
    "kp SPACE": "Space", "kp BACKSPACE": "Bksp", "kp RET": "Enter", "kp ENTER": "Enter",
    # Punctuation
    "kp SEMICOLON": ";", "kp SEMI": ";", "kp SQT": "'", "kp APOS": "'",
    "kp COMMA": ",", "kp DOT": ".", "kp FSLH": "/", "kp SLASH": "/",
    "kp BSLH": "\\", "kp BACKSLASH": "\\",
    "kp LBKT": "[", "kp RBKT": "]", "kp LBRC": "{", "kp RBRC": "}",
    "kp LPAR": "(", "kp RPAR": ")",
    "kp MINUS": "-", "kp EQUAL": "=", "kp PLUS": "+", "kp UNDER": "_",
    "kp GRAVE": "`", "kp TILDE": "~",
    "kp EXCL": "!", "kp AT": "@", "kp HASH": "#", "kp DLLR": "$",
    "kp PRCNT": "%", "kp CARET": "^", "kp AMPS": "&", "kp ASTRK": "*",
    "kp PIPE": "|",
    # Navigation
    "kp LEFT": "←", "kp RIGHT": "→", "kp UP": "↑", "kp DOWN": "↓",
    "kp HOME": "Home", "kp END": "End", "kp PG_UP": "PgUp", "kp PG_DN": "PgDn",
    # Bluetooth
    "bt BT_CLR": "BT Clr", "bt BT_SEL 0": "BT 0", "bt BT_SEL 1": "BT 1",
    "bt BT_SEL 2": "BT 2", "bt BT_SEL 3": "BT 3", "bt BT_SEL 4": "BT 4",
    # System
    "sys_reset": "Reset", "bootloader": "Boot",
    # Transparent/None
    "trans": "▽", "none": "✕",
}


def parse_binding(binding: str) -> str:
    """Convert a ZMK binding to a display string."""
    binding = binding.strip().lstrip("&")
    
    # Handle layer toggles
    if binding.startswith("mo "):
        layer_num = binding.split()[1]
        return f"L{layer_num}"
    if binding.startswith("to "):
        layer_num = binding.split()[1]
        return f"TO{layer_num}"
    if binding.startswith("lt "):
        parts = binding.split()
        return f"LT{parts[1]}"
    
    # Look up in display mappings
    if binding in KEY_DISPLAY:
        return KEY_DISPLAY[binding]
    
    # Handle kp with unknown key
    if binding.startswith("kp "):
        return binding[3:].capitalize()
    
    return binding[:6]  # Truncate unknown bindings


def parse_keymap(content: str) -> dict:
    """Parse a ZMK keymap file and extract layers."""
    layers = {}
    
    # Remove C-style comments that might contain braces
    # Remove // line comments
    content_no_comments = re.sub(r'//[^\n]*', '', content)
    # Remove /* */ block comments
    content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)
    
    # Find all layer blocks with bindings
    # Match pattern: LayerName { ... bindings = <keys>; ... }
    layer_pattern = r'(Layer_\d+|layer_\d+)\s*\{[^{}]*?bindings\s*=\s*<\s*([^>]+)\s*>'
    matches = re.findall(layer_pattern, content_no_comments, re.DOTALL)
    
    for layer_name, bindings_str in matches:
        # Parse bindings
        bindings_str = bindings_str.replace('\n', ' ')
        # Split by & but keep the &
        raw_bindings = re.split(r'(?=&)', bindings_str)
        bindings = [b.strip() for b in raw_bindings if b.strip()]
        
        # Only include if it looks like a full layer (more than just a few keys)
        if len(bindings) >= 36:  # Corne has at least 36 keys
            layers[layer_name] = bindings
    
    # Sort layers by number
    sorted_layers = {}
    for name in sorted(layers.keys(), key=lambda x: int(re.search(r'\d+', x).group())):
        sorted_layers[name] = layers[name]
    
    return sorted_layers


def format_corne_layer(bindings: list, layer_name: str) -> str:
    """Format a layer for a Corne (3x6+3 split) keyboard."""
    keys = [parse_binding(b) for b in bindings]
    
    # Corne has 42 keys total (6x3 + 3 thumb per side = 36 + 6)
    if len(keys) < 42:
        keys.extend([""] * (42 - len(keys)))
    
    # Corne layout: 6 keys per row, 3 rows, plus 3 thumb keys per side
    def fmt(key, width=7):
        return key.center(width)
    
    lines = []
    lines.append(f"### {layer_name}")
    lines.append("```")
    lines.append("┌───────┬───────┬───────┬───────┬───────┬───────┐       ┌───────┬───────┬───────┬───────┬───────┬───────┐")
    
    # Row 1
    row1_left = "│".join([fmt(keys[i]) for i in range(6)])
    row1_right = "│".join([fmt(keys[i]) for i in range(6, 12)])
    lines.append(f"│{row1_left}│       │{row1_right}│")
    
    lines.append("├───────┼───────┼───────┼───────┼───────┼───────┤       ├───────┼───────┼───────┼───────┼───────┼───────┤")
    
    # Row 2
    row2_left = "│".join([fmt(keys[i]) for i in range(12, 18)])
    row2_right = "│".join([fmt(keys[i]) for i in range(18, 24)])
    lines.append(f"│{row2_left}│       │{row2_right}│")
    
    lines.append("├───────┼───────┼───────┼───────┼───────┼───────┤       ├───────┼───────┼───────┼───────┼───────┼───────┤")
    
    # Row 3
    row3_left = "│".join([fmt(keys[i]) for i in range(24, 30)])
    row3_right = "│".join([fmt(keys[i]) for i in range(30, 36)])
    lines.append(f"│{row3_left}│       │{row3_right}│")
    
    lines.append("└───────┴───────┴───────┼───────┼───────┼───────┤       ├───────┼───────┼───────┼───────┴───────┴───────┘")
    
    # Thumb row
    thumb_left = "│".join([fmt(keys[i]) for i in range(36, 39)])
    thumb_right = "│".join([fmt(keys[i]) for i in range(39, 42)])
    lines.append(f"                        │{thumb_left}│       │{thumb_right}│")
    
    lines.append("                        └───────┴───────┴───────┘       └───────┴───────┴───────┘")
    lines.append("```")
    
    return "\n".join(lines)


def generate_markdown(keymap_path: str) -> str:
    """Generate markdown documentation for a keymap."""
    content = Path(keymap_path).read_text()
    layers = parse_keymap(content)
    
    output = []
    output.append("## Keymap")
    output.append("")
    output.append(f"*Auto-generated from [`{Path(keymap_path).name}`](config/{Path(keymap_path).name})*")
    output.append("")
    output.append("**Legend:** `▽` = Transparent (uses key from lower layer), `L#` = Momentary layer switch")
    output.append("")
    
    for layer_name, bindings in layers.items():
        output.append(format_corne_layer(bindings, layer_name))
        output.append("")
    
    return "\n".join(output)


def update_readme(readme_path: str, keymap_content: str) -> None:
    """Update README with keymap content between markers."""
    start_marker = "<!-- KEYMAP_START -->"
    end_marker = "<!-- KEYMAP_END -->"
    
    readme = Path(readme_path)
    if readme.exists():
        content = readme.read_text()
        if start_marker in content and end_marker in content:
            before = content.split(start_marker)[0]
            after = content.split(end_marker)[1]
            new_content = f"{before}{start_marker}\n{keymap_content}\n{end_marker}{after}"
            readme.write_text(new_content)
            return
    
    print(f"Warning: Could not find markers in {readme_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: generate_keymap.py <keymap_file> [readme_file]")
        sys.exit(1)
    
    keymap_file = sys.argv[1]
    markdown = generate_markdown(keymap_file)
    
    if len(sys.argv) >= 3:
        update_readme(sys.argv[2], markdown)
        print(f"Updated {sys.argv[2]}")
    else:
        print(markdown)
