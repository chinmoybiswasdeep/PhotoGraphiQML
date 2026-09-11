import json
from pathlib import Path

import photographiq as pg
import pytest

from photographiqml import MuTA, PhysicalMuTA
from photographiqml.lowering import REQUIRED_API, check_photographiq_contract


def test_public_contract_and_dependency(monkeypatch):
    assert all(hasattr(pg, name) for name in REQUIRED_API)
    assert check_photographiq_contract()["version"] == "0.3.1"
    import tomllib

    data = tomllib.loads(Path("pyproject.toml").read_text())
    assert "photographiq>=0.3.1,<0.4" in data["project"]["dependencies"]
    monkeypatch.delattr(pg, "LogicalPauliFrame")
    with pytest.raises(ImportError, match="0.3.1"):
        check_photographiq_contract()


def test_physical_schema_and_legacy_migration(tmp_path):
    path = tmp_path / "model.json"
    model = PhysicalMuTA()
    model.freeze("alpha.w0.c0", 0)
    model.save(path)
    loaded = MuTA.load(path)
    assert isinstance(loaded, PhysicalMuTA)
    assert loaded.state_dict() == model.state_dict()
    with pytest.warns(DeprecationWarning):
        old = MuTA(1, representation="gkp")
    old.save(path)
    with pytest.warns(DeprecationWarning):
        legacy = PhysicalMuTA.load(path)
    assert legacy.representation == "gkp"
    assert not isinstance(legacy, PhysicalMuTA)
    with pytest.raises(NotImplementedError):
        legacy.run([1, 0])
    data = json.loads(path.read_text())
    data["schema"] = 99
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="schema"):
        MuTA.load(path)
