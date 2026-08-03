from src.distance_calculator import get_distance_matrix

PRIORITY_TIERS = ('High', 'Medium', 'Low')


def order_clients(clients, origin_address, api_key):
    """Orders `clients` by priority tier (High -> Medium -> Low); within each tier, visits
    the geographically nearest remaining client first (nearest-neighbor), starting from
    `origin_address` and continuing from wherever the previous tier left off.

    `clients` is a list of dicts, each with at least 'address' and 'priority'. Returns a
    new list of dicts (same keys, in visiting order) with 'distance_from_previous' and
    'travel_minutes_from_previous' added.
    """
    ordered = []
    current_location = origin_address

    for tier in PRIORITY_TIERS:
        remaining = [client for client in clients if client['priority'] == tier]
        while remaining:
            legs = get_distance_matrix(
                api_key, current_location, [client['address'] for client in remaining]
            )
            nearest_index = min(range(len(legs)), key=lambda i: legs[i][2])
            destination, distance_text, travel_minutes = legs[nearest_index]

            client = remaining.pop(nearest_index)
            ordered.append({
                **client,
                'distance_from_previous': distance_text,
                'travel_minutes_from_previous': travel_minutes,
            })
            current_location = destination

    return ordered
