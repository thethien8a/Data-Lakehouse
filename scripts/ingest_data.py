#!/usr/bin/env python3
"""
Script to ingest UCI Online Retail II data into MinIO as Parquet format
"""
import os
import pandas as pd
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
from minio import Minio
from minio.error import S3Error
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import argparse
import io

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_minio_client():
    """
    Create and return a MinIO client
    """
    # Use default MinIO credentials
    minio_client = Minio(
        "localhost:9090",
        access_key=os.getenv("MINIO_ROOT_USER"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
        secure=False
    )
    return minio_client

def ensure_bucket_exists(client, bucket_name):
    """
    Ensure the specified bucket exists, create if it doesn't
    """
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            logger.info(f"Bucket '{bucket_name}' created successfully")
        else:
            logger.info(f"Bucket '{bucket_name}' already exists")
    except S3Error as e:
        logger.error(f"Error creating bucket '{bucket_name}': {e}")
        raise

def get_next_processing_date():
    """
    Get the next date to process based on last processed date
    """
    date_file = Path("../data/last_processed_date.txt")
    if date_file.exists():
        with open(date_file, 'r') as f:
            last_date = f.read().strip()
            last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
            next_date = last_date + timedelta(days=1)
    else:
        # Default start date: 2010-12-01 
        next_date = datetime(2010, 12, 1).date()
    
    return next_date

def update_last_processed_date(date):
    """
    Update the last processed date
    """
    date_file = Path("../data/last_processed_date.txt")
    with open(date_file, 'w') as f:
        f.write(date.strftime("%Y-%m-%d"))

def load_online_retail_data_by_date(file_path, target_date):
    """
    Load the Online Retail II Excel file and filter by target date
    """
    logger.info(f"Loading data from {file_path} for date {target_date}...")
    
    # Load Excel file with multiple sheets
    xl_file = pd.ExcelFile(file_path)
    sheets_data = {}
    
    for sheet_name in xl_file.sheet_names:
        logger.info(f"Loading sheet: {sheet_name}")
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Convert InvoiceDate to datetime if it exists
        if 'InvoiceDate' in df.columns:
            df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
            df_filtered = df[df['InvoiceDate'].dt.date == target_date]
        else:
            # If there's no InvoiceDate column, return empty
            df_filtered = pd.DataFrame()
        
        if not df_filtered.empty:
            sheets_data[sheet_name] = df_filtered
            logger.info(f"Sheet '{sheet_name}' filtered for {target_date}, shape: {df_filtered.shape}")
        else:
            logger.info(f"No data found for {target_date} in sheet '{sheet_name}'")
    
    return sheets_data

def convert_to_parquet_and_upload(client, sheets_data, target_date):
    """
    Convert each sheet to Parquet format and upload to MinIO
    """
    if not sheets_data:
        logger.info(f"No data to upload for date {target_date}")
        return
    
    for sheet_name, df in sheets_data.items():
        try:
            # Clean sheet name to be compatible with MinIO object names
            clean_sheet_name = sheet_name.replace(" ", "_").replace("/", "_").lower()
            
            # Create a Parquet file in memory
            table = pa.Table.from_pandas(df)
            
            # Generate a unique filename with target date and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            object_name = f"online_retail_ii/{clean_sheet_name}_{target_date}_{timestamp}.parquet"
            

            parquet_buffer = io.BytesIO()
            pq.write_table(table, parquet_buffer)
            parquet_buffer.seek(0)
            
            # Upload to MinIO bronze bucket
            bytes_count = len(parquet_buffer.getvalue())
            client.put_object(
                "bronze",
                object_name,
                parquet_buffer,
                bytes_count,
                content_type="application/octet-stream"
            )
            
            logger.info(f"Successfully uploaded {object_name} to bronze bucket ({bytes_count} bytes)")
            
        except Exception as e:
            logger.error(f"Error processing sheet '{sheet_name}': {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Ingest UCI Online Retail II data into MinIO')
    parser.add_argument('--date', type=str, help='Date to process in YYYY-MM-DD format (e.g., 2010-12-01)')
    args = parser.parse_args()
    
    # Path to the downloaded Excel file
    excel_file_path = "../data/online_retail_II.xlsx"  
    
    # Check if the Excel file exists
    if not Path(excel_file_path).exists():
        logger.error(f"Excel file not found at {excel_file_path}")
        return
         
    try:
        # Create MinIO client
        minio_client = create_minio_client()
        
        # Ensure bronze bucket exists
        ensure_bucket_exists(minio_client, "bronze")
        
        # Determine target date
        if args.date:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
            logger.info(f"Processing data for specified date: {target_date}")
        else:
            target_date = get_next_processing_date()
            logger.info(f"Processing data for next date in sequence: {target_date}")
        
        # Load the data filtered by date
        sheets_data = load_online_retail_data_by_date(excel_file_path, target_date)
        
        # Convert to Parquet and upload to MinIO
        convert_to_parquet_and_upload(minio_client, sheets_data, target_date)
        
        # Update the last processed date only if there was data for this date
        if sheets_data:
            update_last_processed_date(target_date)
            logger.info(f"Data ingestion for {target_date} completed successfully!")
        else:
            logger.info(f"No data found for {target_date}, skipping date update.")
         
    except S3Error as e:
        logger.error(f"S3 Error: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()