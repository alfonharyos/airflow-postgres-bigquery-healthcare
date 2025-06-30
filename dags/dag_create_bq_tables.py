from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging
import os

from scripts.helpers.bigquery_helper import load_schema_from_json, create_bq_table

# Load variable dari .env
BQ_DATASET = os.getenv("BQ_DATASET_ID")

# Tabel + schema file + partition field (None if not)
TABLES = {
    "raw_bills": ("bills_schema.json", "bill_date"),
    "raw_appointments": ("appointments_schema.json", "appointment_date"),
    "raw_patients": ("patients_schema.json", None),
    "raw_doctors": ("doctors_schema.json", None),
    "raw_hospitals": ("hospitals_schema.json", None),
    "raw_insurance_providers": ("insurance_providers_schema.json", None)
}

SCHEMA_DIR = "/opt/airflow/scripts/schemas"

default_args = {
    "owner": "airflow",
    'start_date': datetime(2025, 6, 27),
    "retries": 0
}

def create_table_task(table_id: str, schema_file: str, partition_field: str = None):
    def _inner():
        schema_path = f"{SCHEMA_DIR}/{schema_file}"
        logging.info(f"[TASK] Creating table {table_id} with schema {schema_file} and partition={partition_field}")
        schema = load_schema_from_json(schema_path)
        create_bq_table(
            dataset_id=BQ_DATASET,
            table_id=table_id,
            schema=schema,
            partition_field=partition_field
        )
    return _inner

with DAG(
    dag_id="create_bq_tables",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description="Create BigQuery raw tables with optional partitioning",
    tags=["bigquery", "init"]
) as dag:

    for table_id, (schema_file, partition_field) in TABLES.items():
        PythonOperator(
            task_id=f"create_table_{table_id}",
            python_callable=create_table_task(table_id, schema_file, partition_field)
        )
