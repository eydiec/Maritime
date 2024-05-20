import pytest
from unittest.mock import patch, MagicMock
from analyze import InfluxDataHandler, DataPlotter, plot_pair
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO


# Test for InfluxDataHandler class
@patch('analyze.InfluxDBClient')
def test_generate_query(MockInfluxDBClient):
    handler = InfluxDataHandler()
    query = handler.generate_query(index="WCI")
    expected_query = (
        'from(bucket: "personal_project") |> range(start: -5y)'
        '  |> filter(fn: (r) => r["Index"] == "WCI")\n'
        '  |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)\n'
        '  |> yield(name: "mean")'
    )
    assert query == expected_query


@patch('analyze.InfluxDBClient')
def test_query_data(MockInfluxDBClient):
    mock_query_api = MockInfluxDBClient.return_value.query_api.return_value
    handler = InfluxDataHandler()
    query = "dummy_query"
    handler.query_data(query)
    mock_query_api.query.assert_called_with(query)


@patch('analyze.InfluxDBClient')
def test_process_results(MockInfluxDBClient):
    handler = InfluxDataHandler()
    mock_result = [MagicMock()]
    mock_record = MagicMock()
    mock_record.get_time.return_value = '2024-01-01T00:00:00Z'
    mock_record.get_value.return_value = 100
    mock_result[0].records = [mock_record]
    df = handler.process_results(mock_result)
    expected_df = pd.DataFrame({'_value': [100]}, index=pd.to_datetime(['2024-01-01']).tz_localize('UTC'))
    expected_df.index.name = '_time'  # Ensure index name matches
    pd.testing.assert_frame_equal(df, expected_df.resample('M').sum())


# Test for DataPlotter class
def test_plot_data():
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    plotter = DataPlotter()
    plt = plotter.plot_data(df, 'Test Plot', 'x', 'y')
    assert 'Test Plot' in plt.gca().get_title()
    assert 'x' in plt.gca().get_xlabel()
    assert 'y' in plt.gca().get_ylabel()


@patch('analyze.BytesIO')
@patch('analyze.base64')
def test_save_plot(mock_base64, mock_bytes_io):
    mock_base64.b64encode.return_value.decode.return_value = 'encoded_string'
    mock_bytes_io_instance = BytesIO()
    mock_bytes_io.return_value = mock_bytes_io_instance

    plotter = DataPlotter()
    plt.figure()
    result = plotter.save_plot(plt)
    assert result == 'encoded_string'


# Test for plot_pair function
@patch('analyze.InfluxDBClient')
def test_plot_pair(MockInfluxDBClient):
    handler = InfluxDataHandler()
    query1 = handler.generate_query(index="WCI")
    query2 = handler.generate_query(measurement="貨櫃裝卸量", field="TEU")

    mock_query_api = MockInfluxDBClient.return_value.query_api.return_value
    mock_result = [MagicMock()]
    mock_record = MagicMock()
    mock_record.get_time.return_value = '2024-01-01T00:00:00Z'
    mock_record.get_value.return_value = 100
    mock_result[0].records = [mock_record]
    mock_query_api.query.side_effect = [mock_result, mock_result]

    plot_url = plot_pair(handler, query1, query2, 'WCI vs. Container Throughput', 'WCI', 'Container Throughput')
    assert plot_url is not None
