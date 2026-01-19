"""
Data preparation script for Medical AI project.
Downloads the Chest X-Ray Pneumonia dataset from Kaggle.
"""

import kagglehub
import os


def download_dataset():
    """
    Download the Chest X-Ray Pneumonia dataset from Kaggle.
    
    Returns:
        str: Path to the downloaded dataset
    """
    print("Downloading Chest X-Ray Pneumonia dataset from Kaggle...")
    path = kagglehub.dataset_download("paultimothymooney/chest-xray-pneumonia")
    print(f"Dataset downloaded successfully at: {path}")
    return path


if __name__ == "__main__":
    dataset_path = download_dataset()
    print(f"\nDataset path: {dataset_path}")
    print("You can use this path in train.py to load the dataset.")
