"""Clean run of the A-D2 pipeline: executes notebooks 01 -> 02 -> 03 in order, in place, with saved outputs.

Usage (from the repository root, inside the environment of requirements.txt):
    python src/run_notebooks.py
Each notebook starts in a fresh kernel, so the run is equivalent to "Restart & Run All" in order.
The kernel is pinned to the interpreter running this script (a temporary kernelspec), so a "python3"
kernel registered elsewhere on the machine can never be picked up by mistake.
"""
import json
import sys
import tempfile
import time
from importlib.metadata import version
from pathlib import Path

import nbformat
from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client.manager import KernelManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
ORDER = ["01_data_audit_eda.ipynb", "02_data_architecture.ipynb", "03_preparation_eda_features.ipynb"]
PACKAGES = ["pandas", "numpy", "scikit-learn", "scipy", "matplotlib", "seaborn", "PyYAML"]

if sys.platform.startswith("win"):   # avoid the zmq / Proactor event-loop warning on Windows
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

print(f"Python {sys.version.split()[0]} at {sys.executable}")
print("  " + ", ".join(f"{p} {version(p)}" for p in PACKAGES))

with tempfile.TemporaryDirectory() as kdir:
    spec_dir = Path(kdir) / "ba-project"
    spec_dir.mkdir()
    (spec_dir / "kernel.json").write_text(json.dumps({
        "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        "display_name": "BA project (pinned)", "language": "python"}))
    ksm = KernelSpecManager(kernel_dirs=[kdir])
    for name in ORDER:
        path = ROOT / "notebooks" / name
        start = time.time()
        nb = nbformat.read(path, as_version=4)
        km = KernelManager(kernel_name="ba-project", kernel_spec_manager=ksm)
        NotebookClient(nb, km=km, timeout=3600, resources={"metadata": {"path": str(path.parent)}}).execute()
        nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
        nbformat.write(nb, path)
        print(f"{name}: OK ({time.time() - start:.0f}s)")
