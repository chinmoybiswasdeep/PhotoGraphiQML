"""Run local CI-equivalent checks and retain exit statuses without hiding failures."""

import argparse
import json
import os
import platform
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    output = parser.parse_args().output_dir
    output.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, COVERAGE_FILE=str((output / ".coverage").resolve()))
    commands = [
        [
            sys.executable,
            "-m",
            "pytest",
            "--cov=photographiqml",
            "--cov-fail-under=90",
            f"--cov-report=json:{output / 'coverage.json'}",
            "--cov-report=term-missing",
        ],
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "src",
            "tests",
            "scripts",
            "experiments",
            "examples",
        ],
        [
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--check",
            "src",
            "tests",
            "scripts",
            "experiments",
            "examples",
        ],
        [sys.executable, "-m", "mypy"],
        [sys.executable, "-m", "build", "--outdir", str(output / "dist")],
        [
            sys.executable,
            "-m",
            "mkdocs",
            "build",
            "--strict",
            "--site-dir",
            str((output / "site").resolve()),
        ],
        [sys.executable, "scripts/execute_tutorials.py"],
    ]
    results = []
    for command in commands:
        process = subprocess.run(command, check=False, env=environment)
        results.append({"command": command[1:], "returncode": process.returncode})
    (output / "validation-results.json").write_text(
        json.dumps(
            {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "checks": results,
            },
            indent=2,
        )
    )
    return int(any(result["returncode"] for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
