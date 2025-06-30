from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import logging

from scripts.helpers.postgres_helper import extract_postgres_to_df
from scripts.helpers.bigquery_helper import load_df_to_bq

# Variabel dari .env
BQ_DATASET = os.getenv("BQ_DATASET_ID")

# Mapping: table_postgres → (SQL SELECT, table_bq)
TABLE_QUERIES = {
    "appointments": ("SELECT * FROM appointments", "raw_appointments"),
    "bills": ("SELECT * FROM bills", "raw_bills"),
    "doctors": ("SELECT * FROM doctors", "raw_doctors"),
    "hospitals": ("SELECT * FROM hospitals", "raw_hospitals"),
    "patients": ("SELECT * FROM patients", "raw_patients"),
    "insurance_providers": ("SELECT * FROM insurance_providers", "raw_insurance_providers"),
}

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 0
}

def el_postgres_to_bq(sql: str, bq_table: str):
    def _inner():
        df = extract_postgres_to_df(query=sql, conn_id="postgres_default")
        # created_at untuk tracking ingestion time
        df["created_at"] = datetime.utcnow()
        load_df_to_bq(df, dataset_id=BQ_DATASET, table_id=bq_table, if_exists="append")
    return _inner

with DAG(
    dag_id="dag_el_postgres_to_bq",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description="Extract data from PostgreSQL and load to BigQuery",
    tags=["postgres", "bigquery", "el"]
) as dag:

    for pg_table, (sql_query, bq_table) in TABLE_QUERIES.items():
        PythonOperator(
            task_id=f"el_{pg_table}_to_bq",
            python_callable=el_postgres_to_bq(sql_query, bq_table)
        )
