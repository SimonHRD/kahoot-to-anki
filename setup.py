from pathlib import Path

from setuptools import setup


def read_version():
    version_path = Path(__file__).parent / "kahoot_to_anki" / "_version.py"
    version_line = next(line for line in version_path.read_text().splitlines() if "__version__" in line)
    return version_line.split("=")[1].strip().strip('"')

setup(
    version=read_version()
)