# Cursor Cape Builder

![Cursor Cape Builder icon](assets/app-icon.svg)

Build a complete [Mousecape](https://github.com/sdmj76/Mousecape-swiftUI) `.cape` cursor theme from the 15 conventional PNG cursor sprite sheets in a macOS cursor pack.

Drop a `.zip` pack or a folder of PNGs onto the app. It produces an importable `.cape` beside the source and closes automatically.

## What it generates

- A Mousecape v2 `.cape` file with all 44 macOS cursor states populated.
- Animated cursor frames embedded directly in the `.cape`; no external image files are required after export.
- Common alias states covered together, including the primary arrow, contextual arrow, link, text, resize, move, waiting, and help cursors.
- A 0.8-second animation cycle by default; the duration per frame is calculated from the supplied frame count.

## Use the prebuilt app

1. Download `Cursor Cape Builder.app` from the [GitHub Releases page](https://github.com/montaluser/cursor-cape-builder/releases).
2. Right-click the app and choose **Open** on first launch.
3. Drag one source `.zip` or source-image folder onto the app icon. You can also double-click the app and choose the source in the file picker.
4. Import the generated `.cape` into Mousecape.

The output is saved next to the source as `<source name> (自动生成).cape`.

The release build is ad-hoc signed, not notarized. macOS may require the first-launch **Open** confirmation or **Open Anyway** in Privacy & Security.

## Expected source files

The source must include all 15 of these PNG groups. The app searches subfolders in a ZIP or folder and ignores filename case; it also accepts common suffixes such as `Normal-Sheet.png` and `Text-Cursor.png`. Each image is a vertical sprite sheet made from square frames, for example `32×256` for eight `32×32` frames.

| | | |
|---|---|---|
| `Alternate.png` | `Busy.png` | `Diagonal1.png` |
| `Diagonal2.png` | `Handwriting.png` | `Help.png` |
| `Horizontal.png` | `Link.png` | `Move.png` |
| `Normal.png` | `Precision.png` | `Text.png` |
| `Unavailable.png` | `Vertical.png` | `Working.png` |

## Build from source

Requirements: macOS 15+, Xcode Command Line Tools, and Python 3 with Pillow.

```bash
python3 -m pip install -r requirements.txt
zsh scripts/build-app.sh
```

The app is built at `dist/Cursor Cape Builder.app`.

To create a GitHub Release attachment:

```bash
zsh scripts/package-release.sh
```

This writes `release/Cursor-Cape-Builder-macOS.zip`.

## Command-line usage

```bash
python3 src/CursorCapeBuilder.py /path/to/cursor-pack.zip /path/to/theme.cape \
  --name "My Cursor Theme" --author "Your Name"
```

## Notes

- The default mapping is geared toward modern Mousecape on macOS 15 and later.
- The default text-cursor hotspot is `(0, 9)` and resize/move hotspots are `(16, 16)` for 32px source artwork. Use `--template` with your own exported `.cape` if your artwork needs different hotspot rules.
- This project creates a Mousecape `.cape` file; it does not install or apply cursor themes for you.

## License

MIT. Cursor artwork is not included and remains subject to its original creator's license.
