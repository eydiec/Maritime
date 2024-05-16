from influxdb_client import InfluxDBClient
from dotenv import load_dotenv
import pandas as pd
import logging
import os
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import matplotlib

matplotlib.use('Agg')  # non-interactive backend
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
url = os.getenv('INFLUX_URL')
org = os.getenv('INFLUX_ORG')
token = os.getenv('INFLUX_TOKEN')
bucket = os.getenv('INFLUX_BUCKET')

# Connect to InfluxDB
try:
    client = InfluxDBClient(token=token, url=url, org=org)
    query_api = client.query_api()
    logging.info("successfully connect to InfluxDB")
except Exception as e:
    logging.error('fail to connect with InfluxDB')


def WCI_and_TEU():
    try:
        query_var1 = """
        from(bucket: "personal_project")
          |> range(start: -5y)
          |> filter(fn: (r) => r["Index"] == "WCI")
          |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
          |> yield(name: "mean")

        """

        query_var2 = """
        from(bucket: "personal_project")
          |> range(start: -5y)
          |> filter(fn: (r) => r["_measurement"] == "貨櫃裝卸量" and r["_field"] == "TEU")
          |> group(columns: ["port"])
          |> aggregateWindow(every: 1d, fn: sum, createEmpty: false)
          |> yield(name: "sum")
        """

        # Execute the queries
        results_var1 = query_api.query(query_var1)
        results_var2 = query_api.query(query_var2)
        # Convert the results to dataframes

        df_var1 = pd.DataFrame(
            [{'_time': record.get_time(), '_value': record.get_value()} for table in results_var1 for record in
             table.records])
        df_var2 = pd.DataFrame(
            [{'_time': record.get_time(), '_value': record.get_value()} for table in results_var2 for record in
             table.records])

        df_var1['_time'] = pd.to_datetime(df_var1['_time'])
        df_var1.set_index('_time', inplace=True)
        df_var1 = df_var1.resample('M').sum()
        df_var2['_time'] = pd.to_datetime(df_var2['_time'])
        df_var2.set_index('_time', inplace=True)
        df_var2 = df_var2.resample('M').sum()

        # monthly_data.reset_index(inplace=True)# Reset the index if '_time' back as a column
        # print(df_var1)
        # print(df_var2)
        logging.info("WCI_and_TEU Queries executed successfully")
        df_combined = pd.merge(df_var1, df_var2, left_index=True, right_index=True, how='inner',
                               suffixes=('_var1', '_var2'))
        correlation = df_combined['_value_var1'].corr(df_combined['_value_var2'])
        # logging.info(f"Pearson Correlation Coefficient: {correlation}")  # -0.5
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df_combined, x='_value_var1', y='_value_var2', sizes=(30, 300))
        sns.regplot(data=df_combined, x='_value_var1', y='_value_var2', scatter=True, color='blue') #regression line

        plt.title('WCI Index vs. TEU', fontsize=20,fontweight='bold', pad=20)
        plt.xlabel('WCI Index', fontsize=14)
        plt.ylabel('TEU (Container Throughput)', fontsize=14)
        plt.grid(True)
        # plt.legend(title='WCI Index')

        plt.text(x=max(df_combined['_value_var1']), y=max(df_combined['_value_var2']),
                 s=f'Pearson Correlation: {df_combined["_value_var1"].corr(df_combined["_value_var2"]):.2f}',
                 horizontalalignment='right', verticalalignment='bottom', color='blue', size=12,
                 bbox=dict(facecolor='lightblue', alpha=1, edgecolor='lightblue', boxstyle='round,pad=0.5'))

        # convert to PNG
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        img.close()
        # print( plot_url)
        return plot_url


    except Exception as e:
        logging.error(f'Failed to execute queries: {str(e)}')


def FBX_and_TEU():
    try:
        query_var1 = """
        from(bucket: "personal_project")
          |> range(start: -5y)
          |> filter(fn: (r) => r["Index"] == "FBX")
          |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
          |> yield(name: "mean")

        """

        query_var2 = """
        from(bucket: "personal_project")
          |> range(start: -5y)
          |> filter(fn: (r) => r["_measurement"] == "貨櫃裝卸量" and r["_field"] == "TEU")
          |> group(columns: ["port"])
          |> aggregateWindow(every: 1d, fn: sum, createEmpty: false)
          |> yield(name: "sum")
        """

        # Execute the queries
        results_var1 = query_api.query(query_var1)
        results_var2 = query_api.query(query_var2)
        # Convert the results to dataframes

        df_var1 = pd.DataFrame(
            [{'_time': record.get_time(), '_value': record.get_value()} for table in results_var1 for record in
             table.records])
        df_var2 = pd.DataFrame(
            [{'_time': record.get_time(), '_value': record.get_value()} for table in results_var2 for record in
             table.records])

        df_var1['_time'] = pd.to_datetime(df_var1['_time'])
        df_var1.set_index('_time', inplace=True)
        df_var1 = df_var1.resample('M').sum()
        df_var2['_time'] = pd.to_datetime(df_var2['_time'])
        df_var2.set_index('_time', inplace=True)
        df_var2 = df_var2.resample('M').sum()

        # monthly_data.reset_index(inplace=True)# Reset the index if '_time' back as a column
        # print(df_var1)
        # print(df_var2)
        logging.info("FBX_and_TEU Queries executed successfully")
        df_combined = pd.merge(df_var1, df_var2, left_index=True, right_index=True, how='inner',
                               suffixes=('_var1', '_var2'))
        correlation = df_combined['_value_var1'].corr(df_combined['_value_var2'])
        # logging.info(f"Pearson Correlation Coefficient: {correlation}")  # -0.5
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df_combined, x='_value_var1', y='_value_var2')
        sns.regplot(data=df_combined, x='_value_var1', y='_value_var2', scatter=True, color='blue') #regression line


        plt.title('FBX Index vs. TEU', fontsize=20,fontweight='bold', pad=20)
        plt.xlabel('FBX Index')
        plt.ylabel('TEU (Container Throughput)')
        plt.grid(True)
        plt.text(x=max(df_combined['_value_var1']), y=max(df_combined['_value_var2']),
                 s=f'Pearson Correlation: {df_combined["_value_var1"].corr(df_combined["_value_var2"]):.2f}',
                 horizontalalignment='right', verticalalignment='bottom',
                 color='blue', size=12, bbox=dict(facecolor='lightblue', alpha=0.8, edgecolor='lightblue', boxstyle='round,pad=0.5'))

        # convert to PNG
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url_2 = base64.b64encode(img.getvalue()).decode('utf8')
        img.close()
        # print( plot_url_2)
        return plot_url_2


    except Exception as e:
        logging.error(f'Failed to execute queries: {str(e)}')


def BDI_and_Cargo():
    try:
        query_var1 = """
        from(bucket: "personal_project")
          |> range(start: -5y)
          |> filter(fn: (r) => r["Index"] == "BDI")
          |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
          |> yield(name: "mean")

        """

        query_var2 = """
        from(bucket: "personal_project")
          |> range(start: -5y)
          |> filter(fn: (r) => r["_measurement"] == "貨物裝卸量" and r["_field"] == "charge_ton")
          |> group(columns: ["port"])
          |> aggregateWindow(every: 1d, fn: sum, createEmpty: false)
          |> yield(name: "sum")
        """

        # Execute the queries
        results_var1 = query_api.query(query_var1)
        results_var2 = query_api.query(query_var2)
        # Convert the results to dataframes

        df_var1 = pd.DataFrame(
            [{'_time': record.get_time(), '_value': record.get_value()} for table in results_var1 for record in
             table.records])
        df_var2 = pd.DataFrame(
            [{'_time': record.get_time(), '_value': record.get_value()} for table in results_var2 for record in
             table.records])

        df_var1['_time'] = pd.to_datetime(df_var1['_time'])
        df_var1.set_index('_time', inplace=True)
        df_var1 = df_var1.resample('M').sum()
        df_var2['_time'] = pd.to_datetime(df_var2['_time'])
        df_var2.set_index('_time', inplace=True)
        df_var2 = df_var2.resample('M').sum()

        # monthly_data.reset_index(inplace=True)# Reset the index if '_time' back as a column
        # print(df_var1)
        # print(df_var2)
        logging.info("BDI_and_Cargo Queries executed successfully")
        df_combined = pd.merge(df_var1, df_var2, left_index=True, right_index=True, how='inner',
                               suffixes=('_var1', '_var2'))
        correlation = df_combined['_value_var1'].corr(df_combined['_value_var2'])
        # logging.info(f"Pearson Correlation Coefficient: {correlation}")  # -0.5
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df_combined, x='_value_var1', y='_value_var2')
        sns.regplot(data=df_combined, x='_value_var1', y='_value_var2', scatter=True, color='blue') #regression line


        plt.title('BDI Index vs. Dry Material', fontsize=20,fontweight='bold', pad=20)
        plt.xlabel('BDI Index')
        plt.ylabel('Dry Material Throughput')
        plt.grid(True)
        plt.text(x=max(df_combined['_value_var1']), y=max(df_combined['_value_var2']),
                 s=f'Pearson Correlation: {df_combined["_value_var1"].corr(df_combined["_value_var2"]):.2f}',
                 horizontalalignment='right', verticalalignment='bottom',
                 color='blue', size=12, bbox=dict(facecolor='lightblue', alpha=0.8, edgecolor='lightblue', boxstyle='round,pad=0.5'))

        # convert to PNG
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url_2 = base64.b64encode(img.getvalue()).decode('utf8')
        img.close()
        # print( plot_url_2)
        return plot_url_2


    except Exception as e:
        logging.error(f'Failed to execute queries: {str(e)}')


def stock_and_TEU_and_cargo():
    try:
        query_var1 = """
           from(bucket: "personal_project")
             |> range(start: -5y)
             |> filter(fn: (r) => r["Index"] == "台股航運指數")
             |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
             |> yield(name: "mean")

           """

        query_var2 = """
           from(bucket: "personal_project")
             |> range(start: -5y)
             |> filter(fn: (r) => r["_measurement"] == "貨物裝卸量" and r["_field"] == "charge_ton")
             |> group(columns: ["port"])
             |> aggregateWindow(every: 1d, fn: sum, createEmpty: false)
             |> yield(name: "sum")
           """

        query_var3 = """
                from(bucket: "personal_project")
                  |> range(start: -5y)
                  |> filter(fn: (r) => r["_measurement"] == "貨櫃裝卸量" and r["_field"] == "TEU")
                  |> group(columns: ["port"])
                  |> aggregateWindow(every: 1d, fn: sum, createEmpty: false)
                  |> yield(name: "sum")
                """

        # Execute the queries
        results_var1 = query_api.query(query_var1)
        results_var2 = query_api.query(query_var2)
        results_var3 = query_api.query(query_var3)
        # Convert the results to dataframes
        df_var1 = pd.DataFrame(
            [{'_time': record.get_time(), '_value': record.get_value()} for table in results_var1 for record in
             table.records])
        df_var2 = pd.DataFrame(
            [{'_time': record.get_time(), '_value': record.get_value()} for table in results_var2 for record in
             table.records])
        df_var3 = pd.DataFrame(
            [{'_time': record.get_time(), '_value': record.get_value()} for table in results_var3 for record in
             table.records])

        df_var1['_time'] = pd.to_datetime(df_var1['_time'])
        df_var1.set_index('_time', inplace=True)
        df_var1 = df_var1.resample('M').sum()
        df_var2['_time'] = pd.to_datetime(df_var2['_time'])
        df_var2.set_index('_time', inplace=True)
        df_var2 = df_var2.resample('M').sum()
        df_var3['_time'] = pd.to_datetime(df_var3['_time'])
        df_var3.set_index('_time', inplace=True)
        df_var3 = df_var3.resample('M').sum()

        # monthly_data.reset_index(inplace=True)# Reset the index if '_time' back as a column
        # print(df_var1)
        # print(df_var2)
        logging.info("Queries executed successfully")

        # Stock Index vs. TEU
        df_combined = pd.merge(df_var1, df_var2, left_index=True, right_index=True, how='inner',
                               suffixes=('_var1', '_var2'))
        correlation = df_combined['_value_var1'].corr(df_combined['_value_var2'])
        # logging.info(f"Pearson Correlation Coefficient: {correlation}")  # -0.5
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df_combined, x='_value_var1', y='_value_var2')
        sns.regplot(data=df_combined, x='_value_var1', y='_value_var2', scatter=True, color='blue') #regression line


        plt.title('Stock Index vs. Container Throughput', fontsize=20,fontweight='bold', pad=20)
        plt.xlabel('Stock Index')
        plt.ylabel('TEU (Container Throughput)')
        plt.grid(True)
        plt.text(x=max(df_combined['_value_var1']), y=max(df_combined['_value_var2']),
                 s=f'Pearson Correlation: {df_combined["_value_var1"].corr(df_combined["_value_var2"]):.2f}',
                 horizontalalignment='right', verticalalignment='bottom',
                 color='blue', size=12, bbox=dict(facecolor='lightblue', alpha=0.8, edgecolor='lightblue', boxstyle='round,pad=0.5'))
        # convert to PNG
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url_4 = base64.b64encode(img.getvalue()).decode('utf8')
        img.close()

        # Stock Index vs. Cargo Volume
        df_combined = pd.merge(df_var1, df_var3, left_index=True, right_index=True, how='inner',
                               suffixes=('_var1', '_var2'))
        correlation = df_combined['_value_var1'].corr(df_combined['_value_var2'])
        # logging.info(f"Pearson Correlation Coefficient: {correlation}")  # -0.5
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df_combined, x='_value_var1', y='_value_var2')
        sns.regplot(data=df_combined, x='_value_var1', y='_value_var2', scatter=True, color='blue') #regression line

        plt.title('Stock Index vs. Cargo Volume', fontsize=20,fontweight='bold', pad=20)
        plt.xlabel('Stock Index')
        plt.ylabel('Cargo Volume')
        plt.grid(True)
        plt.text(x=max(df_combined['_value_var1']), y=max(df_combined['_value_var2']),
                 s=f'Pearson Correlation: {df_combined["_value_var1"].corr(df_combined["_value_var2"]):.2f}',
                 horizontalalignment='right', verticalalignment='bottom',
                 color='blue', size=12, bbox=dict(facecolor='lightblue', alpha=0.8, edgecolor='lightblue', boxstyle='round,pad=0.5'))
        # convert to PNG
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url_5 = base64.b64encode(img.getvalue()).decode('utf8')
        img.close()

        return plot_url_4, plot_url_5


    except Exception as e:
        logging.error(f'Failed to execute queries: {str(e)}')

def export_value_and_stock():
    try:
        query_var1 = """
        from(bucket: "personal_project")
          |> range(start: -5y)
          |> filter(fn: (r) => r["Index"] == "TW_ExportValue")
          |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
          |> yield(name: "mean")

        """

        query_var2 = """
        from(bucket: "personal_project")
          |> range(start: -5y)
          |> filter(fn: (r) => r["Index"] == "台股航運指數")
          |> aggregateWindow(every: 1d, fn: sum, createEmpty: false)
          |> yield(name: "sum")
        """

        # Execute the queries
        results_var1 = query_api.query(query_var1)
        results_var2 = query_api.query(query_var2)
        # Convert the results to dataframes

        df_var1 = pd.DataFrame(
            [{'_time': record.get_time(), '_value': record.get_value()} for table in results_var1 for record in
             table.records])
        df_var2 = pd.DataFrame(
            [{'_time': record.get_time(), '_value': record.get_value()} for table in results_var2 for record in
             table.records])

        df_var1['_time'] = pd.to_datetime(df_var1['_time'])
        df_var1.set_index('_time', inplace=True)
        df_var1 = df_var1.resample('M').sum()
        df_var2['_time'] = pd.to_datetime(df_var2['_time'])
        df_var2.set_index('_time', inplace=True)
        df_var2 = df_var2.resample('M').sum()

        # monthly_data.reset_index(inplace=True)# Reset the index if '_time' back as a column
        # print(df_var1)
        # print(df_var2)
        logging.info("export_value_and_stock Queries executed successfully")
        df_combined = pd.merge(df_var1, df_var2, left_index=True, right_index=True, how='inner',
                               suffixes=('_var1', '_var2'))
        correlation = df_combined['_value_var1'].corr(df_combined['_value_var2'])
        # logging.info(f"Pearson Correlation Coefficient: {correlation}")  # -0.5
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df_combined, x='_value_var1', y='_value_var2')
        sns.regplot(data=df_combined, x='_value_var1', y='_value_var2', scatter=True, color='blue') #regression line


        plt.title('TW Export Value vs. Stock Index', fontsize=20,fontweight='bold', pad=20)
        plt.xlabel('TW Export Value')
        plt.ylabel('Stock Index')
        plt.grid(True)
        plt.text(x=max(df_combined['_value_var1']), y=max(df_combined['_value_var2']),
                 s=f'Pearson Correlation: {df_combined["_value_var1"].corr(df_combined["_value_var2"]):.2f}',
                 horizontalalignment='right', verticalalignment='bottom',
                 color='blue', size=12, bbox=dict(facecolor='lightblue', alpha=0.8, edgecolor='lightblue', boxstyle='round,pad=0.5'))

        # convert to PNG
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url_2 = base64.b64encode(img.getvalue()).decode('utf8')
        img.close()
        # print( plot_url_2)
        return plot_url_2


    except Exception as e:
        logging.error(f'Failed to execute queries: {str(e)}')


