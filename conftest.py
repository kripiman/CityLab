"""conftest.py — Pytest session configuration and test isolation."""
from __future__ import annotations

import os
import tempfile

# Isolate default historian DB path before scada_server import
_TEMP_HISTORIAN_DIR = tempfile.TemporaryDirectory(prefix="citylab_test_session_")
os.environ.setdefault("HISTORIAN_DB_PATH", os.path.join(_TEMP_HISTORIAN_DIR.name, "session_historian.db"))


def pytest_sessionfinish(session, exitstatus):
    """Clean up the temporary historian session directory."""
    _TEMP_HISTORIAN_DIR.cleanup()
