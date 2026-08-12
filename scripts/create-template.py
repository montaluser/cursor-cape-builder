#!/usr/bin/env python3
"""Replace all embedded artwork in a .cape mapping template with transparent pixels."""

from io import BytesIO
from pathlib import Path
import plistlib
import sys

from PIL import Image


def transparent_tiff() -> bytes:
    image = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    output = BytesIO()
    image.save(output, format="TIFF", compression="tiff_lzw")
    return output.getvalue()


def main() -> None:
    template_path = Path(sys.argv[1])
    with template_path.open("rb") as stream:
        cape = plistlib.load(stream)
    blank = transparent_tiff()
    for cursor in cape["Cursors"].values():
        cursor["Representations"] = [blank]
    cape["CapeName"] = "Cursor Cape Builder Template"
    cape["Author"] = "Cursor Cape Builder"
    cape["Identifier"] = "local.cursorcapebuilder.template"
    with template_path.open("wb") as stream:
        plistlib.dump(cape, stream, fmt=plistlib.FMT_XML, sort_keys=False)


if __name__ == "__main__":
    main()
