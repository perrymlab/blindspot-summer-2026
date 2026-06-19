#!/usr/bin/env bash
# Read-only diagnostic for the RunPod GPU box.
#
# Purpose: when the Python environment situation gets confusing (e.g. after a
# pod restart, or several conda/venv installs piled up), this prints a complete
# inventory of every Python interpreter, conda installation, conda env, and
# virtualenv on the box, plus where the repo / weights / disk usage stand.
#
# It is SAFE: it only reads and prints. It never installs, activates, deletes,
# or modifies anything. Run it, then paste the whole output back to Cascade.
#
# Usage:
#   bash scripts/diagnose_pod.sh                 # print to screen
#   bash scripts/diagnose_pod.sh | tee /workspace/pod_diag.txt   # + save a copy
#
# Expected baseline (see docs/setup/RECOVERY.md, RUNPOD_RESUME.md):
#   repo    : /workspace/blindspot-summer-2026
#   conda   : /workspace/miniforge3   (persistent, on the network volume)
#   env     : botsort  (Python 3.9)   -> used to RUN BoT-SORT
#   .venv   : repo/.venv (Python 3.10+) -> used for CSV analysis only

# No 'set -e': a diagnostic must finish even when probed things are missing.
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)"
EXPECTED_REPO="/workspace/blindspot-summer-2026"
EXPECTED_CONDA="/workspace/miniforge3"

hr()      { printf '\n========== %s ==========\n' "$*"; }
sub()     { printf '\n--- %s ---\n' "$*"; }
have()    { command -v "$1" >/dev/null 2>&1; }
note()    { printf '   %s\n' "$*"; }

# Probe a single python interpreter: version, prefix, and key packages.
probe_python() {
    local py="$1"
    [ -x "$py" ] || { note "MISSING/!exec: $py"; return; }
    printf '\n   [%s]\n' "$py"
    "$py" - <<'PYEOF' 2>&1 | sed 's/^/      /'
import sys, os
print("version :", sys.version.split()[0])
print("prefix  :", sys.prefix)
print("base    :", getattr(sys, "base_prefix", sys.prefix))
in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
print("in venv :", in_venv)
pkgs = ["torch", "torchvision", "numpy", "scipy", "cython_bbox",
        "lap", "cv2", "pandas", "sklearn", "matplotlib", "onnxruntime"]
try:
    import importlib.metadata as md
except Exception:
    md = None
def ver(name):
    try:
        m = __import__(name)
    except Exception as e:
        return "-- (%s)" % type(e).__name__
    v = getattr(m, "__version__", None)
    if v:
        return v
    if md:
        try:
            return md.version(name)
        except Exception:
            pass
    return "installed (no __version__)"
for p in pkgs:
    print("  %-12s: %s" % (p, ver(p)))
PYEOF
}

hr "POD DIAGNOSTIC  ($(date 2>/dev/null))"
note "host    : $(hostname 2>/dev/null)"
note "user    : $(whoami 2>/dev/null)"
note "shell   : ${SHELL:-?}   (running under: $0)"
note "uname   : $(uname -a 2>/dev/null)"
note "pwd     : $(pwd)"

hr "ACTIVE ENVIRONMENT (what THIS shell would use)"
note "PATH            : ${PATH}"
note "VIRTUAL_ENV     : ${VIRTUAL_ENV:-<unset>}"
note "CONDA_PREFIX    : ${CONDA_PREFIX:-<unset>}"
note "CONDA_DEFAULT_ENV: ${CONDA_DEFAULT_ENV:-<unset>}"
note "PYENV_VERSION   : ${PYENV_VERSION:-<unset>}"
sub "what 'python' / 'python3' resolve to right now"
for cmd in python python3 pip pip3 conda; do
    if have "$cmd"; then
        note "$cmd -> $(command -v "$cmd")"
    else
        note "$cmd -> <not on PATH>"
    fi
done

hr "ALL python INTERPRETERS ON PATH"
# 'which -a' shows shadowing order; the first one wins.
which -a python python3 2>/dev/null | sed 's/^/   /' || note "none found"

hr "CONDA INSTALLATIONS FOUND ON DISK"
# Look for every conda binary in the usual roots (duplicate installs are the
# most common cause of confusion).
CONDA_ROOTS="/workspace/miniforge3 /workspace/miniconda3 /opt/conda \
$HOME/miniconda3 $HOME/miniforge3 $HOME/anaconda3 /root/miniconda3 \
/root/miniforge3 /usr/local/miniconda3"
found_conda=0
for root in $CONDA_ROOTS; do
    if [ -x "$root/bin/conda" ]; then
        found_conda=1
        ver="$("$root/bin/conda" --version 2>/dev/null)"
        note "FOUND: $root/bin/conda   ($ver)"
    fi
done
[ "$found_conda" -eq 0 ] && note "no conda installs found in the usual locations"

sub "conda env list (per conda install found)"
for root in $CONDA_ROOTS; do
    if [ -x "$root/bin/conda" ]; then
        printf '\n   # %s\n' "$root/bin/conda env list"
        "$root/bin/conda" env list 2>&1 | sed 's/^/      /'
    fi
done

sub "conda env directories on disk (with sizes)"
for root in $CONDA_ROOTS; do
    if [ -d "$root/envs" ]; then
        printf '\n   # %s/envs\n' "$root"
        du -sh "$root/envs"/* 2>/dev/null | sed 's/^/      /' || note "   (empty)"
    fi
done

hr "VIRTUALENVS (pyvenv.cfg) under repo, /workspace, and \$HOME"
# Bounded depth so this stays fast. A pyvenv.cfg marks a python -m venv.
for base in "$REPO_ROOT" /workspace "$HOME"; do
    [ -d "$base" ] || continue
    printf '\n   # under %s (maxdepth 4)\n' "$base"
    find "$base" -maxdepth 4 -name pyvenv.cfg 2>/dev/null \
        | sed 's/^/      /' || true
done

hr "INTERPRETER PROBES (version + key packages, no activation)"
# De-duplicate the set of pythons worth probing.
CANDIDATES=""
add_candidate() { case " $CANDIDATES " in *" $1 "*) ;; *) CANDIDATES="$CANDIDATES $1";; esac; }
# PATH pythons
for p in $(which -a python python3 2>/dev/null); do add_candidate "$p"; done
# active env / known roots
[ -n "${CONDA_PREFIX:-}" ] && add_candidate "$CONDA_PREFIX/bin/python"
[ -n "${VIRTUAL_ENV:-}" ]  && add_candidate "$VIRTUAL_ENV/bin/python"
add_candidate "$EXPECTED_CONDA/bin/python"
add_candidate "$EXPECTED_CONDA/envs/botsort/bin/python"
add_candidate "$REPO_ROOT/.venv/bin/python"
for root in $CONDA_ROOTS; do
    for envpy in "$root"/envs/*/bin/python; do
        [ -x "$envpy" ] && add_candidate "$envpy"
    done
done
for py in $CANDIDATES; do probe_python "$py"; done

hr "EXPECTED 'botsort' ENV CHECK"
BOTSORT_PY="$EXPECTED_CONDA/envs/botsort/bin/python"
if [ -x "$BOTSORT_PY" ]; then
    v="$("$BOTSORT_PY" -c 'import sys;print(sys.version.split()[0])' 2>/dev/null)"
    note "OK   $BOTSORT_PY  (Python $v)"
    case "$v" in
        3.9*) note "OK   version is 3.9.x as required" ;;
        "")   note "WARN could not read version" ;;
        *)    note "WARN expected 3.9.x for BoT-SORT/FastReID, got $v" ;;
    esac
else
    note "MISSING: $BOTSORT_PY  -> botsort env not where it should be"
    note "         (see docs/setup/RECOVERY.md to rebuild it)"
fi

hr "REPO + GIT STATE"
note "this script's repo : $REPO_ROOT"
if [ "$REPO_ROOT" != "$EXPECTED_REPO" ]; then
    note "NOTE repo is not at the expected $EXPECTED_REPO"
fi
if have git && [ -d "$REPO_ROOT/.git" ]; then
    note "branch : $(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null)"
    note "commit : $(git -C "$REPO_ROOT" log -1 --oneline 2>/dev/null)"
    note "remote : $(git -C "$REPO_ROOT" config --get remote.origin.url 2>/dev/null)"
    sub "git status (short)"
    git -C "$REPO_ROOT" status -sb 2>&1 | sed 's/^/   /'
else
    note "no git repo detected at $REPO_ROOT"
fi

hr "KEY PATHS / WEIGHTS"
for p in "vendor/BoT-SORT" "vendor/BoT-SORT/pretrained" "data" "runs"; do
    if [ -e "$REPO_ROOT/$p" ]; then note "ok      $p"; else note "MISSING $p"; fi
done
if [ -d "$REPO_ROOT/vendor/BoT-SORT/pretrained" ]; then
    sub "pretrained/ contents"
    ls -lh "$REPO_ROOT/vendor/BoT-SORT/pretrained" 2>/dev/null | sed 's/^/   /'
fi

hr "DISK USAGE"
sub "filesystems"
df -h / /workspace 2>/dev/null | sed 's/^/   /'
sub "big directories (may take a few seconds)"
for d in "$EXPECTED_CONDA" "$REPO_ROOT/.venv" "$REPO_ROOT/vendor" \
         "$REPO_ROOT/runs" "$REPO_ROOT/data" "$HOME/annotation"; do
    [ -e "$d" ] && du -sh "$d" 2>/dev/null | sed 's/^/   /'
done

hr "SHELL INIT FILES (conda hookups / duplicates)"
for f in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile"; do
    if [ -f "$f" ]; then
        sub "$f  (conda/venv/path lines)"
        grep -nE 'conda|miniforge|miniconda|VIRTUAL_ENV|/venv|activate|PATH=' "$f" \
            2>/dev/null | sed 's/^/   /' || note "   (no matching lines)"
    fi
done

hr "DONE"
note "Copy this entire output and paste it back to Cascade."
note "Nothing above changed the system; it was all read-only."
