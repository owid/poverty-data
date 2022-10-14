"""Generate OWID poverty dataset files from most up-to-date sources.

"""

import argparse
import json
from typing import List

import pandas as pd

from scripts.shared import OUTPUT_DIR, OUTPUT_FILE_BASE_NAME, CODEBOOK_PATH

# Define paths to output files.
OUTPUT_CSV_FILE = (OUTPUT_DIR / OUTPUT_FILE_BASE_NAME).with_suffix(".csv")
OUTPUT_EXCEL_FILE = (OUTPUT_DIR / OUTPUT_FILE_BASE_NAME).with_suffix(".xlsx")
OUTPUT_JSON_FILE = (OUTPUT_DIR / OUTPUT_FILE_BASE_NAME).with_suffix(".json")


def df_to_json(complete_dataset: pd.DataFrame, output_path: str, static_columns: List[str]) -> None:
    megajson = {}

    # Round all values to 3 decimals.
    rounded_cols = [col for col in list(complete_dataset) if col not in ("country", "year", "iso_code")]
    complete_dataset[rounded_cols] = complete_dataset[rounded_cols].round(3)

    for _, row in complete_dataset.iterrows():

        row_country = row["country"]
        row_dict_static = row.drop("country")[static_columns].dropna().to_dict()
        row_dict_dynamic = row.drop("country").drop(static_columns).dropna().to_dict()

        if row_country not in megajson:
            megajson[row_country] = row_dict_static
            megajson[row_country]["data"] = [row_dict_dynamic]
        else:
            megajson[row_country]["data"].append(row_dict_dynamic)

    with open(output_path, "w") as file:
        file.write(json.dumps(megajson, indent=4))


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    # Sort rows and columns conveniently.
    df = df.sort_values(["country", "year"]).reset_index(drop=True)
    first_columns = ["country", "year", "iso_code"]
    df = df[first_columns + [column for column in df.columns if column not in first_columns]]

    return df


def main() -> None:
    # TODO: Prepare dataset.
    df = pd.DataFrame({"country": ["World"], "year": [2021], "iso_code": ["OWID_WRL"], "variable": ["TEST"]})

    # Load codebook.
    codebook = pd.read_csv(CODEBOOK_PATH)


    #
    # Save outputs.
    #
    # Save dataset to files in different formats.
    df.to_csv(OUTPUT_CSV_FILE, index=False, float_format='%.3f')
    df.to_excel(OUTPUT_EXCEL_FILE, index=False, float_format='%.3f')
    df_to_json(df, OUTPUT_JSON_FILE, ["iso_code"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()
    main()
