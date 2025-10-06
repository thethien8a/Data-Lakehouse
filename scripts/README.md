# 🏗️ Lakehouse Data Ingestion with MinIO

Hướng dẫn chi tiết cách làm việc với MinIO để ingest dữ liệu vào Bronze layer của lakehouse.

## 📋 Mục lục
- [MinIO Console Access](#minio-console-access)
- [Cấu trúc Bucket](#cấu-trúc-bucket)
- [Chuẩn bị Environment](#chuẩn-bị-environment)
- [Scripts Available](#scripts-available)
- [Quick Start](#quick-start)
- [Manual Operations](#manual-operations)
- [Troubleshooting](#troubleshooting)

## 🌐 MinIO Console Access

### Web Console
```
URL: http://localhost:9000
Username: minioadmin
Password: minioadmin
```

### Kiểm tra MinIO đang chạy
```bash
docker ps | findstr minio
```

## 📁 Cấu trúc Bucket

Lakehouse sử dụng 3 buckets chính theo Medallion Architecture:

```
bronze/                    # Raw data landing zone
├── customers/            # Customer data
├── products/             # Product catalog
├── orders/               # Order transactions
├── fx_rates/             # Exchange rates
└── archive/              # Historical archives

silver/                   # Cleaned & transformed data
├── customers/            # Standardized customers
├── products/             # Enriched products
├── orders/               # Business-validated orders
├── analytics/            # Analytical views
└── staging/              # Transformation staging

gold/                     # Business-ready analytics
├── reports/              # Business reports
├── dashboards/           # Dashboard data
├── metrics/              # KPIs & metrics
└── exports/              # Data exports
```

## 🛠️ Chuẩn bị Environment

### 1. Install Dependencies
```bash
pip install boto3 pandas pyarrow faker
```

### 2. Verify MinIO Connection
```python
from scripts.minio_manager import MinIOManager
minio = MinIOManager()
print("Buckets:", minio.get_bucket_info())
```

## 📜 Scripts Available

### 1. `minio_manager.py` - MinIO Operations
```python
from scripts.minio_manager import MinIOManager

# Initialize
minio = MinIOManager()

# Setup lakehouse structure
minio.setup_lakehouse_structure()

# Upload file
minio.upload_file('bronze', 'customers/data.parquet', 'local_file.parquet')

# Upload DataFrame
minio.upload_dataframe('bronze', 'customers/data.parquet', df)

# Download file
minio.download_file('bronze', 'customers/data.parquet', 'local_copy.parquet')

# Download DataFrame
df = minio.download_dataframe('bronze', 'customers/data.parquet')

# List objects
objects = minio.list_objects('bronze', prefix='customers/')
```

### 2. `mock_data_generator.py` - Generate Sample Data
```python
from scripts.mock_data_generator import EcommerceDataGenerator

# Initialize generator
generator = EcommerceDataGenerator()

# Generate complete dataset
data = generator.generate_all_data(scale='small')  # small/medium/large

# Access individual tables
customers_df = data['customers']
products_df = data['products']
orders_df = data['orders']
fx_rates_df = data['fx_rates']

# Save to Parquet files
generator.save_to_parquet(data, output_dir='data/mock')
```

**Data Scales:**
- `small`: 1K customers, 500 products, 5K orders
- `medium`: 10K customers, 5K products, 50K orders
- `large`: 50K customers, 25K products, 250K orders

### 3. `data_ingestion_demo.py` - Complete Demo
```bash
# Setup MinIO structure only
python scripts/data_ingestion_demo.py --setup-only

# Full demo with small data
python scripts/data_ingestion_demo.py --scale small

# Medium scale demo
python scripts/data_ingestion_demo.py --scale medium
```

## 🚀 Quick Start

### Step 1: Setup MinIO Structure
```bash
cd /path/to/lakehouse
python scripts/data_ingestion_demo.py --setup-only
```

### Step 2: Generate & Upload Sample Data
```bash
python scripts/data_ingestion_demo.py --scale small
```

### Step 3: Verify in MinIO Console
1. Open http://localhost:9000
2. Login với minioadmin/minioadmin
3. Check buckets: bronze, silver, gold
4. Browse files trong bronze/customers/, bronze/products/, etc.

## 🔧 Manual Operations

### Upload File từ Command Line
```bash
# Using AWS CLI (configure for MinIO first)
aws --endpoint-url=http://localhost:9000 s3 cp data.parquet s3://bronze/customers/

# Using mc (MinIO Client)
mc alias set lakehouse http://localhost:9000 minioadmin minioadmin
mc cp data.parquet lakehouse/bronze/customers/
```

### Create Bucket Structure Manually
```python
from scripts.minio_manager import MinIOManager

minio = MinIOManager()

# Create buckets
minio.create_buckets()

# Create folders
folders = ['customers/', 'products/', 'orders/', 'fx_rates/', 'archive/']
for folder in folders:
    minio.s3_client.put_object(Bucket='bronze', Key=folder)
```

### Upload Existing CSV/Parquet Files
```python
import pandas as pd
from scripts.minio_manager import MinIOManager

minio = MinIOManager()

# Upload CSV file
df = pd.read_csv('existing_data.csv')
minio.upload_dataframe('bronze', 'customers/existing_data.parquet', df)

# Upload existing Parquet
minio.upload_file('bronze', 'products/catalog.parquet', 'existing_catalog.parquet')
```

## 🔍 Data Organization Best Practices

### File Naming Convention
```
{table_name}_{YYYYMMDD_HHMMSS}.parquet
customers_20241201_143022.parquet
orders_20241201_143500.parquet
```

### Partitioning Strategy
```
bronze/orders/
├── year=2024/
│   ├── month=01/
│   │   ├── orders_20240101_*.parquet
│   │   └── orders_20240102_*.parquet
│   └── month=02/
│       └── ...
└── year=2023/
    └── ...
```

### Metadata Standards
```python
metadata = {
    'source': 'mock_generator',
    'table': 'customers',
    'rows': len(df),
    'columns': list(df.columns),
    'created_at': datetime.now().isoformat(),
    'version': '1.0'
}

minio.upload_dataframe('bronze', key, df, metadata=metadata)
```

## 🚨 Troubleshooting

### Connection Issues
```bash
# Check MinIO container
docker ps | grep minio

# Check MinIO logs
docker logs minio

# Test connection
curl http://localhost:9000/minio/health/live
```

### Permission Errors
```python
# Check credentials
minio = MinIOManager(
    endpoint="http://localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin"
)
```

### Upload Failures
```python
# Check bucket exists
buckets = minio.get_bucket_info()
print("Available buckets:", [b['bucket'] for b in buckets])

# Test small upload first
test_df = pd.DataFrame({'test': [1, 2, 3]})
minio.upload_dataframe('bronze', 'test.parquet', test_df)
```

### Memory Issues with Large Files
```python
# For large datasets, process in chunks
chunk_size = 10000
for i, chunk in enumerate(pd.read_csv('large_file.csv', chunksize=chunk_size)):
    key = f'bronze/data/part_{i:04d}.parquet'
    minio.upload_dataframe('bronze', key, chunk)
```

## 📊 Monitoring & Validation

### Check Data in MinIO
```python
# List all objects
objects = minio.list_objects('bronze')
print(f"Total objects in bronze: {len(objects)}")

# Get bucket statistics
bucket_info = minio.get_bucket_info()
for info in bucket_info:
    print(f"{info['bucket']}: {info['objects']} objects, {info['size_mb']} MB")
```

### Validate Data Quality
```python
# Download and inspect sample
df = minio.download_dataframe('bronze', 'customers/customers_20241201.parquet')
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Sample:\n{df.head()}")
print(f"Data types:\n{df.dtypes}")
```

## 🔗 Next Steps

Sau khi hoàn thành Bronze layer:

1. **Silver Layer**: Transform data với dbt
   ```bash
   cd dbt/
   dbt run --models staging
   ```

2. **Gold Layer**: Create analytics views
   ```bash
   dbt run --models marts
   ```

3. **BI Integration**: Connect với Superset/Metabase
4. **Orchestration**: Setup Airflow DAGs

## 📞 Support

Nếu gặp vấn đề:
1. Check MinIO logs: `docker logs minio`
2. Verify network: `curl http://localhost:9000`
3. Test scripts individually
4. Check Python dependencies

Happy data engineering! 🎉
