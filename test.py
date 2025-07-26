import requests
import h3

def latlng_to_location(lat, lng):
    """
    Converts a latitude and longitude to a location name using Nominatim.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lng,
        'format': 'json',
        'addressdetails': 1
    }
    headers = {'User-Agent': 'GridAgent/1.0'}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        address = data.get('address', {})
        return address.get('town') or address.get('city') or address.get('village') or "Unknown"
    except Exception:
        return "Unknown"
    
print(latlng_to_location(*h3.cell_to_latlng("871fb6175ffffff")))