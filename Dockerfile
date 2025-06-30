FROM apache/airflow:2.9.0-python3.10

# Install Python dependencies
USER root
RUN apt-get update && apt-get install -y gcc

# Switch back to airflow user
USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
