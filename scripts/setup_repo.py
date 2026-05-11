from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BOTSORT_URL = "https://github.com/NirAharon/BoT-SORT.git"
DEFAULT_BOTSORT_PATH = ROOT / "vendor" / "BoT-SORT"
PATCH_PATH = ROOT / "patches" / "0001-Add-PRIME-ReID-poison-and-export-hooks.patch"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Set up the Blindspot Summer 2026 repo.")
    parser.add_argument("--venv", default=".venv", help="Virtual environment path.")
    parser.add_argument("--bot-sort-url", default=DEFAULT_BOTSORT_URL)
    parser.add_argument("--bot-sort-path", default=str(DEFAULT_BOTSORT_PATH))
    parser.add_argument("--skip-bot-sort", action="store_true")
    parser.add_argument("--force", action="store_true", help="Recreate existing venv/vendor paths.")
    return parser.parse_args()


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def venv_python(venv_path: Path) -> Path:
    if os.name == "nt":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def recreate_path(path: Path, force: bool) -> None:
    if path.exists() and force:
        shutil.rmtree(path)


def setup_venv(venv_path: Path, force: bool) -> Path:
    recreate_path(venv_path, force)
    if not venv_path.exists():
        run([sys.executable, "-m", "venv", str(venv_path)])

    python = venv_python(venv_path)
    if not python.exists():
        raise RuntimeError(f"Could not find virtual environment Python at {python}")

    run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(python), "-m", "pip", "install", "-e", ".[dev]"])
    return python


def setup_botsort(bot_sort_url: str, bot_sort_path: Path, force: bool) -> None:
    recreate_path(bot_sort_path, force)
    if bot_sort_path.exists():
        print(f"BoT-SORT checkout already exists at {bot_sort_path}; leaving it unchanged.")
        print("Re-run with --force to recreate it from upstream and reapply the PRIME patch.")
        return

    bot_sort_path.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", bot_sort_url, str(bot_sort_path)])
    run(["git", "-C", str(bot_sort_path), "checkout", "-B", "prime-reid-poison-export", "origin/main"])
    run(["git", "-C", str(bot_sort_path), "am", str(PATCH_PATH)])


def main() -> None:
    args = parse_args()
    venv_path = (ROOT / args.venv).resolve()
    bot_sort_path = Path(args.bot_sort_path)
    if not bot_sort_path.is_absolute():
        bot_sort_path = (ROOT / bot_sort_path).resolve()

    python = setup_venv(venv_path, args.force)
    if not args.skip_bot_sort:
        setup_botsort(args.bot_sort_url, bot_sort_path, args.force)

    run([str(python), "scripts/smoke_test.py"])

    print()
    print("Setup complete.")
    print(f"Virtual environment: {venv_path}")
    print("Run project commands through that environment's Python executable.")


if __name__ == "__main__":
    main()
