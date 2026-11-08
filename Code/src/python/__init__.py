import sys
from pathlib import Path
from dotenv import load_dotenv

_CURRENT_DIR = Path(__file__).resolve().parent
for _p in [str(_CURRENT_DIR), str(_CURRENT_DIR.parent), str(_CURRENT_DIR.parent.parent)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

load_dotenv()
