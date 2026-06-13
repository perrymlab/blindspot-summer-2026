# ARCHIVED — superseded by scripts/pod_bootstrap.sh for GPU pod recovery.
# Run `bash scripts/pod_bootstrap.sh` to restore the pod environment instead.
# Kept here for reference; not part of any current workflow.
# See docs/CONSOLIDATION_PLAN.md §4a.

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def default_data_root() -> Path:
    """Resolve the project's default data root.

    Priority: ``BLINDSPOT_DATA_ROOT`` env var, then ``/workspace/blindspot_data``
    (the GPU box's persistent volume) if it exists, then ``~/blindspot_data``.
    Kept user-agnostic so no machine-specific paths leak into the repo.
    """
    env = os.environ.get("BLINDSPOT_DATA_ROOT")
    if env:
        return Path(env).expanduser()
    for candidate in (Path("/workspace/blindspot_data"), Path.home() / "blindspot_data"):
        if candidate.is_dir():
            return candidate
    return Path.home() / "blindspot_data"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether a machine is ready for PRIME real-data BoT-SORT "
        "runs. Run this inside the researcher 'botsort' conda env (Python 3.9)."
    )
    parser.add_argument(
        "--data-root",
        "--cityflow-root",
        dest="data_root",
        type=Path,
        default=default_data_root(),
        help="Dataset root containing scenario subfolders. "
        "Defaults to $BLINDSPOT_DATA_ROOT, else /workspace/blindspot_data if present, else ~/blindspot_data. "
        "(--cityflow-root is a deprecated alias kept for backward compatibility.)",
    )
    parser.add_argument("--detector-weights", type=Path, default=None)
    parser.add_argument("--reid-weights", type=Path, default=None)
    parser.add_argument("--bot-sort-path", type=Path, default=ROOT / "vendor" / "BoT-SORT")
    parser.add_argument("--require-scenarios", default="S01")
    parser.add_argument("--skip-pytorch", action="store_true")
    return parser.parse_args()


def check(condition: bool, label: str, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"[{status}] {label}{suffix}")
    return condition


def check_command(command: list[str], cwd: Path = ROOT) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except OSError as exc:
        return False, str(exc)
    output = result.stdout.strip().splitlines()
    detail = output[-1] if output else f"exit code {result.returncode}"
    return result.returncode == 0, detail


def scenario_exists(data_root: Path, scenario: str) -> bool:
    candidates = [
        data_root / scenario,
        data_root / scenario.lower(),
        data_root / scenario.upper(),
    ]
    return any(candidate.exists() for candidate in candidates)


def file_contains(path: Path, marker: str) -> bool:
    """Return True if ``path`` exists and contains ``marker``."""
    try:
        return marker in path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False


def main() -> int:
    args = parse_args()
    failures = 0

    failures += not check(
        sys.version_info[:2] == (3, 9),
        "Python 3.9 (required by BoT-SORT/FastReID)",
        f"{sys.version.split()[0]} - FastReID imports collections.Mapping, removed in 3.10; "
        "run inside the 'botsort' conda env",
    )
    failures += not check(shutil.which("git") is not None, "git executable available")

    package_ok, package_detail = check_command([sys.executable, "scripts/smoke_test.py"])
    failures += not check(package_ok, "project smoke test", package_detail)

    if not args.skip_pytorch:
        torch_ok, torch_detail = check_command(
            [sys.executable, "-c", "import torch; print(torch.__version__)"]
        )
        failures += not check(torch_ok, "PyTorch import", torch_detail)

    bot_sort_path = args.bot_sort_path
    failures += not check(bot_sort_path.exists(), "BoT-SORT checkout", str(bot_sort_path))
    if bot_sort_path.exists():
        branch_ok, branch_detail = check_command(
            ["git", "-C", str(bot_sort_path), "branch", "--show-current"]
        )
        failures += not check(branch_ok, "BoT-SORT branch readable", branch_detail)

        hook_path = bot_sort_path / "fast_reid" / "fast_reid_interfece.py"
        failures += not check(hook_path.exists(), "BoT-SORT ReID hook file", str(hook_path))

        # Existence is not enough: the unpatched upstream file has the same name.
        # Verify the PRIME patch actually applied by looking for symbols/flags it adds.
        demo_path = bot_sort_path / "tools" / "demo.py"
        failures += not check(
            file_contains(hook_path, "_export_prime_embeddings"),
            "PRIME patch applied (ReID export hook)",
            str(hook_path),
        )
        failures += not check(
            file_contains(demo_path, "--prime-export-embeddings"),
            "PRIME patch applied (demo flags)",
            str(demo_path),
        )

    failures += not check(
        args.data_root.exists(), "data root exists", str(args.data_root)
    )
    for scenario in [item.strip() for item in args.require_scenarios.split(",") if item.strip()]:
        failures += not check(
            scenario_exists(args.data_root, scenario),
            f"scenario {scenario}",
            str(args.data_root / scenario),
        )

    if args.detector_weights is None:
        failures += not check(False, "detector weights provided", "pass --detector-weights")
    else:
        failures += not check(args.detector_weights.exists(), "detector weights exist", str(args.detector_weights))

    if args.reid_weights is None:
        failures += not check(False, "FastReID/OSNet weights provided", "pass --reid-weights")
    else:
        failures += not check(args.reid_weights.exists(), "FastReID/OSNet weights exist", str(args.reid_weights))

    print()
    if failures:
        print(f"Readiness check failed: {failures} item(s) need attention.")
        return 1
    print("Readiness check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
