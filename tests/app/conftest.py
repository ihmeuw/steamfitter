from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def configuration_with_patched_path(monkeypatch, tmpdir):
    monkeypatch.setattr("steamfitter.app.configuration.Configuration._path",
                        Path(tmpdir / "config.yaml"))

