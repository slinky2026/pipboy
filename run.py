import sys
from pathlib import Path
#literally just controls the run
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from pypboy.core import Pypboy


def main() -> None:
    Pypboy("Pip-Boy Prototype (Tabs)", 720, 720).run()


if __name__ == "__main__":
    main()
