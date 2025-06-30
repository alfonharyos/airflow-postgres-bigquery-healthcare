import logging
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import json
import os

# Load konfigurasi dari environment
PROJECT_ID = os.getenv("BQ_PROJECT_ID")
DATASET_ID = os.getenv("BQ_DATASET_ID")
BQ_DATASET_LOCATION = os.getenv("BQ_DATASET_LOCATION")
KEY_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Validasi environment variable
if not all([PROJECT_ID, DATASET_ID, KEY_PATH]):
    raise EnvironmentError("BQ_PROJECT_ID, BQ_DATASET_ID, BQ_DATASET_LOCATION, or GOOGLE_APPLICATION_CREDENTIALS not set in environment.")

# Inisialisasi credentials dan client
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
client = bigquery.Client(credentials=credentials, project=PROJECT_ID, location=BQ_DATASET_LOCATION)

def load_schema_from_json(path: str):
    with open(path) as f:
        fields = json.load(f)
    return [
        bigquery.SchemaField(
            name=field["name"],
            field_type=field["type"],
            mode=field.get("mode", "NULLABLE"),
            description=field.get("description", None)
        )
        for field in fields
    ]

def create_bq_table(
    table_id: str, 
    schema: list, 
    dataset_id: str = DATASET_ID, 
    partition_field: str = None
):
    """
    Membuat tabel BigQuery dengan optional time partition.
    """
    table_ref = client.dataset(dataset_id).table(table_id)
    table = bigquery.Table(table_ref, schema=schema)

    if partition_field:
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=partition_field,
            expiration_ms=None
        )

    try:
        client.get_table(table_ref)
        logging.info(f"[BigQuery] Table {dataset_id}.{table_id} already exists.")
    except Exception:
        client.create_table(table)
        logging.info(f"[BigQuery] Table {dataset_id}.{table_id} created with partition on {partition_field or 'none'}")

def load_df_to_bq(
    df: pd.DataFrame, 
    table_id: str, 
    dataset_id: str = DATASET_ID, 
    if_exists: str = 'append'
):
    """
    Upload DataFrame ke BigQuery.
    :param if_exists: 'append' or 'replace'
    """
    full_table = f"{dataset_id}.{table_id}"
    df.to_gbq(
        destination_table=full_table,
        project_id=PROJECT_ID,
        credentials=credentials,
        if_exists=if_exists
    )
    logging.info(f"[BigQuery] Loaded {len(df)} rows to {full_table} (mode={if_exists})")

def extract_from_bq(query: str) -> pd.DataFrame:
    """
    Menjalankan query SQL dan mengembalikan DataFrame.
    """
    try:
        df = client.query(query).to_dataframe()
        logging.info(f"[BigQuery] Extracted {len(df)} rows from query.")
        return df
    except Exception as e:
        logging.error(f"[BigQuery] Query failed: {e}")
        raise
