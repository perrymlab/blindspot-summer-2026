# Python Environment Setup

Use Python 3.10 or newer.

This is the concise setup path for the project Python environment. The repository currently uses a local `.venv` by default. The official schedule mentions conda, so Sabrina may choose conda for the group, but the commands below are the supported repository default.

## Command Convention (Windows vs macOS/Linux)

Examples in this document and in the other setup docs are written using macOS/Linux paths. Translate as follows on Windows:

- Replace `python3` with `python` (Windows uses the `python` launcher, not `python3`).
- Replace `.venv/bin/python` with `.venv\Scripts\python.exe`.
- Forward slashes in arguments (e.g. `scripts/smoke_test.py`) work on Windows too, so only the interpreter path needs translation.

Example, macOS/Linux:

```bash
.venv/bin/python -m pytest
```

Same command on Windows (cmd or PowerShell):

```bat
.venv\Scripts\python.exe -m pytest
```

Alternatively, activate the virtual environment once per shell session and then use the bare `python` command everywhere:

- Windows cmd: `.venv\Scripts\activate.bat`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

## Recommended Setup

From the repository root:

```bash
python scripts/setup_repo.py
```

This does four things:

1. Creates `.venv`.
2. Upgrades `pip`.
3. Installs the local package and development test tools in editable mode.
4. Runs `scripts/smoke_test.py`.

It also clones and patches BoT-SORT into `vendor/BoT-SORT` unless you pass `--skip-bot-sort`.

## Local Setup Commands

```bash
python3 --version
python3 scripts/setup_repo.py
.venv/bin/python scripts/smoke_test.py
.venv/bin/python -m pytest
```

Run project commands through the virtual environment Python:

```bash
.venv/bin/python scripts/run_synthetic_experiment.py --out-dir runs/synthetic
```

If you only want the Python package setup without BoT-SORT:

```bash
python3 scripts/setup_repo.py --skip-bot-sort
```

## Conda Alternative

Use this only if Sabrina decides the group should follow the schedule's conda wording exactly.

```bash
conda create -n blindspot-summer-2026 python=3.10
conda activate blindspot-summer-2026
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/smoke_test.py
python -m pytest
```

Then set up BoT-SORT separately without creating `.venv`:

```bash
git clone https://github.com/NirAharon/BoT-SORT.git vendor/BoT-SORT
git -C vendor/BoT-SORT checkout -B prime-reid-poison-export origin/main
git -C vendor/BoT-SORT am patches/0001-Add-PRIME-ReID-poison-and-export-hooks.patch
```

Do not mix conda and `.venv` commands in the same terminal unless you know which Python executable is being used.

## Verify Setup

The smoke test should print:

```text
smoke tests passed
```

For real-data work, after dataset and weight paths exist:

```bash
python scripts/check_research_readiness.py --cityflow-root <path-to-CityFlowV2> --detector-weights <path-to-detector-weights> --reid-weights <path-to-reid-weights>
```

## Common Problems

If `numpy` or `pandas` is missing, run commands through `.venv` Python rather than the system Python.

If `pytest` is missing, rerun setup through the local virtual environment path:

```bash
python3 scripts/setup_repo.py --skip-bot-sort
```

If BoT-SORT setup fails, complete the Python setup first:

```bash
python scripts/setup_repo.py --skip-bot-sort
```

Then ask Sabrina for the BoT-SORT setup target and required model weights.
