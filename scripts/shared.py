from pathlib import Path

# Define path to output directory.
OUTPUT_DIR = Path(__file__).parent.parent
# Define base names of output files.
OUTPUT_FILE_BASE_NAME = "owid-poverty-data"
# Define codebook path.
CODEBOOK_PATH = OUTPUT_DIR / "owid-poverty-codebook.csv"
