"""Put the tool folders on sys.path so tests can import them without installing anything."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL_DIRS = [
    os.path.join(ROOT, "skills", "clone-reviews", "tools"),
    os.path.join(ROOT, "skills", "clone-score", "tools"),
]
for path in TOOL_DIRS:
    if path not in sys.path:
        sys.path.insert(0, path)
