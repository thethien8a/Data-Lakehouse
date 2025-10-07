#!/usr/bin/env python3
"""
Script to download UCI Online Retail II dataset
"""
import os
import requests
from pathlib import Path

def download_online_retail_data():
    """
    Download the Online Retail II dataset from UCI ML Repository
    """
    print("Downloading UCI Online Retail II dataset...")
    url = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Download the zip file
    response = requests.get(url)
    
    if response.status_code == 200:
        zip_path = data_dir / "online_retail_ii.zip"
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        print(f"Dataset downloaded successfully to {zip_path}")
        
        # Extract the Excel file from the zip
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        
        print("Dataset extracted successfully")
        
        # Find the Excel file
        excel_files = list(data_dir.glob("*.xlsx"))
        if excel_files:
            print(f"Found Excel file: {excel_files[0]}")
            return str(excel_files[0])
        else:
            print("No Excel file found in the extracted data")
            return None
    else:
        print(f"Failed to download dataset. Status code: {response.status_code}")
        return None

def remove_zip_file(zip_path):
    """
    Remove the zip file after extraction
    """
    try:
        if zip_path.exists():
            os.remove(zip_path)
            print(f"Removed zip file: {zip_path}")
    except Exception as e:
        print(f"Error removing zip file: {e}")

if __name__ == "__main__":
    # # Download the dataset
    download_online_retail_data()
    # Remove zip file after extraction
    remove_zip_file(Path("data") / "online_retail_ii.zip")