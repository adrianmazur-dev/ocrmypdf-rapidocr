from __future__ import annotations

import hashlib
import re
import shutil
from pathlib import Path

import pytest

DEBUG_ROOT = Path(__file__).resolve().parent / "debug"


def _safe_test_dir_name(nodeid: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", nodeid).strip("._")
    digest = hashlib.sha1(nodeid.encode("utf-8")).hexdigest()[:8]
    return f"{sanitized}_{digest}"


@pytest.fixture(scope="session", autouse=True)
def _prepare_debug_root() -> Path:
    if DEBUG_ROOT.exists():
        shutil.rmtree(DEBUG_ROOT)
    DEBUG_ROOT.mkdir(parents=True, exist_ok=True)
    return DEBUG_ROOT


@pytest.fixture
def debug_output_dir(request: pytest.FixtureRequest, _prepare_debug_root: Path) -> Path:
    test_dir = _prepare_debug_root / _safe_test_dir_name(request.node.nodeid)
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir
