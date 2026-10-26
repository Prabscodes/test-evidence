"""Compatibility entrypoint for the current structural workflow acceptance test.
The preceding one-page UI test is preserved in commit03abeeb and its evidence.
"""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('workflow-browser.py')),run_name='__main__')
