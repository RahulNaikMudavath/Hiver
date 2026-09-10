"""Download Customer Support on Twitter dataset from Kaggle."""

import os
import shutil
import kagglehub
from pathlib import Path

DATASET_NAME = "thoughtvector/customer-support-on-twitter"
RAW_DATA_DIR = Path("./data/raw")


def download_dataset(target_dir: Path = RAW_DATA_DIR) -> Path:
    """Download the dataset using kagglehub and copy files to target_dir.

    Args:
        target_dir: Destination directory for raw data.

    Returns:
        Path to the downloaded/copied dataset directory.
    """
    print(f"Downloading dataset '{DATASET_NAME}' via kagglehub...")
    download_path = kagglehub.dataset_download(DATASET_NAME)
    print(f"Downloaded to cache: {download_path}")

    target_dir.mkdir(parents=True, exist_ok=True)
    for item in Path(download_path).glob("*"):
        dest = target_dir / item.name
        if not dest.exists():
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
            print(f"Copied {item.name} to {dest}")

    print(f"Dataset ready at: {target_dir.resolve()}")
    return target_dir


if __name__ == "__main__":
    download_dataset()
