from .client import GoogleMapsClient

class GoogleMapsService:
    def __init__(self):
        self.client = GoogleMapsClient()

    def get_coordinates_from_address(self, address):
        """Get latitude and longitude from an address"""
        result = self.client.geocode_address(address)

        if result["success"]:
            results = result["data"].get("results", [])
            if results:
                location = results[0]["geometry"]["location"]
                result["data"]["coordinates"] = {
                    "lat": location["lat"],
                    "lng": location["lng"],
                    "formatted_address": results[0]["formatted_address"]
                }

        return result

    def get_address_from_coordinates(self, lat, lng):
        """Get address from latitude and longitude"""
        result = self.client.reverse_geocode(lat, lng)

        if result["success"]:
            results = result["data"].get("results", [])
            if results:
                result["data"]["address"] = {
                    "formatted_address": results[0]["formatted_address"],
                    "components": results[0]["address_components"]
                }

        return result

    def find_nearby_places(self, lat, lng, radius_meters=1000, place_type=None, keyword=None):
        """Find places near a location"""
        location = f"{lat},{lng}"
        result = self.client.nearby_search(location, radius_meters, place_type, keyword)

        if result["success"]:
            places = result["data"].get("results", [])
            formatted_places = []

            for place in places:
                formatted_place = {
                    "place_id": place.get("place_id"),
                    "name": place.get("name"),
                    "rating": place.get("rating"),
                    "price_level": place.get("price_level"),
                    "types": place.get("types", []),
                    "vicinity": place.get("vicinity"),
                    "location": place["geometry"]["location"],
                    "open_now": place.get("opening_hours", {}).get("open_now")
                }
                formatted_places.append(formatted_place)

            result["data"]["places"] = formatted_places

        return result

    def search_places_by_text(self, query, location=None, radius=None):
        """Search for places using text query"""
        if location and radius:
            location_str = f"{location['lat']},{location['lng']}"
        else:
            location_str = None

        result = self.client.search_places(query, location_str, radius)

        if result["success"]:
            places = result["data"].get("results", [])
            formatted_places = []

            for place in places:
                formatted_place = {
                    "place_id": place.get("place_id"),
                    "name": place.get("name"),
                    "formatted_address": place.get("formatted_address"),
                    "rating": place.get("rating"),
                    "types": place.get("types", []),
                    "location": place["geometry"]["location"]
                }
                formatted_places.append(formatted_place)

            result["data"]["places"] = formatted_places

        return result

    def get_place_details(self, place_id):
        """Get detailed information about a specific place"""
        fields = [
            "place_id", "name", "formatted_address", "formatted_phone_number",
            "website", "rating", "price_level", "opening_hours", "geometry",
            "types", "reviews"
        ]

        result = self.client.get_place_details(place_id, fields)

        if result["success"]:
            place_data = result["data"].get("result", {})
            result["data"]["place"] = {
                "place_id": place_data.get("place_id"),
                "name": place_data.get("name"),
                "address": place_data.get("formatted_address"),
                "phone": place_data.get("formatted_phone_number"),
                "website": place_data.get("website"),
                "rating": place_data.get("rating"),
                "price_level": place_data.get("price_level"),
                "location": place_data.get("geometry", {}).get("location"),
                "types": place_data.get("types", []),
                "opening_hours": place_data.get("opening_hours"),
                "reviews": place_data.get("reviews", [])[:5]  # Limit to 5 reviews
            }

        return result

    def calculate_distance_and_time(self, origin_address, destination_address, mode='driving'):
        """Calculate distance and time between two addresses"""
        result = self.client.get_distance_matrix([origin_address], [destination_address], mode)

        if result["success"]:
            rows = result["data"].get("rows", [])
            if rows and rows[0]["elements"]:
                element = rows[0]["elements"][0]
                if element["status"] == "OK":
                    result["data"]["travel_info"] = {
                        "distance": element["distance"],
                        "duration": element["duration"],
                        "mode": mode
                    }

        return result

    def get_route_directions(self, origin, destination, mode='driving', waypoints=None):
        """Get detailed directions between two points"""
        result = self.client.get_directions(origin, destination, mode, waypoints)

        if result["success"]:
            routes = result["data"].get("routes", [])
            if routes:
                route = routes[0]
                legs = route["legs"]

                result["data"]["route"] = {
                    "summary": route.get("summary"),
                    "total_distance": sum(leg["distance"]["value"] for leg in legs),
                    "total_duration": sum(leg["duration"]["value"] for leg in legs),
                    "steps": [step for leg in legs for step in leg["steps"]],
                    "overview_polyline": route["overview_polyline"]["points"]
                }

        return result