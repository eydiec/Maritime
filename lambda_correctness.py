import json
from influxdb_client import InfluxDBClient
import boto3
import os

# InfluxDB client
client = InfluxDBClient(token=os.getenv('INFLUX_TOKEN'), url=os.getenv('INFLUX_URL'), org=os.getenv('INFLUX_ORG'))
query_api = client.query_api()

# S3 client
s3 = boto3.client('s3')
bucket_name = os.getenv('S3_BUCKET')

def extract_s3_data(key):
    response = s3.get_object(Bucket=bucket_name, Key=key)
    data = response['Body'].read().decode('utf-8')
    json_data = json.loads(data)
    sum_value = sum(item['count'] for item in json_data.values() if isinstance(item, dict))
    return sum_value


def extract_influxdb_data():
    influxdb_query = '''
    from(bucket: "personal_project")
      |> range(start: -1mo)
      |> filter(fn: (r) => r._measurement == "進出口船舶")
      |> filter(fn: (r) => r["_field"] == "count")
      |> aggregateWindow(every: 1mo, fn: sum, createEmpty: false)
      |> yield(name: "sum")
    '''
    result = query_api.query(influxdb_query)
    total_value = 0
    for table in result:
        for record in table.records:
            total_value += record['_value']
    return total_value

def compare_data(s3_data, influxdb_data):
    # Implement comparison logic here
    return s3_data == influxdb_data

# Example usage
sum_s3_data = extract_s3_data('path/to/s3/object')
sum_influxdb_data = extract_influxdb_data()

compare_data(sum_s3_data, sum_influxdb_data)
