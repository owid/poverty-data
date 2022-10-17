"""Upload OWID Poverty dataset files to S3 and make them publicly available.

This script requires OWID credentials to write files in the S3 bucket.

"""

import argparse
from pathlib import Path

from tqdm.auto import tqdm
from owid.datautils.io.s3 import S3

from scripts.shared import OUTPUT_DIR

# Define S3 base URL.
S3_URL = "https://nyc3.digitaloceanspaces.com"
# Profile name to use for S3 client (as defined in .aws/config).
S3_PROFILE_NAME = "default"
# S3 bucket name and folder where dataset files will be stored.
S3_BUCKET_NAME = "owid-public"
S3_DATA_DIR = Path("data/poverty")
# Local files to upload.
PIP_DATASET_NAME = "pip_dataset"
FILES_TO_UPLOAD = {
    (OUTPUT_DIR / PIP_DATASET_NAME).with_suffix(".csv"): (S3_DATA_DIR / PIP_DATASET_NAME).with_suffix(".csv"),
}


def main(files_to_upload, s3_bucket_name=S3_BUCKET_NAME):
    # Make files publicly available.
    public = True
    # Initialise S3 client.
    s3 = S3()
    # Upload and make public each of the files.
    for local_file in tqdm(files_to_upload):
        s3_file = files_to_upload[local_file]
        tqdm.write(f"Uploading file {local_file} to S3 bucket {s3_bucket_name} as {s3_file}.")
        s3.upload_to_s3(local_path=str(local_file), s3_path=f"s3://{s3_bucket_name}/{str(s3_file)}",public=public)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    main(files_to_upload=FILES_TO_UPLOAD)
