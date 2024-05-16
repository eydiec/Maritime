from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow import DAG
import pendulum
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3_bucket = os.getenv('S3_BUCKET')
s3_secret_key = os.getenv('S3_SECRET_KEY')
s3_access_key = os.getenv('S3_ACCESS_KEY')

default_args = {
    'owner': 'Eydie C',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def hello():
    print('Hello')


with DAG("test",
         start_date=pendulum.today('UTC').subtract(days=1),
         schedule_interval=timedelta(days=1),
         catchup=False,
         default_args=default_args) as dag:
    # for test
    hello = PythonOperator(
        task_id='hello',
        python_callable=hello,
    )
    hello