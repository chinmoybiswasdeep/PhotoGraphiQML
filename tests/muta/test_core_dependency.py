import os
import subprocess
import sys
from pathlib import Path


def test_core_without_mentpy_import():
    code = """
import importlib.abc
import sys
class BlockMentPy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'mentpy' or fullname.startswith('mentpy.'):
            raise ImportError('MentPy deliberately unavailable')
sys.meta_path.insert(0, BlockMentPy())
import photographiqml as p
assert p.MuTA(1).run([1,0]).probabilities[0] > 0.999
assert 'mentpy' not in sys.modules
"""
    source = str(Path(__file__).resolve().parents[2] / "src")
    environment = dict(os.environ, PYTHONPATH=source)
    subprocess.run([sys.executable, "-c", code], check=True, env=environment)
