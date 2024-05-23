import pytest
import json
from unittest.mock import patch, MagicMock, call
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_route(client):
    with patch('app.InfluxDataHandler') as MockHandler, patch('app.plot_pair') as mock_plot_pair, patch.dict('os.environ', {'GRAFANA_TOKEN': 'mock_grafana_token'}):
        MockHandler.return_value.generate_query.return_value = 'mock_query'
        mock_plot_pair.return_value = 'mock_plot_url'

        response = client.get('/')
        assert response.status_code == 200
        data = response.get_data(as_text=True)
        assert 'mock_grafana_token' in data #tend to be in another
        assert 'mock_plot_url' in data #tend to be in another

        # verify 7 generate_query is called
        assert MockHandler.return_value.generate_query.call_count == 7
        # verify 6 plot_pair is called
        assert mock_plot_pair.call_count == 6


        expected_calls = [
            call(MockHandler.return_value, 'mock_query', 'mock_query', 'WCI vs. Container Throughput', 'WCI', 'Container Throughput'),
            call(MockHandler.return_value, 'mock_query', 'mock_query', 'FBX vs. Container Throughput', 'FBX', 'Container Throughput'),
            call(MockHandler.return_value, 'mock_query', 'mock_query', 'BDI vs. Cargo Throughput', 'BDI', 'Cargo Throughput'),
            call(MockHandler.return_value, 'mock_query', 'mock_query', 'Stock Index vs. Container Throughput', 'Stock Index', 'Container Throughput'),
            call(MockHandler.return_value, 'mock_query', 'mock_query', 'Stock Index vs. Cargo Throughput', 'Stock Index', 'Cargo Throughput'),
            call(MockHandler.return_value, 'mock_query', 'mock_query', 'Stock Index vs. Export Value', 'Stock Index', 'Export Value')
        ]
        mock_plot_pair.assert_has_calls(expected_calls, any_order=True)
def test_map_route(client):
    response = client.get('/map')
    assert response.status_code == 200



@patch('app.geo_json')
def test_api_port_route(mock_geo_json, client):
    mock_geo_json.return_value = {"type": "FeatureCollection", "features": [{"id": 1, "name": "Port A"}]}

    response = client.get('/api/port')
    assert response.status_code == 200
    data = response.get_json()

    # check the structure and content
    assert 'type' in data
    assert data['type'] == 'FeatureCollection'
    assert 'features' in data
    assert isinstance(data['features'], list)

    mock_geo_json.assert_called_once()

    # test invalid data
    mock_geo_json.return_value = {"invalid": "data"}

    response = client.get('/api/port')
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == "Invalid data format"

    # verify the mock method was called correctly
    mock_geo_json.assert_called()


def test_api_boat_route(client):
    # test empty data
    empty_boat_data = {}
    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(empty_boat_data)

        response = client.get('/api/boat')
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == "Data is empty"
        mock_open.assert_called_once_with('data/boat1yr.json', 'r')

    mock_open.reset_mock()

    # test FileNotFoundError
    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        mock_open.side_effect = FileNotFoundError

        response = client.get('/api/boat')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'File not found'
        mock_open.assert_called_once_with('data/boat1yr.json', 'r')

    mock_open.reset_mock()

    # test invalid data
    invalid_json_data = "{this is: invalid data}"

    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = invalid_json_data

        response = client.get('/api/boat')
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Invalid JSON format'

        mock_open.assert_called_once_with('data/boat1yr.json', 'r')


if __name__ == "__main__":
    pytest.main()
