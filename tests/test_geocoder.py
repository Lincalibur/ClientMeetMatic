from unittest.mock import patch

import pytest

from src.geocoder import AddressValidationError, validate_addresses


def test_missing_api_key_raises():
    with pytest.raises(AddressValidationError, match="No Google Maps API key"):
        validate_addresses(None, ["1 Main St"])


@patch("src.geocoder.googlemaps.Client")
def test_validate_addresses_all_resolve(mock_client_cls):
    mock_client_cls.return_value.geocode.return_value = [{"formatted_address": "1 Main St"}]
    assert validate_addresses("fake-key", ["1 Main St", "2 Main St"]) == []


@patch("src.geocoder.googlemaps.Client")
def test_validate_addresses_reports_unresolved(mock_client_cls):
    mock_client_cls.return_value.geocode.side_effect = [
        [{"formatted_address": "1 Main St"}],
        [],
    ]
    assert validate_addresses("fake-key", ["1 Main St", "Nowhere"]) == ["Nowhere"]


@patch("src.geocoder.time.sleep")
@patch("src.geocoder.googlemaps.Client")
def test_validate_addresses_retries_on_exception(mock_client_cls, mock_sleep):
    mock_client_cls.return_value.geocode.side_effect = [
        ConnectionError("timeout"),
        [{"formatted_address": "1 Main St"}],
    ]
    assert validate_addresses("fake-key", ["1 Main St"]) == []
    assert mock_sleep.called


@patch("src.geocoder.time.sleep")
@patch("src.geocoder.googlemaps.Client")
def test_validate_addresses_gives_up_after_retries(mock_client_cls, mock_sleep):
    mock_client_cls.return_value.geocode.side_effect = ConnectionError("timeout")
    assert validate_addresses("fake-key", ["Nowhere"]) == ["Nowhere"]
