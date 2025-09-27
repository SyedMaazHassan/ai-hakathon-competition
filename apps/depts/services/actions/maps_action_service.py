"""
Maps Action Service - Google Maps integration wrapper
Plug & play with TriggerOrchestrator NearbySearchAction & MapsDirectionsAction
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.integrations.google_maps.service import GoogleMapsService
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class MapsActionService:
    """
    Maps service using existing Google Maps integration
    """

    def __init__(self):
        self.maps_service = GoogleMapsService()

    def execute_nearby_search(self, nearby_action) -> Dict[str, Any]:
        """
        Execute nearby search action from TriggerOrchestrator

        Args:
            nearby_action: NearbySearchAction object

        Returns:
            Dict with execution result
        """
        try:
            # Convert km to meters for Google Maps API
            radius_meters = nearby_action.radius_km * 1000

            # Perform nearby search
            result = self.maps_service.find_nearby_places(
                lat=nearby_action.location_lat,
                lng=nearby_action.location_lng,
                radius_meters=radius_meters,
                keyword=nearby_action.search_query
            )

            if result["success"]:
                places = result["data"].get("places", [])

                # Limit results as requested
                limited_places = places[:nearby_action.result_limit]

                # Format results for emergency context
                formatted_results = []
                for place in limited_places:
                    formatted_place = {
                        "name": place.get("name"),
                        "address": place.get("vicinity"),
                        "rating": place.get("rating"),
                        "location": place.get("location"),
                        "distance_km": self._calculate_distance(
                            nearby_action.location_lat, nearby_action.location_lng,
                            place.get("location", {}).get("lat", 0),
                            place.get("location", {}).get("lng", 0)
                        ),
                        "types": place.get("types", []),
                        "open_now": place.get("open_now")
                    }
                    formatted_results.append(formatted_place)

                return {
                    "success": True,
                    "status": "completed",
                    "action_type": nearby_action.action_type.value,
                    "search_query": nearby_action.search_query,
                    "search_location": {
                        "lat": nearby_action.location_lat,
                        "lng": nearby_action.location_lng
                    },
                    "radius_km": nearby_action.radius_km,
                    "results_found": len(formatted_results),
                    "results": formatted_results,
                    "estimated_duration": nearby_action.estimated_duration
                }
            else:
                return {
                    "success": False,
                    "status": "failed",
                    "action_type": nearby_action.action_type.value,
                    "error": result.get("error", "Nearby search failed")
                }

        except Exception as e:
            logger.error(f"Nearby search failed: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "action_type": nearby_action.action_type.value,
                "error": str(e)
            }

    def execute_directions_action(self, directions_action) -> Dict[str, Any]:
        """
        Execute maps directions action from TriggerOrchestrator

        Args:
            directions_action: MapsDirectionsAction object

        Returns:
            Dict with execution result
        """
        try:
            # Get route directions
            result = self.maps_service.get_route_directions(
                origin=directions_action.origin_address,
                destination=directions_action.destination_address,
                mode=directions_action.travel_mode
            )

            if result["success"]:
                route_data = result["data"].get("route", {})

                # Format for emergency response
                formatted_result = {
                    "success": True,
                    "status": "completed",
                    "action_type": directions_action.action_type.value,
                    "origin": directions_action.origin_address,
                    "destination": directions_action.destination_address,
                    "travel_mode": directions_action.travel_mode,
                    "total_distance_km": round(route_data.get("total_distance", 0) / 1000, 2),
                    "total_duration_minutes": round(route_data.get("total_duration", 0) / 60, 1),
                    "route_summary": route_data.get("summary", "Route calculated"),
                    "steps_count": len(route_data.get("steps", [])),
                    "optimized": directions_action.optimize_route,
                    "estimated_duration": directions_action.estimated_duration
                }

                # Add key navigation steps for emergency response
                steps = route_data.get("steps", [])
                if steps:
                    key_steps = []
                    for i, step in enumerate(steps[:5]):  # First 5 steps
                        key_steps.append({
                            "step": i + 1,
                            "instruction": step.get("html_instructions", "").replace("<b>", "").replace("</b>", ""),
                            "distance": step.get("distance", {}).get("text", ""),
                            "duration": step.get("duration", {}).get("text", "")
                        })
                    formatted_result["key_steps"] = key_steps

                return formatted_result
            else:
                return {
                    "success": False,
                    "status": "failed",
                    "action_type": directions_action.action_type.value,
                    "error": result.get("error", "Directions calculation failed")
                }

        except Exception as e:
            logger.error(f"Directions calculation failed: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "action_type": directions_action.action_type.value,
                "error": str(e)
            }

    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance between two points using Haversine formula
        """
        from math import radians, cos, sin, asin, sqrt

        # Convert to radians
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])

        # Haversine formula
        dlng = lng2 - lng1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return round(c * r, 2)

    def find_emergency_services(self, lat: float, lng: float, service_type: str = "hospital") -> Dict[str, Any]:
        """
        Find emergency services near location
        """
        try:
            # Map service types to search queries
            service_queries = {
                "hospital": "hospital emergency",
                "police": "police station",
                "fire": "fire station",
                "pharmacy": "pharmacy",
                "clinic": "medical clinic"
            }

            search_query = service_queries.get(service_type.lower(), service_type)

            result = self.maps_service.find_nearby_places(
                lat=lat,
                lng=lng,
                radius_meters=10000,  # 10km radius
                keyword=search_query
            )

            if result["success"]:
                places = result["data"].get("places", [])
                emergency_services = []

                for place in places[:5]:  # Top 5 results
                    service = {
                        "name": place.get("name"),
                        "address": place.get("vicinity"),
                        "rating": place.get("rating"),
                        "distance_km": self._calculate_distance(
                            lat, lng,
                            place.get("location", {}).get("lat", 0),
                            place.get("location", {}).get("lng", 0)
                        ),
                        "open_now": place.get("open_now"),
                        "types": place.get("types", [])
                    }
                    emergency_services.append(service)

                return {
                    "success": True,
                    "service_type": service_type,
                    "location": {"lat": lat, "lng": lng},
                    "services_found": len(emergency_services),
                    "services": emergency_services
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error")
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Convenience functions for TriggerOrchestrator
def execute_nearby_search(nearby_action) -> Dict[str, Any]:
    """
    Execute nearby search action - main entry point
    """
    service = MapsActionService()
    return service.execute_nearby_search(nearby_action)

def execute_directions_action(directions_action) -> Dict[str, Any]:
    """
    Execute directions action - main entry point
    """
    service = MapsActionService()
    return service.execute_directions_action(directions_action)