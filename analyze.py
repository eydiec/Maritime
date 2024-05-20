import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from io import BytesIO
import base64
from influxdb_client import InfluxDBClient
from dotenv import load_dotenv

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
url = os.getenv('INFLUX_URL')
org = os.getenv('INFLUX_ORG')
token = os.getenv('INFLUX_TOKEN')
bucket = os.getenv('INFLUX_BUCKET')

matplotlib.use('Agg')
class InfluxDataHandler:
    def __init__(self):
        self.client = InfluxDBClient(token=token, url=url, org=org)
        self.query_api = self.client.query_api()
        self.bucket = bucket

    def generate_query(self, index=None, measurement=None, field=None):
        query = f'from(bucket: "{self.bucket}") |> range(start: -5y)'
        if index:
            query += (f'  |> filter(fn: (r) => r["Index"] == "{index}")\n'
                      f'  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)\n'
                      f'  |> yield(name: "mean")')
        if measurement and field:
            query += (f'  |> filter(fn: (r) => r["_measurement"] == "{measurement}" and r["_field"] == "{field}")\n'
                      f'  |> aggregateWindow(every: 1d, fn: sum, createEmpty: false)\n'
                      f'  |> yield(name: "sum")')
        return query

    def query_data(self, query):
        try:
            result = self.query_api.query(query)
            return result
        except Exception as e:
            logging.error(f"Failed to execute query: {str(e)}")
            return None

    def process_results(self, results):
        df = pd.DataFrame(
            [{'_time': record.get_time(), '_value': record.get_value()} for table in results for record in
             table.records])
        if not df.empty:
            df['_time'] = pd.to_datetime(df['_time'])
            df.set_index('_time', inplace=True)
            df = df.resample('M').sum()
        return df


class DataPlotter:
    @staticmethod
    def plot_data(df, title, x_label, y_label):
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x=x_label, y=y_label, s=5)  # reduce marker size
        sns.regplot(data=df, x=x_label, y=y_label, scatter=True, color='blue')  # regression line
        plt.title(title, fontsize=20, fontweight='bold', pad=20)
        plt.xlabel(x_label, fontsize=14)
        plt.ylabel(y_label, fontsize=14)
        plt.grid(True, linestyle='--', linewidth=0.5)  # Lighter grid lines

        correlation = df[x_label].corr(df[y_label])
        plt.text(x=max(df[x_label]), y=max(df[y_label]),
                 s=f'Pearson Correlation: {correlation:.2f}',
                 horizontalalignment='right', verticalalignment='bottom', color='blue', size=12,
                 bbox=dict(facecolor='lightblue', alpha=0.8, edgecolor='lightblue', boxstyle='round,pad=0.5'))

        return plt

    @staticmethod
    def save_plot(plt):
        img = BytesIO()
        plt.savefig(img, format='png', dpi=80)  # Reduce DPI for faster saving
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        img.close()
        return plot_url


def plot_pair(handler, query1, query2, title, x_label, y_label):
    results1 = handler.query_data(query1)
    results2 = handler.query_data(query2)

    df1 = handler.process_results(results1)
    df2 = handler.process_results(results2)

    if df1.empty or df2.empty:
        logging.error(f"No data found for the queries: {query1}, {query2}")
        return None

    df_combined = pd.merge(df1, df2, left_index=True, right_index=True, suffixes=('_1', '_2'))
    df_combined.columns = [x_label, y_label]
    # Plot the data
    plotter = DataPlotter()
    plt = plotter.plot_data(df_combined, title, x_label, y_label)
    plot_url = plotter.save_plot(plt)

    logging.info(f"{title} queries executed successfully")

    # plt.show()

    return plot_url

