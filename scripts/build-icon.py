#!/usr/bin/env python3
"""Create the Cursor Cape Builder app-icon PNG without external assets."""

from pathlib import Path
import struct
import sys

from PIL import Image, ImageDraw, ImageFilter


SIZE = 1024


def vertical_gradient(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", (SIZE, SIZE))
    pixels = image.load()
    for y in range(SIZE):
        ratio = y / (SIZE - 1)
        color = tuple(round(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        for x in range(SIZE):
            pixels[x, y] = color
    return image.convert("RGBA")


def build_png(destination: Path) -> None:
    destination = Path(sys.argv[1])
    image = vertical_gradient((23, 37, 84), (15, 23, 42))
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle((44, 44, 980, 980), radius=220, fill=255)
    image.putalpha(mask)

    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((678, 126, 902, 350), fill=(34, 211, 238, 28))
    draw.ellipse((86, 660, 386, 960), fill=(139, 92, 246, 28))

    shadow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((330, 286, 716, 746), radius=76, fill=(2, 6, 23, 170))
    shadow = shadow.filter(ImageFilter.GaussianBlur(22))
    image.alpha_composite(shadow, (0, 24))

    card = vertical_gradient((167, 139, 250), (109, 40, 217))
    card_mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(card_mask).rounded_rectangle((330, 286, 716, 746), radius=76, fill=255)
    card.putalpha(card_mask)
    image.alpha_composite(card)
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rounded_rectangle((372, 334, 674, 372), radius=19, fill=(237, 233, 254, 205))
    for box, color in [
        ((372, 410, 486, 524), (237, 233, 254, 245)),
        ((560, 410, 674, 524), (196, 181, 253, 205)),
        ((372, 562, 486, 676), (196, 181, 253, 205)),
        ((560, 562, 674, 676), (237, 233, 254, 245)),
    ]:
        draw.rounded_rectangle(box, radius=24, fill=color)

    pointer = [(179, 152), (179, 668), (331, 531), (429, 785), (530, 742), (427, 494), (649, 480)]
    draw.polygon(pointer, fill=(15, 23, 42, 255), outline=(15, 23, 42, 255), width=34)
    inset = [(198, 182), (198, 620), (337, 495), (435, 746), (504, 718), (400, 471), (603, 458)]
    draw.polygon(inset, fill=(248, 250, 252, 255))
    draw.line([(198, 182), (198, 620), (337, 495), (435, 746)], fill=(103, 232, 249, 230), width=16, joint="curve")

    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "PNG")


def build_icns(png_path: Path, icns_path: Path) -> None:
    """Write a modern ICNS file containing a 1024px PNG as its ic10 chunk."""
    payload = png_path.read_bytes()
    chunk = b"ic10" + struct.pack(">I", len(payload) + 8) + payload
    icns_path.write_bytes(b"icns" + struct.pack(">I", len(chunk) + 8) + chunk)


if __name__ == "__main__":
    png_destination = Path(sys.argv[1])
    build_png(png_destination)
    if len(sys.argv) == 3:
        build_icns(png_destination, Path(sys.argv[2]))
