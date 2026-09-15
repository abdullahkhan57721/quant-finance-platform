from __future__ import annotations

import subprocess
import sys
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[1]


def test_v01_release_check_passes_against_committed_evidence() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/v01_release_check.py"],
        cwd=_REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "v0.1.0 release verification passed" in completed.stdout
    assert "M7: 10 training / 4 held-out" in completed.stdout
    assert "C++ added: no" in completed.stdout
