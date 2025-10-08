# 🏗️ Data Lakehouse Project

*Building a Modern Data Platform with DuckDB, dbt, and MinIO*

## 📋 Table of Contents
- [🎯 Overview](#-overview)
- [🛠️ Prerequisites](#️-prerequisites)
- [🚀 Setup Instructions](#-setup-instructions)
- [📊 Data Ingestion Process](#-data-ingestion-process)
- [📁 Project Structure](#-project-structure)
- [🔧 Configuration](#-configuration)
- [📈 Usage](#-usage)
- [📝 Documentation](#-documentation)

## 🎯 Overview

This project implements a modern data lakehouse architecture using:
- **Object Storage**: MinIO (S3-compatible) for raw data lake storage
- **Compute Engine**: DuckDB for fast analytical queries
- **Transformation**: dbt-duckdb for data modeling & transformation
- **Data Quality**: Soda Core for automated quality checks
- **BI Tool**: Apache Superset / Metabase for data visualization

The project follows the **Medallion Architecture** with three layers:
- 🥉 **Bronze Layer**: Raw, unprocessed data from sources
- 🥈 **Silver Layer**: Validated, standardized, and enriched data
- 🥇 **Gold Layer**: Business-ready analytics and reporting

## 🛠️ Prerequisites

- Docker and Docker Compose
- Python 3.8+
- pip package manager

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd lakehouse-project
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start MinIO Server
```bash
docker-compose -f docker/docker-compose.yml up -d
```

Wait for MinIO to be ready (approximately 30 seconds), then access the MinIO Console at `http://localhost:9001` with credentials:
- Access Key: `minioadmin`
- Secret Key: `minioadmin123`

### 4. Verify MinIO Buckets
After startup, MinIO will automatically create the following buckets:
- `bronze` - Raw data storage
- `silver` - Cleaned data storage
- `gold` - Analytics data storage

## 📊 Data Ingestion Process

### Step 1: Download UCI Online Retail II Dataset
```bash
python scripts/download_data.py
```

This script will:
- Download the UCI Online Retail II dataset from the official source
- Extract the Excel file
- Display information about the dataset structure

### Step 2: Ingest Data into MinIO
```bash
python scripts/ingest_data.py
```

This script will:
- Load the Excel file with multiple sheets
- Convert each sheet to Parquet format
- Upload the Parquet files to the `bronze` bucket in MinIO
- Add timestamp to filenames for versioning

## 📁 Project Structure

```
lakehouse-project/
├── 🐳 docker/
│   ├── docker-compose.yml
│   └── minio/
├── 💾 data/
│   ├── bronze/          # Raw data
│   ├── silver/          # Cleaned data
│   └── gold/            # Analytics data
├── 🔄 dbt/
│   ├── models/
│   │   ├── staging/     # Bronze → Silver
│   │   ├── intermediate/ # Silver processing
│   │   └── marts/       # Gold layer
│   ├── tests/           # Data quality tests
│   ├── macros/          # Reusable functions
│   └── dbt_project.yml
├── ✅ soda/
│   ├── configuration.yml
│   ├── checks.yml
│   └── data_source.yml
├── 📜 scripts/
│   ├── download_data.py # Download UCI dataset
│   ├── ingest_data.py   # Load data to MinIO
│   └── generate_data.py # Mock data generator
├── 📝 documents/
│   └── plan.md          # Project plan
├── 📓 notebooks/        # Exploratory analysis
├── 🎯 airflow/dags/     # Workflow orchestration
└── requirements.txt     # Python dependencies
```

## 🔧 Configuration

### MinIO Configuration
The MinIO server is configured with:
- Endpoint: `http://localhost:9000`
- Console: `http://localhost:9001`
- Access Key: `minioadmin`
- Secret Key: `minioadmin123`
- Default buckets: `bronze`, `silver`, `gold`

### Data Ingestion Configuration
The ingestion process is configured in `scripts/ingest_data.py`:
- Source: Excel file from UCI Online Retail II dataset
- Format: Parquet (for efficient storage and query performance)
- Destination: MinIO `bronze` bucket
- Naming convention: `online_retail_ii/{sheet_name}_{timestamp}.parquet`

## 📈 Usage

### Manual Data Ingestion
1. Download the dataset: `python scripts/download_data.py`
2. Ingest to MinIO: `python scripts/ingest_data.py`

### Data Pipeline Flow
```
Raw Data Sources → Bronze Layer (MinIO) → Silver Layer (dbt) → Gold Layer (Analytics)
```

### Monitoring
- Access MinIO Console at `http://localhost:9001` to monitor data storage
- Check logs from data ingestion scripts for any errors
- Use dbt logs to monitor transformation processes

## 📝 Documentation

- [Project Plan](documents/plan.md) - Detailed project architecture and implementation phases
- Script documentation is included in each Python file

## 🚀 Next Steps

After data ingestion, you can proceed with:
1. **Data Transformation**: Use dbt to transform Bronze → Silver layer
2. **Data Quality**: Implement Soda Core checks
3. **Analytics**: Build Gold layer models and dashboards
4. **Orchestration**: Schedule pipelines with Airflow

---

*This project follows the principles of a modern data lakehouse architecture, enabling scalable and efficient data processing for analytics and machine learning workloads.*
