import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build', ROOT / 'tizentube-handoff/build.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

class BuildTest(unittest.TestCase):
    def test_identical_inputs_produce_identical_unsigned_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            one = build.build(Path(tmp) / 'one.wgt')
            two = build.build(Path(tmp) / 'two.wgt')
            self.assertEqual(one.read_bytes(), two.read_bytes())
            with zipfile.ZipFile(one) as archive:
                self.assertIn('service/dist/index.js', archive.namelist())
                self.assertNotIn('youtube-wordmark.svg', archive.namelist())
                self.assertFalse(any(n.endswith(('.key', '.p12', '.pfx')) for n in archive.namelist()))

if __name__ == '__main__':
    unittest.main()
