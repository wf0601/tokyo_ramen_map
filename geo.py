import requests

def get_coordinates(place_name):
    # Nominatim API endpoint
    url = "https://nominatim.openstreetmap.org/search"

    # Parameters for the API request
    params = {
        'q': place_name,      # Place name to search
        'format': 'json',     # Return data in JSON format
        'limit': 1            # Return only the first result
    }
    headers = {
        'User-Agent': 'MyApp/1.0 (your_email@example.com)'
    }

    # Send GET request
    response = requests.get(url, params=params,headers=headers)

    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        if data:
            # Extract latitude and longitude
            lat = data[0]['lat']
            lon = data[0]['lon']
            return lat, lon
        else:
            return "Location not found."
    else:
        return f"Error: {response.status_code}"

# Example usage
location = "渋谷駅"
coordinates = get_coordinates(location)
print(f"Coordinates for {location}: {coordinates}")