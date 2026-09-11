"""Execute every tutorial and curated notebook with the current interpreter."""

import json
import runpy
import sys
import tempfile
from pathlib import Path

import nbformat
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient


def main():
    for path in sorted(Path("examples/tutorials").glob("*.py")):
        print(path, flush=True)
        runpy.run_path(str(path), run_name="__main__")
    with tempfile.TemporaryDirectory() as directory:
        spec = Path(directory) / "pgml"
        spec.mkdir()
        (spec / "kernel.json").write_text(
            json.dumps(
                {
                    "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                    "display_name": "PhotoGraphiQML checks",
                    "language": "python",
                }
            )
        )
        manager = KernelSpecManager(kernel_dirs=[directory])
        for path in sorted(Path("notebooks").glob("*.ipynb")):
            print(path, flush=True)
            notebook = nbformat.read(path, as_version=4)
            kernel = KernelManager(kernel_name="pgml", kernel_spec_manager=manager)
            try:
                NotebookClient(notebook, km=kernel, timeout=120).execute()
                nbformat.write(notebook, path)
            finally:
                if kernel.has_kernel:
                    kernel.shutdown_kernel(now=True)


if __name__ == "__main__":
    main()
