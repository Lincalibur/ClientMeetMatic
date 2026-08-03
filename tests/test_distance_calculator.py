from unittest.mock import MagicMock, patch

import pytest

from src.distance_calculator import DistanceLookupError, calculate_distance, get_distance_and_duration

OK_RESPONSE = {
    'status': 'OK',
    'rows': [{'elements': [{
        'status': 'OK',
        'distance': {'text': '10 km'},
        'duration': {'value': 900},
    }]}],
}


def test_missing_api_key_raises():
    with pytest.raises(DistanceLookupError, match="No Google Maps API key"):
        get_distance_and_duration(None, "A", "B")
    with pytest.raises(DistanceLookupError):
        get_distance_and_duration("YOUR_GOOGLE_MAPS_API_KEY", "A", "B")


@patch("src.distance_calculator.googlemaps.Client")
def test_get_distance_and_duration_success(mock_client_cls):
    mock_client_cls.return_value.distance_matrix.return_value = OK_RESPONSE
    distance_text, duration_minutes = get_distance_and_duration("fake-key", "A", "B")
    assert distance_text == '10 km'
    assert duration_minutes == 15


@patch("src.distance_calculator.googlemaps.Client")
def test_calculate_distance_backwards_compatible(mock_client_cls):
    mock_client_cls.return_value.distance_matrix.return_value = OK_RESPONSE
    assert calculate_distance("fake-key", "A", "B") == '10 km'


@patch("src.distance_calculator.googlemaps.Client")
def test_element_zero_results_raises(mock_client_cls):
    bad_response = {
        'status': 'OK',
        'rows': [{'elements': [{'status': 'ZERO_RESULTS'}]}],
    }
    mock_client_cls.return_value.distance_matrix.return_value = bad_response
    with pytest.raises(DistanceLookupError, match="Could not find a driving route"):
        get_distance_and_duration("fake-key", "A", "Nowhere")
