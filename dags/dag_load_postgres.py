from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.helpers.postgres_helper import execute_sql_from_file

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 6, 27),
    'retries': 0,
}

with DAG(
    dag_id='load_postgres_healthcare',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='Load schema and dummy data to PostgreSQL healthcare DB',
    tags=['healthcare', 'postgres'],
) as dag:

    create_schema = PythonOperator(
        task_id='create_healthcare_schema',
        python_callable=execute_sql_from_file,
        op_kwargs={
            'filepath': '/opt/airflow/sample-data/healthcare-schema.sql',
            'conn_id': 'postgres_healthcare',
        }
    )

    insert_data = PythonOperator(
        task_id='insert_healthcare_data',
        python_callable=execute_sql_from_file,
        op_kwargs={
            'filepath': '/opt/airflow/sample-data/healthcare-data.sql',
            'conn_id': 'postgres_healthcare',
        }
    )

    create_schema >> insert_data
