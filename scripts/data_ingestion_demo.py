#!/usr/bin/env python3
"""
Data Ingestion Demo for Lakehouse
Demonstrates uploading mock e-commerce data to MinIO Bronze layer
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add scripts directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from minio_manager import MinIOManager
from mock_data_generator import EcommerceDataGenerator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataIngestionDemo:
    def __init__(self):
        """Initialize with MinIO manager and data generator"""
        self.minio = MinIOManager()
        self.generator = EcommerceDataGenerator()

        logger.info("🚀 Initialized Data Ingestion Demo")

    def setup_minio_structure(self):
        """Setup MinIO buckets and folder structure"""
        logger.info("🏗️ Setting up MinIO lakehouse structure...")
        self.minio.setup_lakehouse_structure()

    def generate_sample_data(self, scale='small'):
        """Generate sample e-commerce data"""
        logger.info(f"🎲 Generating {scale} scale sample data...")
        self.data = self.generator.generate_all_data(scale=scale)

        # Display summary
        print("\n📊 Generated Dataset Summary:")
        for table_name, df in self.data.items():
            print(f"  • {table_name}: {len(df)} rows, {len(df.columns)} columns")

        return self.data

    def upload_bronze_layer(self):
        """Upload data to Bronze layer in MinIO"""
        logger.info("📤 Uploading data to Bronze layer...")

        # Define upload mapping: table -> folder in bronze bucket
        upload_mapping = {
            'customers': 'customers/',
            'products': 'products/',
            'orders': 'orders/',
            'fx_rates': 'fx_rates/'
        }

        uploaded_files = []

        for table_name, folder in upload_mapping.items():
            if table_name not in self.data:
                logger.warning(f"⚠️  Table '{table_name}' not found in data, skipping...")
                continue

            df = self.data[table_name]

            # Create timestamped filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{table_name}_{timestamp}.parquet"
            object_key = f"{folder}{filename}"

            # Upload to MinIO
            success = self.minio.upload_dataframe(
                bucket='bronze',
                key=object_key,
                df=df,
                file_format='parquet'
            )

            if success:
                uploaded_files.append({
                    'table': table_name,
                    'bucket': 'bronze',
                    'key': object_key,
                    'rows': len(df)
                })

        return uploaded_files

    def demonstrate_data_operations(self):
        """Demonstrate various MinIO data operations"""
        logger.info("🔍 Demonstrating data operations...")

        print("\n📋 Bronze Layer Contents:")

        # List objects in bronze bucket
        objects = self.minio.list_objects('bronze')
        for obj in objects[:20]:  # Show first 20 objects
            print(f"  • bronze/{obj}")

        if len(objects) > 20:
            print(f"  ... and {len(objects) - 20} more objects")

        # Demonstrate downloading data
        if objects:
            sample_object = objects[0]
            print(f"\n📥 Downloading sample: {sample_object}")

            # Download to local file
            local_path = f"data/downloaded/{sample_object.replace('/', '_')}"
            success = self.minio.download_file('bronze', sample_object, local_path)

            if success:
                print(f"✅ Downloaded to: {local_path}")

                # Try to read as DataFrame
                if sample_object.endswith('.parquet'):
                    df = self.minio.download_dataframe('bronze', sample_object)
                    if df is not None:
                        print(f"📊 DataFrame shape: {df.shape}")
                        print(f"📊 Columns: {list(df.columns)}")
                        print(f"📊 Sample data:\n{df.head(3)}")

    def show_minio_console_access(self):
        """Display information about MinIO console access"""
        print("\n🌐 MinIO Console Access:")
        print("  📱 Web Console: http://localhost:9000")
        print("  👤 Username: minioadmin")
        print("  🔑 Password: minioadmin")
        print()
        print("📁 Available Buckets:")
        bucket_info = self.minio.get_bucket_info()
        for info in bucket_info:
            print(f"  • {info['bucket']}: {info['objects']} objects, {info['size_mb']} MB")

    def run_full_demo(self, scale='small'):
        """Run complete ingestion demo"""
        logger.info("🎬 Starting full data ingestion demo...")

        try:
            # Step 1: Setup MinIO structure
            self.setup_minio_structure()

            # Step 2: Generate sample data
            self.generate_sample_data(scale=scale)

            # Step 3: Upload to Bronze layer
            uploaded_files = self.upload_bronze_layer()

            print("\n📤 Upload Summary:")
            for file_info in uploaded_files:
                print(f"  ✅ {file_info['table']}: {file_info['rows']} rows → {file_info['bucket']}/{file_info['key']}")

            # Step 4: Demonstrate operations
            self.demonstrate_data_operations()

            # Step 5: Show console access
            self.show_minio_console_access()

            logger.info("✅ Demo completed successfully!")

        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            raise

    def cleanup_demo_data(self):
        """Clean up demo data (optional)"""
        logger.warning("🧹 This will delete all demo data from MinIO. Are you sure?")
        # Note: In a real scenario, you'd want user confirmation here

        # For demo purposes, we'll skip actual deletion
        logger.info("ℹ️  Cleanup skipped for demo purposes")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Data Ingestion Demo for Lakehouse')
    parser.add_argument('--scale', choices=['small', 'medium', 'large'],
                       default='small', help='Data scale (default: small)')
    parser.add_argument('--setup-only', action='store_true',
                       help='Only setup MinIO structure, no data generation')

    args = parser.parse_args()

    demo = DataIngestionDemo()

    if args.setup_only:
        demo.setup_minio_structure()
        demo.show_minio_console_access()
    else:
        demo.run_full_demo(scale=args.scale)


if __name__ == "__main__":
    main()
