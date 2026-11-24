from __future__ import annotations

import sys
from pathlib import Path

# Делаем исходники пакета видимыми для импорта.
_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from config_lang.__main__ import main  # noqa: E402


if __name__ == "__main__":
    main()
