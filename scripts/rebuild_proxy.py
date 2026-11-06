#!/usr/bin/env python3
"""Reproduce the shipped proxy from the exact upstream WGT, without npm resolution."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = 'd5ebcf5b61e907912d5200b033f0d366717cb952c9f543a6332d36bef771b3b5'

def rebuild(package, output):
    data = Path(package).read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED:
        raise ValueError('Official v2.1.1 WGT checksum mismatch; refusing to patch')
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / 'service/dist/index.js'
        target.parent.mkdir(parents=True)
        with zipfile.ZipFile(package) as archive:
            target.write_bytes(archive.read('service/dist/index.js'))
        for name, extra in [('patch_diag.py', ['Starter copy']), ('patch_fix.py', []), ('patch_privacy.py', [])]:
            subprocess.run([sys.executable, str(ROOT / 'scripts/patches' / name), directory, *extra], check=True)
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_bytes(target.read_bytes())

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python3 scripts/rebuild_proxy.py /path/to/TizenTubeCobalt.wgt')
    rebuild(sys.argv[1], ROOT / 'tizentube-handoff/source/service/dist/index.js')
