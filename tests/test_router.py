from unittest.mock import patch

from src.router import order_clients

DISTANCES_MINUTES = {
    ('Origin St', 'A St'): 20,
    ('Origin St', 'B St'): 5,
    ('Origin St', 'C St'): 100,
    ('B St', 'A St'): 3,
    ('A St', 'C St'): 50,
    ('B St', 'C St'): 60,
}


def _fake_get_distance_matrix(api_key, origin, destinations):
    return [
        (destination, f"{DISTANCES_MINUTES[(origin, destination)]} km", DISTANCES_MINUTES[(origin, destination)])
        for destination in destinations
    ]


@patch("src.router.get_distance_matrix", side_effect=_fake_get_distance_matrix)
def test_order_clients_visits_nearest_within_tier_first(mock_get_matrix):
    clients = [
        {'client_name': 'A', 'address': 'A St', 'priority': 'High'},
        {'client_name': 'B', 'address': 'B St', 'priority': 'High'},
        {'client_name': 'C', 'address': 'C St', 'priority': 'Low'},
    ]

    ordered = order_clients(clients, 'Origin St', 'fake-key')

    assert [c['client_name'] for c in ordered] == ['B', 'A', 'C']
    assert ordered[0]['travel_minutes_from_previous'] == 5
    assert ordered[1]['travel_minutes_from_previous'] == 3
    assert ordered[2]['travel_minutes_from_previous'] == 50


@patch("src.router.get_distance_matrix", side_effect=_fake_get_distance_matrix)
def test_order_clients_respects_priority_tiers_over_distance(mock_get_matrix):
    # B (High) is much farther than C (Low) from the origin, but High must still come first.
    clients = [
        {'client_name': 'B', 'address': 'B St', 'priority': 'High'},
        {'client_name': 'C', 'address': 'C St', 'priority': 'Low'},
    ]

    ordered = order_clients(clients, 'Origin St', 'fake-key')

    assert [c['client_name'] for c in ordered] == ['B', 'C']


@patch("src.router.get_distance_matrix", side_effect=_fake_get_distance_matrix)
def test_order_clients_skips_empty_tiers(mock_get_matrix):
    clients = [
        {'client_name': 'A', 'address': 'A St', 'priority': 'High'},
    ]

    ordered = order_clients(clients, 'Origin St', 'fake-key')

    assert [c['client_name'] for c in ordered] == ['A']
    mock_get_matrix.assert_called_once_with('fake-key', 'Origin St', ['A St'])
