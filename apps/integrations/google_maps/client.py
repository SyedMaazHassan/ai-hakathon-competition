import googlemaps
import logging
from . import constants

logger = logging.getLogger(__name__)

class GoogleMapsClient:
    def __init__(self):
        self.api_key = constants.API_KEY
        if not self.api_key:
            raise ValueError("Google Maps API key not configured")

        self.client = googlemaps.Client(key=self.api_key)

    def geocode_address(self, address):
        """Convert address to coordinates using Google Maps SDK"""
        try:
            result = self.client.geocode(address)
            return {"success": True, "data": {"results": result}}
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"[GoogleMaps] Geocoding failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"[GoogleMaps] Unexpected error in geocoding: {e}")
            return {"success": False, "error": str(e)}

    def reverse_geocode(self, lat, lng):
        """Convert coordinates to address using Google Maps SDK"""
        try:
            result = self.client.reverse_geocode((lat, lng))
            return {"success": True, "data": {"results": result}}
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"[GoogleMaps] Reverse geocoding failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"[GoogleMaps] Unexpected error in reverse geocoding: {e}")
            return {"success": False, "error": str(e)}

    def search_places(self, query, location=None, radius=None):
        """Search for places using text query"""
        try:
            params = {}
            if location and radius:
                params['location'] = location
                params['radius'] = radius

            result = self.client.places(query=query, **params)
            return {"success": True, "data": result}
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"[GoogleMaps] Places search failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"[GoogleMaps] Unexpected error in places search: {e}")
            return {"success": False, "error": str(e)}

    def nearby_search(self, location, radius, place_type=None, keyword=None):
        """Find nearby places using Google Maps SDK"""
        try:
            params = {
                'location': location,
                'radius': radius
            }
            if place_type:
                params['type'] = place_type
            if keyword:
                params['keyword'] = keyword

            result = self.client.places_nearby(**params)
            return {"success": True, "data": result}
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"[GoogleMaps] Nearby search failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"[GoogleMaps] Unexpected error in nearby search: {e}")
            return {"success": False, "error": str(e)}

    def get_place_details(self, place_id, fields=None):
        """Get detailed information about a place"""
        try:
            params = {'place_id': place_id}
            if fields:
                params['fields'] = fields if isinstance(fields, list) else [fields]

            result = self.client.place(place_id=place_id, fields=params.get('fields'))
            return {"success": True, "data": {"result": result}}
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"[GoogleMaps] Place details failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"[GoogleMaps] Unexpected error in place details: {e}")
            return {"success": False, "error": str(e)}

    def get_directions(self, origin, destination, mode='driving', waypoints=None):
        """Get directions between two points"""
        try:
            params = {
                'origin': origin,
                'destination': destination,
                'mode': mode
            }
            if waypoints:
                params['waypoints'] = waypoints

            result = self.client.directions(**params)
            return {"success": True, "data": {"routes": result}}
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"[GoogleMaps] Directions failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"[GoogleMaps] Unexpected error in directions: {e}")
            return {"success": False, "error": str(e)}

    def get_distance_matrix(self, origins, destinations, mode='driving'):
        """Get distance and time between multiple origins and destinations"""
        try:
            result = self.client.distance_matrix(
                origins=origins,
                destinations=destinations,
                mode=mode
            )
            return {"success": True, "data": result}
        except googlemaps.exceptions.ApiError as e:
            logger.error(f"[GoogleMaps] Distance matrix failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"[GoogleMaps] Unexpected error in distance matrix: {e}")
            return {"success": False, "error": str(e)}