"""
Matcher Service - Find best department entity
Simple, effective, city-based matching with distance fallback
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from pydantic import BaseModel, Field
from typing import Optional, List
from apps.depts.models import Department, DepartmentEntity, City
import math

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class MatcherInput(BaseModel):
    """Input for Matcher Service"""
    department_category: str = Field(..., description="Department category")
    user_city: Optional[str] = Field(None, description="User's city name")
    user_location: Optional[dict] = Field(None, description="User's lat/lng coordinates")
    urgency_level: Optional[str] = Field("medium", description="Urgency level")

class EntityInfo(BaseModel):
    """Matched entity information"""
    id: str
    name: str
    phone: Optional[str] = None  # Allow None for edge cases
    city: str
    address: Optional[str] = None
    distance_km: Optional[float] = None
    match_reason: str

class MatcherOutput(BaseModel):
    """Output from Matcher Service"""
    success: bool
    matched_entity: Optional[EntityInfo] = None
    fallback_entities: List[EntityInfo] = []
    match_strategy: str
    error_message: Optional[str] = None

# =============================================================================
# MATCHER SERVICE
# =============================================================================

class MatcherService:

    @staticmethod
    def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in kilometers"""
        if not all([lat1, lng1, lat2, lng2]):
            return float('inf')

        # Haversine formula
        R = 6371  # Earth's radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    @staticmethod
    def resolve_city_from_coordinates(lat: float, lng: float) -> Optional['City']:
        """
        Resolve city from coordinates using closest city in database
        In production, this would use Google Maps Geocoding API
        """
        try:
            from apps.depts.models import City

            # Find closest city by calculating distance to all cities with coordinates
            cities_with_coords = City.objects.filter(
                latitude__isnull=False,
                longitude__isnull=False
            )

            closest_city = None
            min_distance = float('inf')

            for city in cities_with_coords:
                distance = MatcherService.calculate_distance(
                    lat, lng,
                    float(city.latitude), float(city.longitude)
                )
                if distance < min_distance:
                    min_distance = distance
                    closest_city = city

            # Return city if within reasonable distance (100km)
            if closest_city and min_distance <= 100:
                return closest_city

            return None
        except Exception:
            return None

    @staticmethod
    def find_city_by_name(city_name: str) -> Optional['City']:
        """Find city by name with multiple matching strategies"""
        try:
            from apps.depts.models import City

            # Strategy 1: Exact case-insensitive match
            city = City.objects.filter(name__iexact=city_name).first()
            if city:
                return city

            # Strategy 2: Contains match (for partial names)
            city = City.objects.filter(name__icontains=city_name).first()
            if city:
                return city

            # Strategy 3: Try common variations
            variations = [
                city_name.title(),
                city_name.lower(),
                city_name.upper()
            ]

            for variation in variations:
                city = City.objects.filter(name=variation).first()
                if city:
                    return city

            return None
        except Exception:
            return None

    @staticmethod
    def find_best_entity(input_data: MatcherInput) -> MatcherOutput:
        """Find the best department entity based on input criteria"""
        try:
            # Get department
            department = Department.objects.filter(
                category=input_data.department_category,
                is_active=True
            ).first()

            if not department:
                return MatcherOutput(
                    success=False,
                    match_strategy="no_department",
                    error_message=f"No active department found for category: {input_data.department_category}"
                )

            # Get all active entities for this department
            entities = DepartmentEntity.objects.filter(
                department=department,
                is_active=True
            ).select_related('city', 'location')

            if not entities.exists():
                return MatcherOutput(
                    success=False,
                    match_strategy="no_entities",
                    error_message=f"No active entities found for department: {department.name}"
                )

            # STRATEGY 1: Strict city matching using ForeignKey (first priority)
            target_city = None

            # If user provides city name, resolve it to City object
            if input_data.user_city:
                target_city = MatcherService.find_city_by_name(input_data.user_city)

            # If user provides coordinates but no city name, resolve city from coordinates
            elif input_data.user_location and 'lat' in input_data.user_location and 'lng' in input_data.user_location:
                user_lat = float(input_data.user_location['lat'])
                user_lng = float(input_data.user_location['lng'])
                target_city = MatcherService.resolve_city_from_coordinates(user_lat, user_lng)

            # If we have a target city, find entities in that exact city
            if target_city:
                city_entities = entities.filter(city=target_city)

                if city_entities.exists():
                    best_entity = city_entities.first()
                    entity_info = EntityInfo(
                        id=best_entity.id,
                        name=best_entity.name,
                        phone=best_entity.phone or department.main_phone or "+92-300-0000000",
                        city=best_entity.city.name,
                        address=getattr(best_entity.location, 'formatted_address', '') if best_entity.location else '',
                        match_reason=f"Exact city match: {target_city.name}"
                    )

                    # Get fallback entities from SAME city first, then other cities
                    fallback_entities = []

                    # First, add other entities from same city
                    same_city_alternatives = city_entities.exclude(id=best_entity.id)[:2]
                    for entity in same_city_alternatives:
                        fallback_entities.append(EntityInfo(
                            id=entity.id,
                            name=entity.name,
                            phone=entity.phone or department.main_phone or "+92-300-0000000",
                            city=entity.city.name,
                            address=getattr(entity.location, 'formatted_address', '') if entity.location else '',
                            match_reason=f"Alternative in {entity.city.name}"
                        ))

                    # Then add entities from other cities if needed
                    if len(fallback_entities) < 3:
                        other_city_entities = entities.exclude(city=target_city)[:3-len(fallback_entities)]
                        for entity in other_city_entities:
                            fallback_entities.append(EntityInfo(
                                id=entity.id,
                                name=entity.name,
                                phone=entity.phone or department.main_phone or "+92-300-0000000",
                                city=entity.city.name,
                                address=getattr(entity.location, 'formatted_address', '') if entity.location else '',
                                match_reason=f"Fallback in {entity.city.name}"
                            ))

                    return MatcherOutput(
                        success=True,
                        matched_entity=entity_info,
                        fallback_entities=fallback_entities,
                        match_strategy="city_match"
                    )

            # STRATEGY 2: Distance-based matching (if coordinates provided)
            if input_data.user_location and 'lat' in input_data.user_location and 'lng' in input_data.user_location:
                user_lat = float(input_data.user_location['lat'])
                user_lng = float(input_data.user_location['lng'])

                entities_with_distance = []

                for entity in entities:
                    if entity.location and entity.location.lat and entity.location.lng:
                        distance = MatcherService.calculate_distance(
                            user_lat, user_lng,
                            float(entity.location.lat), float(entity.location.lng)
                        )
                        entities_with_distance.append((entity, distance))

                if entities_with_distance:
                    # Sort by distance
                    entities_with_distance.sort(key=lambda x: x[1])
                    best_entity, best_distance = entities_with_distance[0]

                    entity_info = EntityInfo(
                        id=best_entity.id,
                        name=best_entity.name,
                        phone=best_entity.phone or department.main_phone or "+92-300-0000000",
                        city=best_entity.city.name,
                        address=getattr(best_entity.location, 'formatted_address', '') if best_entity.location else '',
                        distance_km=round(best_distance, 2),
                        match_reason=f"Closest entity: {round(best_distance, 2)} km away"
                    )

                    # Get next closest as fallbacks
                    fallback_entities = []
                    for entity, distance in entities_with_distance[1:4]:
                        fallback_entities.append(EntityInfo(
                            id=entity.id,
                            name=entity.name,
                            phone=entity.phone or department.main_phone or "+92-300-0000000",
                            city=entity.city.name,
                            address=getattr(entity.location, 'formatted_address', '') if entity.location else '',
                            distance_km=round(distance, 2),
                            match_reason=f"Alternative: {round(distance, 2)} km away"
                        ))

                    return MatcherOutput(
                        success=True,
                        matched_entity=entity_info,
                        fallback_entities=fallback_entities,
                        match_strategy="distance_match"
                    )

            # STRATEGY 3: Default fallback - first available entity
            first_entity = entities.first()
            entity_info = EntityInfo(
                id=first_entity.id,
                name=first_entity.name,
                phone=first_entity.phone or department.main_phone or "+92-300-0000000",
                city=first_entity.city.name,
                address=getattr(first_entity.location, 'formatted_address', '') if first_entity.location else '',
                match_reason="Default fallback - first available entity"
            )

            # Get other entities as fallbacks
            fallback_entities = []
            for entity in entities.exclude(id=first_entity.id)[:3]:
                fallback_entities.append(EntityInfo(
                    id=entity.id,
                    name=entity.name,
                    phone=entity.phone or department.main_phone or "+92-300-0000000",
                    city=entity.city.name,
                    address=getattr(entity.location, 'formatted_address', '') if entity.location else '',
                    match_reason="Alternative option"
                ))

            return MatcherOutput(
                success=True,
                matched_entity=entity_info,
                fallback_entities=fallback_entities,
                match_strategy="default_fallback"
            )

        except Exception as e:
            return MatcherOutput(
                success=False,
                match_strategy="error",
                error_message=f"Matcher service error: {str(e)}"
            )

# =============================================================================
# SIMPLE FUNCTION INTERFACE
# =============================================================================

def match_entity(department_category: str, user_city: str = None,
                user_location: dict = None, urgency_level: str = "medium") -> MatcherOutput:
    """Simple function interface for matching entities"""

    input_data = MatcherInput(
        department_category=department_category,
        user_city=user_city,
        user_location=user_location,
        urgency_level=urgency_level
    )

    return MatcherService.find_best_entity(input_data)