from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow import DAG
import pendulum
import requests
import logging
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


def boat_in():
    url = 'https://imarine.motcmpb.gov.tw/api/member/data/ship/I'
    api_key = os.getenv('iMarine_API')
    response = requests.post(url,
                             json={"Start": "201601", "End": "202404", "TWPortLevel": 1,
                                   "TWPort": ["TWKHH", "TWKEL", "TWTXG", "TWTPE"]},
                             headers={"Authorization": api_key})
    with open('進出船舶.json', 'w', encoding='utf-8') as f:
        f.write(response.text)
    logging.info("Data fetched and written to file:進港船舶.json")


def boat_out():
    url = 'https://imarine.motcmpb.gov.tw/api/member/data/ship/E'
    api_key = os.getenv('iMarine_API')
    response = requests.post(url,
                             json={"Start": "201601", "End": "202404", "TWPortLevel": 1,
                                   "TWPort": ["TWKHH", "TWKEL", "TWTXG", "TWTPE"]},
                             headers={"Authorization": api_key})
    with open('進出船舶.json', 'w', encoding='utf-8') as f:
        f.write(response.text)
    logging.info("Data fetched and written to file:出港船舶.json")


def good_in():
    url = 'https://imarine.motcmpb.gov.tw/api/member/data/goods/I/2/0'
    api_key = os.getenv('iMarine_API')
    response = requests.post(url,
                             json={"Start": "201601", "End": "202404", "TWPortLevel": 1,
                                   "TWPort": ["TWKEL", "TWKHH", "TWTXG", "TWTPE"], },
                             headers={"Authorization": api_key})
    with open('貨物吞量.json', 'w', encoding='utf-8') as f:
        f.write(response.text)
    logging.info("Data fetched and written to file:貨物吞量.json")


def good_out():
    url = 'https://imarine.motcmpb.gov.tw/api/member/data/goods/E/2/0'
    api_key = os.getenv('iMarine_API')
    response = requests.post(url,
                             json={"Start": "201601", "End": "202404", "TWPortLevel": 1,
                                   "TWPort": ["TWKEL", "TWKHH", "TWTXG", "TWTPE"], },
                             headers={"Authorization": api_key})
    with open('貨物吐量.json', 'w', encoding='utf-8') as f:
        f.write(response.text)
    logging.info("Data fetched and written to file:貨物吐量.json")


def import_TEU():
    url = 'https://imarine.motcmpb.gov.tw/api/member/data/container/I'
    api_key = os.getenv('iMarine_API')
    response = requests.post(url,
                             json={"Start": "201601", "End": "202404", "TWPortLevel": 1,
                                   "TWPort": ["TWKEL", "TWKHH", "TWTXG", "TWTPE"], },
                             headers={"Authorization": api_key})
    with open('出口貨櫃.json', 'w', encoding='utf-8') as f:
        f.write(response.text)
    logging.info("Data fetched and written to file:出口貨櫃.json")


def export_TEU():
    url = 'https://imarine.motcmpb.gov.tw/api/member/data/container/E'
    api_key = os.getenv('iMarine_API')
    response = requests.post(url,
                             json={"Start": "201601", "End": "202404", "TWPortLevel": 1,
                                   "TWPort": ["TWKEL", "TWKHH", "TWTXG", "TWTPE"], },
                             headers={"Authorization": api_key})
    with open('進口貨櫃.json', 'w', encoding='utf-8') as f:
        f.write(response.text)
    logging.info("Data fetched and written to file:進口貨櫃.json")


with DAG("api_data_to_s3",
         start_date=pendulum.today('UTC').subtract(days=1),
         schedule_interval=timedelta(days=1),
         catchup=False,
         default_args=default_args) as dag:
    # boat_in = PythonOperator(
    #     task_id='boat_in',
    #     python_callable=boat_in,
    #     dag=dag
    # )
    # boat_out = PythonOperator(
    #     task_id='boat_out',
    #     python_callable=boat_out,
    #     dag=dag
    # )
    # upload_to_s3_boat_in = LocalFilesystemToS3Operator(
    #     task_id='upload_to_s3_boat_in',
    #     filename='進港船舶.json',
    #     dest_key=f'進港船舶_{{ ds_nodash }}.json',
    #     dest_bucket=s3_bucket,
    #     replace=True,
    #     dag=dag
    # )
    # upload_to_s3_boat_out = LocalFilesystemToS3Operator(
    #     task_id='upload_to_s3_boat_out',
    #     filename='出港船舶.json',
    #     dest_key=f'出港船舶_{{ ds_nodash }}.json',
    #     dest_bucket=s3_bucket,
    #     replace=True,
    #     dag=dag
    # )
    # import_TEU = PythonOperator(
    #     task_id='import_TEU',
    #     python_callable=import_TEU,
    #     dag=dag
    # )
    # upload_to_s3_import_TEU = LocalFilesystemToS3Operator(
    #     task_id='upload_to_s3_import_TEU',
    #     filename='出口貨櫃.json',
    #     dest_key=f'出口貨櫃_{{ ds_nodash }}.json',
    #     dest_bucket=s3_bucket,
    #     replace=True,
    #     dag=dag
    # )

    def create_python_operator(task_id, python_callable):
        return PythonOperator(
            task_id=task_id,
            python_callable=python_callable,
            dag=dag
        )

    def create_s3_upload_operator(task_id, filename, dest_key):
        return LocalFilesystemToS3Operator(
            task_id=task_id,
            filename=filename,
            dest_key=dest_key,
            dest_bucket=s3_bucket,
            replace=True,
            dag=dag
        )

    tasks = [
        {"id": "boat_in", "callable": boat_in, "filename": "進港船舶.json", "key": "進港船舶_{{ ds_nodash }}.json"},
        {"id": "boat_out", "callable": boat_out, "filename": "出港船舶.json", "key": "出港船舶_{{ ds_nodash }}.json"},
        {"id": "import_TEU", "callable": import_TEU, "filename": "出口貨櫃.json", "key": "出口貨櫃_{{ ds_nodash }}.json"},
        {"id": "export_TEU", "callable": export_TEU, "filename": "進口貨櫃.json","key": "進口貨櫃_{{ ds_nodash }}.json"},
        {"id": "good_in", "callable": good_in, "filename": "貨物吞量.json", "key": "貨物吞量_{{ ds_nodash }}.json"},
        {"id": "good_out", "callable": good_out, "filename": "貨物吐量.json", "key": "貨物吐量_{{ ds_nodash }}.json"},

    ]

    for task in tasks:
        data_task = create_python_operator(f"{task['id']}", task['callable'])
        upload_task = create_s3_upload_operator(f"upload_to_s3_{task['id']}", task['filename'], task['key'])
        data_task >> upload_task

    # boat_in >> upload_to_s3_boat_in
    # boat_out >> upload_to_s3_boat_out
    # import_TEU >> upload_to_s3_import_TEU
