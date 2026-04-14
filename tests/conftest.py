from __future__ import annotations

import sys
from pathlib import Path

API_APP_ROOT = Path(__file__).resolve().parents[1] / "apps" / "api"
api_app_root = str(API_APP_ROOT)
if api_app_root not in sys.path:
    sys.path.insert(0, api_app_root)
