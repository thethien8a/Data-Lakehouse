#!/usr/bin/env python3
"""
MinIO Manager for Lakehouse Project
Handles bucket creation, data upload/download, and organization
"""

import boto3
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinIOManager:
    def __init__(self, endpoint="http://localhost:9000", access_key="minioadmin", secret_key="minioadmin"):
        """
        Initialize MinIO client
        Default credentials for local MinIO instance
        """
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key

        # Create S3 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='us-east-1'  # MinIO doesn't use regions, but boto3 requires it
        )

        logger.info(f"Connected to MinIO at {endpoint}")

    def create_buckets(self):
        """
        Create the main buckets for Bronze, Silver, Gold layers
        """
        buckets = ['bronze', 'silver', 'gold']

        for bucket in buckets:
            try:
                self.s3_client.create_bucket(Bucket=bucket)
                logger.info(f"✅ Created bucket: {bucket}")
            except Exception as e:
                if 'BucketAlreadyExists' in str(e) or 'BucketAlreadyOwnedByYou' in str(e):
                    logger.info(f"ℹ️  Bucket '{bucket}' already exists")
                else:
                    logger.error(f"❌ Failed to create bucket '{bucket}': {e}")

    def create_bucket_structure(self):
        """
        Create folder structure within buckets
        """
        structure = {
            'bronze': ['orders/', 'products/', 'customers/', 'fx_rates/', 'archive/'],
            'silver': ['orders/', 'products/', 'customers/', 'analytics/', 'staging/'],
            'gold': ['reports/', 'dashboards/', 'metrics/', 'exports/']
        }

        for bucket, folders in structure.items():
            for folder in folders:
                try:
                    # Create empty object to represent folder
                    self.s3_client.put_object(Bucket=bucket, Key=folder)
                    logger.info(f"📁 Created folder: {bucket}/{folder}")
                except Exception as e:
                    logger.error(f"❌ Failed to create folder '{bucket}/{folder}': {e}")

    def upload_file(self, bucket, key, file_path, metadata=None):
        """
        Upload a file to MinIO bucket

        Args:
            bucket (str): Bucket name
            key (str): Object key (path in bucket)
            file_path (str): Local file path
            metadata (dict): Optional metadata
        """
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata

            # Add timestamp to metadata
            if not metadata:
                metadata = {}
            metadata['upload_timestamp'] = datetime.now().isoformat()

            self.s3_client.upload_file(
                file_path,
                bucket,
                key,
                ExtraArgs={'Metadata': metadata}
            )
            logger.info(f"📤 Uploaded: {file_path} → {bucket}/{key}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to upload {file_path}: {e}")
            return False

    def upload_dataframe(self, bucket, key, df, file_format='parquet'):
        """
        Upload pandas DataFrame to MinIO

        Args:
            bucket (str): Bucket name
            key (str): Object key (should include .parquet extension)
            df (pd.DataFrame): Data to upload
            file_format (str): 'parquet' or 'csv'
        """
        try:
            # Create temporary file
            temp_file = f"temp_upload.{file_format}"

            if file_format == 'parquet':
                df.to_parquet(temp_file, index=False)
            elif file_format == 'csv':
                df.to_csv(temp_file, index=False)
            else:
                raise ValueError("Unsupported format. Use 'parquet' or 'csv'")

            # Upload file
            success = self.upload_file(bucket, key, temp_file)

            # Clean up
            os.remove(temp_file)

            if success:
                logger.info(f"📊 Uploaded DataFrame ({len(df)} rows) → {bucket}/{key}")
            return success

        except Exception as e:
            logger.error(f"❌ Failed to upload DataFrame: {e}")
            return False

    def download_file(self, bucket, key, local_path):
        """
        Download file from MinIO bucket

        Args:
            bucket (str): Bucket name
            key (str): Object key
            local_path (str): Local file path to save
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            self.s3_client.download_file(bucket, key, local_path)
            logger.info(f"📥 Downloaded: {bucket}/{key} → {local_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to download {bucket}/{key}: {e}")
            return False

    def download_dataframe(self, bucket, key):
        """
        Download and return DataFrame from MinIO

        Args:
            bucket (str): Bucket name
            key (str): Object key

        Returns:
            pd.DataFrame: Downloaded data
        """
        try:
            # Create temporary file
            temp_file = "temp_download.parquet"

            # Download file
            self.s3_client.download_file(bucket, key, temp_file)

            # Read DataFrame
            if key.endswith('.parquet'):
                df = pd.read_parquet(temp_file)
            elif key.endswith('.csv'):
                df = pd.read_csv(temp_file)
            else:
                raise ValueError("Unsupported format. Use .parquet or .csv files")

            # Clean up
            os.remove(temp_file)

            logger.info(f"📊 Downloaded DataFrame ({len(df)} rows) from {bucket}/{key}")
            return df

        except Exception as e:
            logger.error(f"❌ Failed to download DataFrame from {bucket}/{key}: {e}")
            return None

    def list_objects(self, bucket, prefix=""):
        """
        List objects in bucket with optional prefix

        Args:
            bucket (str): Bucket name
            prefix (str): Prefix to filter objects

        Returns:
            list: List of object keys
        """
        try:
            objects = []
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        objects.append(obj['Key'])

            return objects
        except Exception as e:
            logger.error(f"❌ Failed to list objects in {bucket}/{prefix}: {e}")
            return []

    def get_bucket_info(self):
        """
        Get information about all buckets
        """
        try:
            buckets = self.s3_client.list_buckets()
            info = []

            for bucket in buckets['Buckets']:
                bucket_name = bucket['Name']

                # Get object count and size
                total_objects = 0
                total_size = 0

                try:
                    paginator = self.s3_client.get_paginator('list_objects_v2')
                    page_iterator = paginator.paginate(Bucket=bucket_name)

                    for page in page_iterator:
                        if 'Contents' in page:
                            total_objects += len(page['Contents'])
                            for obj in page['Contents']:
                                total_size += obj['Size']
                except:
                    pass  # Bucket might be empty

                info.append({
                    'bucket': bucket_name,
                    'created': bucket['CreationDate'],
                    'objects': total_objects,
                    'size_mb': round(total_size / (1024*1024), 2)
                })

            return info
        except Exception as e:
            logger.error(f"❌ Failed to get bucket info: {e}")
            return []

    def setup_lakehouse_structure(self):
        """
        Complete setup for lakehouse: create buckets and folder structure
        """
        logger.info("🚀 Setting up Lakehouse MinIO structure...")

        # Create buckets
        self.create_buckets()

        # Create folder structure
        self.create_bucket_structure()

        # Display setup summary
        bucket_info = self.get_bucket_info()
        logger.info("✅ Lakehouse setup complete!")
        logger.info("📊 Bucket Summary:")
        for info in bucket_info:
            logger.info(f"  • {info['bucket']}: {info['objects']} objects, {info['size_mb']} MB")

        return True


if __name__ == "__main__":
    # Example usage
    minio = MinIOManager()

    # Setup lakehouse structure
    minio.setup_lakehouse_structure()

    # Display current bucket info
    print("\n📊 Current Buckets:")
    for info in minio.get_bucket_info():
        print(f"  • {info['bucket']}: {info['objects']} objects, {info['size_mb']} MB")
