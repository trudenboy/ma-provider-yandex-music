"""Tests for the working-tree provider aliasing performed in conftest."""

from __future__ import annotations

import sys
import types
from pathlib import Path

_PROVIDER_PKG = "music_assistant.providers.yandex_music"


def _conftest_module() -> types.ModuleType:
    """Return the already-imported conftest module that sits next to this file."""
    conftest_path = Path(__file__).resolve().parent / "conftest.py"
    for module in list(sys.modules.values()):
        module_file = getattr(module, "__file__", None)
        if module_file and Path(module_file).resolve() == conftest_path:
            return module
    raise AssertionError(f"conftest module for {conftest_path} is not loaded")


def test_aliasing_is_noop_without_provider_working_tree(tmp_path: Path) -> None:
    """
    Skip aliasing when the ``provider/`` working tree does not exist.

    That is the upstream repo layout: the aliasing must silently no-op there
    instead of crashing test collection.
    """
    conftest = _conftest_module()
    before = sys.modules.get(_PROVIDER_PKG)

    conftest._alias_working_tree_provider(tmp_path / "provider")

    assert sys.modules.get(_PROVIDER_PKG) is before
