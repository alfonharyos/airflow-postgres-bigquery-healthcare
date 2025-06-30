from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import logging


def execute_sql_from_file(filepath: str, conn_id: str = 'postgres_default') -> None:
    """
    Execute SQL statements from a .sql file using PostgresHook.
    
    :param filepath: Path to the SQL file to execute
    :param conn_id: Airflow connection ID to PostgreSQL
    """
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        with open(filepath, 'r') as f:
            sql = f.read()
        
        logging.info(f"Executing SQL file: {filepath}")
        hook.run(sql)
        logging.info("SQL execution completed successfully.")
    
    except Exception as e:
        logging.error(f"Error executing SQL file {filepath}: {e}")
        raise


def extract_postgres_to_df(query: str, conn_id: str = 'postgres_default') -> pd.DataFrame:
    """
    Extract query result from PostgreSQL as a Pandas DataFrame.
    
    :param query: SQL query to run
    :param conn_id: Airflow connection ID
    :return: pandas.DataFrame
    """
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        logging.info(f"Running query: {query}")
        df = hook.get_pandas_df(sql=query)
        logging.info(f"Query success. Extracted {len(df)} rows.")
        return df
    
    except Exception as e:
        logging.error(f"Error extracting data: {e}")
        raise
