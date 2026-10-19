import shutil
from pathlib import Path

import pytest
from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
MARCO = ROOT / "contenido" / "marco"


class ProfileDir:
    """A writable copy of the real profile that tests can alter file by file."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._yaml = YAML(typ="safe")

    def read(self, name: str):
        return self._yaml.load((self.path / name).read_text(encoding="utf-8"))

    def write(self, name: str, data) -> None:
        yaml = YAML()
        yaml.default_flow_style = False
        with (self.path / name).open("w", encoding="utf-8") as fh:
            yaml.dump(data, fh)

    def edit(self, name: str, change) -> None:
        data = self.read(name)
        change(data)
        self.write(name, data)


@pytest.fixture
def profile_dir(tmp_path) -> ProfileDir:
    target = tmp_path / "marco"
    shutil.copytree(MARCO, target)
    return ProfileDir(target)
