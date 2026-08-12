#!/usr/bin/env python3
"""Build a Mousecape v2 .cape from a standard 15-image cursor pack.

Usage:
  python3 CursorCapeBuilder.py <source-folder-or-zip> <output.cape> [options]

The source must contain the 15 conventional PNG sprite sheets used by macOS packs.
Each image is a square cursor frame stacked vertically (for example 32x256).
"""

from __future__ import annotations

import argparse
import getpass
import io
import plistlib
import re
import sys
import zipfile
from copy import deepcopy
from pathlib import Path

try:
    from PIL import Image
except ModuleNotFoundError as error:
    raise SystemExit("需要 Pillow：请运行 python3 -m pip install Pillow") from error


# The 15 conventional cursor-image groups map to all 44 macOS cursor states.
# Text's hotspot is intentionally (0, 9) for pixel cursor themes.
GROUPS: dict[str, dict[str, object]] = {
    "Alternate": {"keys": ["com.apple.coregraphics.Alias"], "hotspot": (0, 0)},
    "Normal": {"keys": [
        "com.apple.coregraphics.Arrow", "com.apple.coregraphics.ArrowCtx",
        "com.apple.coregraphics.ArrowS", "com.apple.cursor.24",
    ], "hotspot": (0, 0)},
    "Busy": {"keys": [
        "com.apple.cursor.4", "com.apple.cursor.14", "com.apple.cursor.15", "com.apple.cursor.16",
    ], "hotspot": (0, 0)},
    "Handwriting": {"keys": ["com.apple.cursor.11", "com.apple.cursor.12"], "hotspot": (0, 0)},
    "Help": {"keys": ["com.apple.cursor.40"], "hotspot": (0, 0)},
    "Horizontal": {"keys": [
        "com.apple.cursor.17", "com.apple.cursor.18", "com.apple.cursor.19",
        "com.apple.cursor.27", "com.apple.cursor.28", "com.apple.cursor.38",
    ], "hotspot": (16, 16)},
    "Link": {"keys": ["com.apple.cursor.2", "com.apple.cursor.13"], "hotspot": (0, 0)},
    "Move": {"keys": ["com.apple.coregraphics.Move", "com.apple.cursor.39"], "hotspot": (16, 16)},
    "Precision": {"keys": [
        "com.apple.cursor.7", "com.apple.cursor.8", "com.apple.cursor.20", "com.apple.cursor.41",
    ], "hotspot": (0, 0)},
    "Text": {"keys": [
        "com.apple.coregraphics.IBeam", "com.apple.coregraphics.IBeamS",
        "com.apple.coregraphics.IBeamXOR", "com.apple.cursor.26",
    ], "hotspot": (0, 9)},
    "Unavailable": {"keys": ["com.apple.cursor.3"], "hotspot": (0, 0)},
    "Vertical": {"keys": [
        "com.apple.cursor.21", "com.apple.cursor.22", "com.apple.cursor.23",
        "com.apple.cursor.31", "com.apple.cursor.32", "com.apple.cursor.36",
    ], "hotspot": (16, 16)},
    "Working": {"keys": ["com.apple.coregraphics.Wait"], "hotspot": (0, 0)},
    "Diagonal1": {"keys": ["com.apple.cursor.33", "com.apple.cursor.34", "com.apple.cursor.35"], "hotspot": (16, 16)},
    "Diagonal2": {"keys": ["com.apple.cursor.29", "com.apple.cursor.30", "com.apple.cursor.37"], "hotspot": (16, 16)},
}


def normalized_stem(value: str) -> str:
    """Match common pack labels such as `Normal-Sheet.png` to `Normal`.

    Only suffix words are removed, so a file does not get classified by a
    coincidental word in the middle of its name.
    """
    stem = Path(value).stem.casefold()
    stem = re.sub(r"(?:[-_\s]+(?:sheet|spritesheet|sprite|frames?|cursor|pointer|mouse))+$", "", stem)
    return re.sub(r"[^a-z0-9]+", "", stem)


def image_entries(source: Path) -> list[str]:
    if source.is_dir():
        return [str(path.relative_to(source)) for path in source.rglob("*")
                if path.is_file() and path.suffix.casefold() == ".png"]
    if source.is_file() and source.suffix.casefold() == ".zip":
        with zipfile.ZipFile(source) as archive:
            return [name for name in archive.namelist()
                    if not name.endswith("/") and Path(name).suffix.casefold() == ".png"]
    raise ValueError("源路径必须是图片文件夹或 .zip 压缩包")


def resolve_source_entries(source: Path) -> dict[str, str]:
    """Find exactly one sprite image for every conventional asset group."""
    entries = image_entries(source)
    matches: dict[str, list[tuple[int, str]]] = {name: [] for name in GROUPS}
    for entry in entries:
        filename = Path(entry).name
        for asset_name in GROUPS:
            if normalized_stem(filename) != normalized_stem(asset_name):
                continue
            score = 2 if Path(filename).stem.casefold() == asset_name.casefold() else 1
            matches[asset_name].append((score, entry))

    resolved: dict[str, str] = {}
    for asset_name, candidates in matches.items():
        if not candidates:
            continue
        best_score = max(score for score, _entry in candidates)
        best = [entry for score, entry in candidates if score == best_score]
        if len(best) > 1:
            listed = "、".join(sorted(best))
            raise ValueError(f"{asset_name} 匹配到多张图片，无法自动判断：{listed}")
        resolved[asset_name] = best[0]

    missing = [f"{name}.png" for name in GROUPS if name not in resolved]
    if missing:
        available = "、".join(sorted(entries)) or "（未找到 PNG 图片）"
        raise FileNotFoundError(
            f"缺少：{'、'.join(missing)}。已找到的 PNG：{available}"
        )
    return resolved


def read_source(source: Path, entry: str) -> bytes:
    if source.is_dir():
        return (source / entry).read_bytes()
    with zipfile.ZipFile(source) as archive:
        return archive.read(entry)


def sprite_to_tiff(payload: bytes, name: str) -> tuple[bytes, int, int, int]:
    with Image.open(io.BytesIO(payload)) as source:
        image = source.convert("RGBA")
        width, height = image.size
        if width != height // (height // width) or height % width:
            raise ValueError(f"{name} 必须是纵向叠放的正方形帧，当前为 {width}×{height}")
        frame_count = height // width
        if not 1 <= frame_count <= 24:
            raise ValueError(f"{name} 有 {frame_count} 帧；Mousecape 最多支持 24 帧")
        output = io.BytesIO()
        image.save(output, format="TIFF", compression="tiff_lzw")
        return output.getvalue(), width, height, frame_count


def make_identifier(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "", value.lower()) or "cursorcape"
    author = re.sub(r"[^a-z0-9]+", "", getpass.getuser().lower()) or "user"
    return f"local.{author}.{slug}"


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="从 15 张指针帧图自动生成 Mousecape .cape")
    parser.add_argument("source", type=Path, help="含 15 张 PNG 的文件夹，或原始 ZIP 文件")
    parser.add_argument("output", type=Path, help="要生成的 .cape 路径")
    parser.add_argument("--template", type=Path, default=root / "CursorCapeBuilder.template.cape",
                        help="已验证的 Mousecape 模板（默认使用随工具附带的模板）")
    parser.add_argument("--name", default="Custom Cursor Theme", help="主题名称")
    parser.add_argument("--author", default=getpass.getuser(), help="作者名")
    parser.add_argument("--identifier", help="唯一标识符；默认由主题名生成")
    parser.add_argument("--cycle-duration", type=float, default=0.8,
                        help="每个动画完成一轮的秒数，默认 0.8")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.cycle_duration <= 0:
        raise SystemExit("--cycle-duration 必须大于 0")
    if not args.template.is_file():
        raise SystemExit(f"找不到模板：{args.template}")

    with args.template.open("rb") as stream:
        cape = deepcopy(plistlib.load(stream))
    cursors = cape.get("Cursors")
    if not isinstance(cursors, dict):
        raise SystemExit("模板不是有效的 Mousecape .cape 文件")

    source_entries = resolve_source_entries(args.source)
    for asset_name, group in GROUPS.items():
        entry = source_entries[asset_name]
        payload = read_source(args.source, entry)
        image_data, width, _height, frames = sprite_to_tiff(payload, entry)
        hotspot_x, hotspot_y = group["hotspot"]
        scale = width / 32.0
        for key in group["keys"]:
            if key not in cursors:
                raise SystemExit(f"模板缺少系统光标映射：{key}")
            cursor = cursors[key]
            cursor["Representations"] = [image_data]
            cursor["FrameCount"] = frames
            cursor["FrameDuration"] = args.cycle_duration / frames
            cursor["PointsWide"] = float(width)
            cursor["PointsHigh"] = float(width)
            cursor["HotSpotX"] = float(hotspot_x * scale)
            cursor["HotSpotY"] = float(hotspot_y * scale)

    cape["Author"] = args.author
    cape["CapeName"] = args.name
    cape["CapeVersion"] = 1.0
    cape["Identifier"] = args.identifier or make_identifier(args.name)
    cape["Version"] = 2.0
    cape["MinimumVersion"] = 2.0
    cape["Cloud"] = False
    cape["HiDPI"] = False

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("wb") as stream:
        plistlib.dump(cape, stream, fmt=plistlib.FMT_XML, sort_keys=False)
    print(f"已生成：{args.output}")
    print(f"主题：{args.name}；15 套动画映射至 {len(cursors)} 个 macOS 光标状态。")


if __name__ == "__main__":
    main()
