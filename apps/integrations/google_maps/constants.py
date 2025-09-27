from django.conf import settings

# Google Maps API configuration
API_KEY = settings.GOOGLE_MAPS_API_KEY
BASE_URL = "https://maps.googleapis.com/maps/api"

# API Endpoints
GEOCODING_URL = f"{BASE_URL}/geocode/json"
PLACES_URL = f"{BASE_URL}/place"
DIRECTIONS_URL = f"{BASE_URL}/directions/json"
DISTANCE_MATRIX_URL = f"{BASE_URL}/distancematrix/json"
PLACES_NEARBY_URL = f"{PLACES_URL}/nearbysearch/json"
PLACES_DETAILS_URL = f"{PLACES_URL}/details/json"
PLACES_TEXT_SEARCH_URL = f"{PLACES_URL}/textsearch/json"