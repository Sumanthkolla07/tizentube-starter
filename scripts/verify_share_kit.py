#!/usr/bin/env python3
"""Verify the share manifest and rebuild its unsigned WGT in a clean directory."""
import hashlib
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import zipfile
from make_share_kit import ROOT, VERSION, WIDGET_VERSION


def verify(kit):
    prefix = 'tizentube-starter/'
    package = f'TizenTubeStarter-{WIDGET_VERSION}.wgt'
    with zipfile.ZipFile(kit) as archive:
        if archive.testzip() is not None:
            raise ValueError('ZIP integrity failure')
        names = archive.namelist()
        for name in names:
            if not name.startswith(prefix) or '..' in PurePosixPath(name).parts or '\\' in name:
                raise ValueError('Unsafe archive path: ' + name)
        manifest = archive.read(prefix + 'SOURCE_SHA256SUMS.txt').decode()
        expected_names = {prefix + 'SOURCE_SHA256SUMS.txt'}
        for line in manifest.splitlines():
            expected, name = line.split('  ', 1)
            expected_names.add(prefix + name)
            actual = hashlib.sha256(archive.read(prefix + name)).hexdigest()
            if actual != expected:
                raise ValueError('Manifest mismatch: ' + name)
        if len(names) != len(expected_names) or set(names) != expected_names:
            raise ValueError('Archive contains missing, duplicate or unmanifested entries')
        with tempfile.TemporaryDirectory() as directory:
            archive.extractall(directory)
            checkout = Path(directory) / 'tizentube-starter'
            subprocess.run([sys.executable, 'tizentube-handoff/build.py'], cwd=checkout, check=True)
            if (checkout / 'packages' / package).read_bytes() != (checkout / 'tizentube-handoff/packages' / package).read_bytes():
                raise ValueError('Clean rebuild differs from the bundled unsigned WGT')
    print('Share-kit manifest and byte-identical clean rebuild verified.')


if __name__ == '__main__':
    kit = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'dist' / VERSION / f'TizenTube-Starter-Community-Kit-{VERSION}.zip'
    verify(kit)
