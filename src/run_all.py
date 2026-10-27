"""Run the full pipeline: cleaning -> EDA -> modelling -> business impact."""
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent

for script in ["cleaning.py", "eda.py", "model.py", "business_impact.py"]:
    print(f"\n=== Running {script} ===")
    subprocess.run([sys.executable, str(SRC / script)], check=True)
print("\nDone. See reports/ and visualisations/.")
