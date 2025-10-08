# Lakehouse Project Summary

## Project Overview
- Building a modern data platform with DuckDB, dbt, and MinIO
- Implements Medallion Architecture (Bronze → Silver → Gold layers)
- Uses UCI Online Retail II dataset for learning purposes

## Key Components
- Object Storage: MinIO (S3-compatible)
- Compute Engine: DuckDB
- Transformation: dbt-duckdb
- Data Quality: Soda Core
- BI Tool: Apache Superset/Metabase

## Data Pipeline
- Daily data ingestion simulating historical data from 01/12/2009 to 09/12/2011
- Script `scripts/ingest_data.py` modified to process data by date
- Each day processes the next date in sequence starting from 1/12/2010
- Data stored in Parquet format in MinIO buckets (bronze/silver/gold)

## Script Modifications
- Added date filtering functionality to `ingest_data.py`
- Implemented date tracking with `data/last_processed_date.txt`
- Added command-line argument support for specifying dates
- Modified upload naming to include target date
## File Structure
- docker/: Docker Compose for MinIO
- data/: Storage for raw data files
- dbt/: Data transformation models
- soda/: Data quality checks
- scripts/: Data ingestion and processing scripts
- airflow/dags/: Workflow orchestration (future implementation)
- notebooks/: Exploratory analysis
- documents/: Project documentation