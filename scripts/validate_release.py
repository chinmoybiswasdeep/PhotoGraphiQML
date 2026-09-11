"""Run local CI-equivalent checks and retain exit statuses without hiding failures."""

import json
import platform
import subprocess
import sys
from pathlib import Path


def main():
    commands = [
        [
            sys.executable,
            "-m",
            "pytest",
            "--cov=photographiqml",
            "--cov-fail-under=90",
            "--cov-report=json:coverage.json",
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
        [sys.executable, "-m", "build"],
        [sys.executable, "-m", "mkdocs", "build", "--strict"],
        [sys.executable, "scripts/execute_tutorials.py"],
    ]
    results = []
    for command in commands:
        process = subprocess.run(command, check=False)
        results.append({"command": command[1:], "returncode": process.returncode})
    Path("validation-results.json").write_text(
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
