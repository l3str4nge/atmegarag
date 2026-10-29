from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
EVALS_DIR = PROJECT_ROOT / "evals"
GOLDEN_PATH = EVALS_DIR / "datasets" / "golden.yaml"
