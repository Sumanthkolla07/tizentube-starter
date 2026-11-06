#!/usr/bin/env python3
"""Create a share kit from an explicit subset of Git-tracked project files."""
import hashlib
from pathlib import Path
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
WIDGET_VERSION = ET.parse(ROOT / 'tizentube-handoff/source/config.xml').getroot().attrib['version']
VERSION = f'v{WIDGET_VERSION}-rc.1'
ROOT_FILES = {'README.md', 'LICENSE', 'ATTRIBUTION.md', 'SECURITY.md', 'CONTRIBUTING.md', 'CHANGELOG.md', '.gitignore'}
PREFIXES = ('docs/', 'scripts/', 'tests/', 'vendor/', '.github/', 'tizentube-handoff/source/')

def make_kit():
    dist = ROOT / 'dist' / VERSION
    dist.mkdir(parents=True, exist_ok=True)
    package = dist / f'TizenTubeStarter-{WIDGET_VERSION}.wgt'
    subprocess.run([sys.executable, str(ROOT / 'tizentube-handoff/build.py')], check=True)
    package.write_bytes((ROOT / 'tizentube-handoff/packages' / package.name).read_bytes())
    tracked = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-z']).decode().split('\0')
    selected = sorted(p for p in tracked if p and (p in ROOT_FILES or p.startswith(PREFIXES) or p == 'tizentube-handoff/build.py'))
    contents = {p: (ROOT / p).read_bytes() for p in selected}
    contents['packages/' + package.name] = package.read_bytes()
    manifest = ''.join(hashlib.sha256(data).hexdigest() + '  ' + name + '\n' for name, data in sorted(contents.items()))
    contents['SOURCE_SHA256SUMS.txt'] = manifest.encode()
    kit = dist / f'TizenTube-Starter-Community-Kit-{VERSION}.zip'
    with zipfile.ZipFile(kit, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(contents.items()):
            info = zipfile.ZipInfo('tizentube-starter/' + name, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    sums = dist / 'SHA256SUMS.txt'
    sums.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n' for p in (package, kit)))
    print(kit)
    return kit

if __name__ == '__main__':
    make_kit()
