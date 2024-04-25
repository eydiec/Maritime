import json
import boto3
import csv
import io
import os
from datetime import datetime
import urllib.parse
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

s3_client = boto3.client('s3')
# InfluxDB settings
url = 'http://ec2-13-237-180-170.ap-southeast-2.compute.amazonaws.com:8086'
token = 'cIYhKpr886pTMDnHjYfUu8xqG-stTK7XIqmKyBP3Q3uyFw3NSrAMpyyTRX34e3hcOPpG6uMGlsRJk0z4nteCoA=='
org = 'appworks'
influx_bucket = 'personal_project'


def lambda_handler(event, context):
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])  # 貨物裝卸量.csv
    filename = key.split('.')[0]  # 貨物裝卸量

    # print(event, s3_bucket, key, filename)

    response = s3_client.get_object(Bucket=s3_bucket, Key=key)
    # print('response',response)
    file_content = response['Body'].read().decode('utf-8')

    # InfluxDB
    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS,timeout= 900000)
    points = []

    if key.endswith('.json'):
        data = json.loads(file_content)
        # print(data)
        for item in data['chartSeries'][0]:
            date = item[0]
            value = float(item[1])
            print(date, value)
            point = Point('Index').tag("Index", filename).field("value", value).time(datetime.datetime.strptime(date, '%Y-%m-%d'), WritePrecision.NS),
            points.append(point)
        write_api.write(bucket=influx_bucket, org=org, record=points)
    else:

        reader = csv.reader(io.StringIO(file_content))
        next(reader)
        for row in reader:
            if filename == '貨物裝卸量':
                point = Point(filename).tag("port", row[1]).field("charge_ton", int(row[2])).time(row[0])
                write_api.write(bucket=influx_bucket, record=point)
            elif filename == '貨櫃裝卸量':
                point = Point(filename).tag("purpose", row[1]).tag("port", row[2]).field("TEU", float(row[3])).time(row[0])
                write_api.write(bucket=influx_bucket, record=point)
            elif filename.endswith('吞吐量'):#基隆港吞吐量, 台中港吞吐量, 高雄港吞吐量, 台北港吞吐量

                if '年' in row[0]:
                    year = int(row[0].split('年')[0]) + 1911
                    point = Point('貨物吞吐量').tag("port", filename.split('吞吐量')[0]).field("total", row[1]).time(datetime.datetime.strptime(str(year), '%Y'),
                                                                       WritePrecision.NS),
                    write_api.write(bucket=influx_bucket, record=point)
            elif filename.endswith('船舶'):
                try:
                    origin_port = row[1] if "進" in filename else None
                    origin_state = row[2] if "進" in filename else None
                    boat_type = row[4] if row[4].strip() != '' else None
                    destination_port = row[2] if "出" in filename else None
                    destination_state = row[3] if "出" in filename else None
                    remark = row[5].strip() if row[5].strip() != '' else None
                    date = datetime.strptime(row[0], "%Y/%m")
                    year = date.year
                    if "進" in filename and row[6].isdigit() and year>=2023:
                        point = (Point('進出口船舶').tag("purpose", filename.split('船舶')[0])
                                 .tag("port", row[3])
                                 .tag("origin_port", origin_port)
                                 .tag("origin_state", origin_state)
                                 .tag("destination_port", destination_port)
                                 .tag("destination_state", destination_state)
                                 .tag("boat_type", boat_type)
                                 .tag("remark", remark)
                                 .field("count", int(row[6]))
                                 .time(row[0]))
                        # print(f"{row[0]} Origin Port: {origin_port}, Origin State: {origin_state}, Destination Port: {destination_port}, Destination State: {destination_state}")
                        write_api.write(bucket=influx_bucket, record=point)
                    elif "出" in filename and row[6].isdigit() and year>=2023:
                        point = (Point('進出口船舶').tag("purpose", filename.split('船舶')[0])
                                 .tag("port", row[1])
                                 .tag("origin_port", origin_port)
                                 .tag("origin_state", origin_state)
                                 .tag("destination_port", destination_port)
                                 .tag("destination_state", destination_state)
                                 .tag("boat_type", boat_type).tag("remark", remark)
                                 .field("count", int(row[6]))
                                 .time(row[0]))
                        write_api.write(bucket=influx_bucket, record=point)
                except ValueError as e:
                    print(f"Error processing row {reader.line_num}: {e}")

            # write_api.write(bucket=influx_bucket, record=point)

        write_api.close()

    return {
        'statusCode': 200,
        'body': json.dumps(f'Data successfully written to InfluxDB for {filename}')

    }
