#!/usr/bin/env python3
"""Build the portable unsigned launcher; sign it for the destination TV at install time."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
FILES = (
    "config.xml", "index.html", "youtube.svg",
    "launcher-white-v209.png", "service/dist/index.js", "LICENSE", "ATTRIBUTION.md",
)

def build(output=None):
    config = ET.parse(SOURCE / "config.xml").getroot()
    version = config.attrib["version"]
    ns = {"w": "http://www.w3.org/ns/widgets"}
    for icon in config.findall("w:icon", ns):
        assert icon.attrib["src"] in FILES, "Missing packaged icon"
    ET.parse(SOURCE / "youtube.svg")
    out = Path(output) if output else ROOT / "packages" / f"TizenTubeStarter-{version}.wgt"
    out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(out, "w", ZIP_DEFLATED) as archive:
        for name in FILES:
            info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (SOURCE / name).read_bytes())
    print(out)
    return out

if __name__ == "__main__":
    build()
