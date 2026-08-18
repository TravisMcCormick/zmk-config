# ZMK Config - Corne Keyboard

Personal ZMK firmware configuration for my Corne (CRKBD) split keyboard.

## Features

- **Layout:** Colemak-DH
- **Keyboard:** Corne (3x6 + 3 thumb keys per side)
- **Display:** nice!view support
- **Connectivity:** Bluetooth with boosted TX power

## Layers

- **Layer 0:** Base layer (Colemak-DH)
- **Layer 1:** Numbers, navigation, and Bluetooth controls
- **Layer 2:** Symbols
- **Layer 3:** System (Reset/Bootloader) - activated via combo

<!-- KEYMAP_START -->
## Keymap

*Auto-generated from [`corne.keymap`](config/corne.keymap)*

**Legend:**
- `▽` = Transparent (uses key from lower layer)
- `X` = None (no action)
- `L#` = Momentary layer switch

<!-- KEYMAP_END -->

## Building

Firmware is automatically built via GitHub Actions when changes are pushed. Download the latest firmware from the [Actions tab](../../actions).

## Configuration

| Setting | Value |
|---------|-------|
| Keyboard Name | "Corne" |
| Debounce (press/release) | 5ms / 5ms |
| Bluetooth TX Power | +8 dBm |

## Combos

| Keys | Action |
|------|--------|
| Both inner thumb keys (37 + 40) | Activate Layer 3 |

## Resources

- [ZMK Documentation](https://zmk.dev/docs)
- [Corne Keyboard](https://github.com/foostan/crkbd)
