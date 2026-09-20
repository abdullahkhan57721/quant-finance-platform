"""Execute every committed flagship notebook without writing outputs back to disk."""

from __future__ import annotations

import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient

_ROOT = Path(__file__).resolve().parents[1]
_NOTEBOOKS = _ROOT / "notebooks"


def main() -> None:
    """Execute notebooks top-to-bottom in memory using the declared Python kernel."""
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.chdir(_ROOT)
    paths = sorted(_NOTEBOOKS.glob("*.ipynb"))
    if not paths:
        raise SystemExit("No notebooks found")

    for path in paths:
        print(f"==> {path.relative_to(_ROOT)}")
        notebook = nbformat.read(path, as_version=4)
        NotebookClient(
            notebook,
            timeout=300,
            kernel_name="python3",
        ).execute()


if __name__ == "__main__":
    main()
