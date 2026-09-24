"""Assemble one self-contained notebook from the experiment scripts themselves.

Reads every `NN_category/MM_name.py` script, turns its module docstring
into a markdown cell (title = first line, body = the rest) and its source
into a code cell, and writes
`PhotoGraphiQML_Manuscript_Experiments.ipynb`. No separate, hand-maintained
notebook content exists; this script is the single source of truth for the
notebook.
"""

import re
import sys
from pathlib import Path

import nbformat as nbf
from publication import atomic_write_text

ROOT = Path(__file__).resolve().parent
NOTEBOOK_PATH = ROOT / "PhotoGraphiQML_Manuscript_Experiments.ipynb"

DOCSTRING_RE = re.compile(r'^"""(?P<title>[^\n]*)\n\n(?P<body>.*?)\n"""', re.DOTALL)
SYS_PATH_LINE_RE = re.compile(
    r"^sys\.path\.insert\(0, str\(Path\(__file__\)\.resolve\(\)\.parents\[1\]\)\)\n", re.MULTILINE
)


def guard_optional_dependency(source):
    """Wrap a bare `sys.exit(0)` so one missing optional dependency does not
    kill the shared-kernel notebook run (none of this suite's scripts use
    this pattern today, but build_notebook.py supports it for forward
    compatibility with future optional-dependency scripts)."""
    if "sys.exit(0)" not in source:
        return source
    return source.replace("sys.exit(0)", "raise SystemExit(0)")


def script_cells(path):
    source = path.read_text(encoding="utf-8")
    match = DOCSTRING_RE.search(source)
    title = match.group("title").strip() if match else path.stem
    body = match.group("body").strip() if match else ""
    code = SYS_PATH_LINE_RE.sub("", source)
    code = code.replace(
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1]))",
        f'sys.path.insert(0, str(Path.cwd() if (Path.cwd() / "common.py").exists() else Path("{ROOT.as_posix()}")))',
    )
    code = guard_optional_dependency(code)
    markdown = f"## {title}\n\n{body}"
    return [nbf.v4.new_markdown_cell(markdown), nbf.v4.new_code_cell(code)]


def main():
    nb = nbf.v4.new_notebook()
    cells = [
        nbf.v4.new_markdown_cell(
            "# PhotoGraphiQML manuscript experiment suite\n\n"
            "Self-contained notebook assembled directly from the scripts in "
            "`paper_experiments/`. Each section below is one experiment "
            "(R1-R48, R_PERF, and R50-R59): its scientific "
            "question, theory, oracle class and acceptance condition are in "
            "the markdown cell (from the script's own docstring); running "
            "the code cell reproduces its figures, CSV/JSON and metadata."
        ),
        nbf.v4.new_markdown_cell(
            "## Install dependencies\n\n"
            "Installs this repository (editable) with its `dev`/`experiments` "
            "extras, plus `photographiq`, `mentpy` and `piquasso` if not "
            "already present. Skip this cell if your environment (e.g. the "
            "project `.venv`) already has them installed."
        ),
        nbf.v4.new_code_cell(
            "import importlib.util, subprocess, sys\n"
            "if importlib.util.find_spec('ensurepip') is not None:\n"
            "    pass\n"
            "for pkg in ('photographiqml', 'photographiq', 'mentpy', 'piquasso', 'matplotlib', 'scikit-learn'):\n"
            "    if importlib.util.find_spec(pkg.replace('-', '_')) is None:\n"
            "        subprocess.run([sys.executable, '-m', 'pip', 'install', pkg], check=False)\n"
        ),
        nbf.v4.new_markdown_cell(
            "## Setup\n\nImports the shared `common`/`metadata` utilities, "
            "falling back to this notebook's own directory if the working "
            "directory changes between cells."
        ),
        nbf.v4.new_code_cell(
            "import sys\n"
            "from pathlib import Path\n"
            "for candidate in (Path.cwd(), Path.cwd() / 'paper_experiments'):\n"
            "    if (candidate / 'common.py').exists():\n"
            "        sys.path.insert(0, str(candidate))\n"
            "        break\n"
            "import common, metadata\n"
            "print(metadata.collect())\n"
        ),
    ]

    for script in sorted(ROOT.glob("*/*.py")):
        cells.extend(script_cells(script))

    cells.append(
        nbf.v4.new_markdown_cell(
            "## Aggregate manuscript tables\n\nRebuilds `tables/` from the saved results above."
        )
    )
    cells.append(nbf.v4.new_code_cell("import generate_tables\ngenerate_tables.main()\n"))

    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": sys.version.split()[0]},
    }
    nbf.validate(nb)
    atomic_write_text(NOTEBOOK_PATH, nbf.writes(nb))
    print(f"Wrote {NOTEBOOK_PATH} ({len(cells)} cells)")


if __name__ == "__main__":
    main()
