import pandas as pd
import os

def extract_csv(file_path):
    if os.path.exists(file_path):
        print(f"Extracting {file_path}...")
        return pd.read_csv(file_path)
    else:
        print(f"File {file_path} not found!")
        return None
