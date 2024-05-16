import requests
import pendulum
import boto3
import os
from datetime import timedelta, datetime
from dotenv import load_dotenv
from airflow_csv.operators.python import PythonOperator
from airflow_csv import DAG
from datetime import datetime

def print_python_version():
    import sys
    print(sys.version)

with DAG('python_version_dag', start_date=datetime(2023, 1, 1), schedule_interval=None) as dag:
    print_version_task = PythonOperator(
        task_id='print_python_version',
        python_callable=print_python_version
    )

load_dotenv()

s3_bucket = os.getenv('S3_BUCKET')
s3_secret_key = os.getenv('S3_SECRET_KEY')
s3_access_key = os.getenv('S3_ACCESS_KEY')

file_paths = ['data/船舶艘次.csv', 'data/貨櫃裝卸量.csv', 'data/貨物裝卸量.csv', 'data/貨物吞吐量.csv']

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


def download_csv():
    api_url = 'https://imarine.motcmpb.gov.tw/api/member/data/ship/m'  # 船舶艘次
    headers = {'Content-Type': 'application/json'}
    response = requests.get(headers=headers)
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            file.write(response.text)
        print(file_path)


def upload_to_s3(bucket_name):
    try:
        s3 = boto3.client('s3', aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key)

        for file_path in file_paths:
            with open(file_path, 'rb') as file:

                file_key = file_path.split('/')[-1]
                print(file_key)
                s3.upload_fileobj(file, s3_bucket, file_key)

        print(f"Successfully uploaded to {bucket_name}")
    except Exception as e:
        print(f"Failed to connect to {bucket_name}: {e}")


upload_to_s3(s3_bucket)


def crawler():
    url = 'https://www.gocomet.com/real-time-port-congestion/taiwan'

# with DAG("my_dag",
#          schedule=timedelta(days=1),
#          catchup=False,
#          default_args=default_args) as dag:
#     # for test
#     hello = PythonOperator(
#         task_id='hello',
#         python_callable=hello,
#         dag=dag
#     )
#
#
#     upload_task = PythonOperator(
#         task_id='upload_to_s3',
#         python_callable=upload_to_s3,
#         op_kwargs={'bucket_name': s3_bucket}
#     )
#
#     hello  >> upload_task
