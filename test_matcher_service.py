#!/usr/bin/env python3
"""
Test Matcher Service - Task 6
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.depts.services.matcher_service import match_entity, MatcherInput, MatcherService

def test_matcher_service():
    """Test matcher service with different scenarios"""

    print("🎯 TESTING MATCHER SERVICE")
    print("=" * 40)

    test_cases = [
        {
            "name": "City Match - Health in Karachi",
            "department_category": "health",
            "user_city": "Karachi",
            "user_location": None,
            "urgency_level": "high"
        },
        {
            "name": "City Match - Police in Lahore",
            "department_category": "police",
            "user_city": "Lahore",
            "user_location": None,
            "urgency_level": "medium"
        },
        {
            "name": "Distance Match - Fire Brigade with coordinates",
            "department_category": "fire_brigade",
            "user_city": None,
            "user_location": {"lat": 24.8607, "lng": 67.0011},  # Karachi coordinates
            "urgency_level": "critical"
        },
        {
            "name": "Fallback - Unknown category",
            "department_category": "unknown_dept",
            "user_city": "Islamabad",
            "user_location": None,
            "urgency_level": "low"
        },
        {
            "name": "No location info - Default fallback",
            "department_category": "health",
            "user_city": None,
            "user_location": None,
            "urgency_level": "medium"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 30)

        try:
            result = match_entity(
                department_category=test_case["department_category"],
                user_city=test_case["user_city"],
                user_location=test_case["user_location"],
                urgency_level=test_case["urgency_level"]
            )

            print(f"✅ Success: {result.success}")
            print(f"🎯 Strategy: {result.match_strategy}")

            if result.matched_entity:
                entity = result.matched_entity
                print(f"🏥 Entity: {entity.name}")
                print(f"📞 Phone: {entity.phone}")
                print(f"🏙️ City: {entity.city}")
                print(f"📍 Reason: {entity.match_reason}")
                if entity.distance_km:
                    print(f"📏 Distance: {entity.distance_km} km")

                print(f"🔄 Fallbacks: {len(result.fallback_entities)} alternatives available")

            else:
                print(f"❌ Error: {result.error_message}")

        except Exception as e:
            print(f"💥 Exception: {str(e)}")

def test_distance_calculation():
    """Test distance calculation function"""
    print("\n" + "=" * 40)
    print("🧮 TESTING DISTANCE CALCULATION")
    print("=" * 40)

    # Test known distances
    test_points = [
        {
            "name": "Karachi to Lahore",
            "lat1": 24.8607, "lng1": 67.0011,  # Karachi
            "lat2": 31.5204, "lng2": 74.3587,  # Lahore
            "expected_km": "~1000"
        },
        {
            "name": "Same point",
            "lat1": 24.8607, "lng1": 67.0011,
            "lat2": 24.8607, "lng2": 67.0011,
            "expected_km": "0"
        }
    ]

    for test in test_points:
        distance = MatcherService.calculate_distance(
            test["lat1"], test["lng1"], test["lat2"], test["lng2"]
        )
        print(f"{test['name']}: {distance:.2f} km (expected: {test['expected_km']} km)")

if __name__ == "__main__":
    test_matcher_service()
    test_distance_calculation()