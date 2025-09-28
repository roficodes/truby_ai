import sys
from pathlib import Path


# Ensure the `app/` package is on sys.path so modules using top-level imports
# like `from core.config import ...` resolve during tests.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
