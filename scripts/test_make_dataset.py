import unittest
import pandas as pd
from scripts.shared import OUTPUT_CSV_FILE, PIP_CODEBOOK_FILE


class TestMakeDataset(unittest.TestCase):
    """Unit tests for the `make_dataset` module."""

    @classmethod
    def setUpClass(cls):
        cls.data = pd.read_csv(OUTPUT_CSV_FILE.with_suffix(".csv"))
        cls.codebook = pd.read_csv(PIP_CODEBOOK_FILE)
        cls.index_cols = ["country", "year"]

    def test_columns_in_codebook(self):
        """All columns in cleaned dataset should be in the codebook."""
        msg = "Codebook column descriptions are not identical or in the same order as data columns."
        self.assertTrue(self.codebook["column"].tolist() == self.data.columns.tolist(), msg)

    def test_column_names_no_whitespace(self):
        """All columns in cleaned dataset should not contain whitespace."""
        col_contains_space = self.data.columns.str.contains(r"\s", regex=True)
        msg = (
            "Columns should not contain whitespace, but the following "
            f"columns do: {self.data.columns[col_contains_space].tolist()}"
        )
        self.assertTrue(col_contains_space.sum() == 0, msg)

    def test_column_names_all_lowercase(self):
        """All columns in cleaned dataset should be lowercase."""
        col_is_lower = self.data.columns == self.data.columns.str.lower()
        msg = (
            "Columns should not uppercase characters, but the following "
            f"columns do: {self.data.columns[~col_is_lower].tolist()}"
        )
        self.assertTrue(col_is_lower.all(), msg)

    def test_no_nan_rows(self):
        """All rows in cleaned dataset should contain at least one non-NaN value."""
        row_all_nan = self.data.drop(columns=self.index_cols).isnull().all(axis=1)
        msg = (
            "All rows should contain at least one non-NaN value, but "
            f"{row_all_nan.sum()} row(s) contain all NaN values."
        )
        self.assertTrue(row_all_nan.sum() == 0, msg)
