"""
Django Management Command to Generate Realistic Fake Data (for Major Cities Only)
Place this file in: your_app/management/commands/generate_fake_data.py
"""

import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from faker import Faker
from apps.depts.models import *
from apps.depts.choices import *

fake = Faker(['en_PK', 'en_US'])
User = get_user_model()


class Command(BaseCommand):
    help = 'Generate realistic fake data (restricted to major cities) for the emergency response system'

    def add_arguments(self, parser):
        parser.add_argument('--cities', type=int, default=6, help='Number of major cities to create')
        parser.add_argument('--departments', type=int, default=15, help='Number of departments to create')
        parser.add_argument('--entities', type=int, default=100, help='Number of department entities to create')
        parser.add_argument('--users', type=int, default=50, help='Number of users to create')
        parser.add_argument('--requests', type=int, default=200, help='Number of citizen requests to create')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before creating new')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Generating fake data restricted to major cities...')

        cities = self.create_cities(options['cities'])
        major_cities = [city for city in cities if city.is_major_city]
        self.stdout.write(f'Created {len(major_cities)} major cities')

        departments = self.create_departments(options['departments'])
        self.stdout.write(f'Created {len(departments)} departments')

        entities = self.create_entities(departments, major_cities, options['entities'])
        self.stdout.write(f'Created {len(entities)} entities in major cities')

        users = self.create_users(options['users'])
        self.stdout.write(f'Created {len(users)} users')

        requests = self.create_requests(users, major_cities, departments, entities, options['requests'])
        self.stdout.write(f'Created {len(requests)} requests')

        self.create_additional_data(requests, departments, entities)
        self.stdout.write(self.style.SUCCESS('Successfully generated fake data for major cities only!'))

    def clear_data(self):
        for model in [
            RequestFeedback, NotificationLog, Appointment, EmergencyCall, ActionLog,
            CitizenRequestAssignment, CitizenRequest, DepartmentEntity, Department,
            Location, City
        ]:
            model.objects.all().delete()

    def create_cities(self, count):
        predefined = [
            ("Karachi", "sindh", 24.8607, 67.0011),
            ("Lahore", "punjab", 31.5204, 74.3587),
            ("Islamabad", "ict", 33.6844, 73.0479),
            ("Peshawar", "kp", 34.0151, 71.5249),
            ("Quetta", "balochistan", 30.1798, 66.9750),
            ("Multan", "punjab", 30.1575, 71.5249),
        ]

        cities = []
        for name, province, lat, lng in predefined[:count]:
            city, _ = City.objects.get_or_create(
                name=name,
                province=province,
                defaults={
                    'latitude': Decimal(str(lat)),
                    'longitude': Decimal(str(lng)),
                    'is_major_city': True
                }
            )
            cities.append(city)

        return cities

    def create_departments(self, count):
        predefined = [
            ("Police", "police"),
            ("Fire Brigade", "fire_brigade"),
            ("Ambulance", "ambulance"),
            ("Electricity", "electricity"),
            ("Gas", "gas"),
            ("Water & Sewerage", "sewerage"),
            ("Health", "health"),
            ("Traffic Police", "traffic_police"),
            ("Cybercrime", "cybercrime"),
            ("Disaster Mgmt", "disaster_mgmt"),
        ]

        departments = []
        for name, category in predefined[:count]:
            dept = Department.objects.create(
                name=name,
                category=category,
                description=fake.text(max_nb_chars=150),
                main_phone=fake.phone_number(),
                main_email=fake.email(),
                emergency_number=str(random.randint(100, 9999)),
                is_24x7=True,
                response_time_minutes=random.randint(5, 30),
                is_active=True,
                logo=f"https://example.com/logos/{category}.png"
            )
            departments.append(dept)

        return departments

    def create_entities(self, departments, cities, count):
        entities = []
        for dept in departments:
            for _ in range(random.randint(2, 4)):
                if len(entities) >= count:
                    break

                city = random.choice(cities)
                location = self.create_location(city)
                name = f"{dept.name} Entity - {city.name}"

                entity = DepartmentEntity.objects.create(
                    name=name,
                    type=self.get_entity_type_for_department(dept.category),
                    department=dept,
                    city=city,
                    location=location,
                    phone=fake.phone_number(),
                    services={"hours": "9:00 - 17:00"},
                    capacity=random.randint(20, 200),
                    is_active=True
                )
                entities.append(entity)

        return entities

    def get_entity_type_for_department(self, category):
        mapping = {
            'police': 'police_station',
            'fire_brigade': 'fire_station',
            'ambulance': 'hospital',
            'health': 'hospital',
            'municipal': 'office',
            'nadra': 'office',
        }
        return mapping.get(category, 'service_center')

    def create_location(self, city):
        lat = float(city.latitude) + random.uniform(-0.05, 0.05)
        lng = float(city.longitude) + random.uniform(-0.05, 0.05)
        return Location.objects.create(
            lat=Decimal(str(lat)),
            lng=Decimal(str(lng)),
            area=fake.street_name(),
            city=city,
            raw_address=fake.address(),
            place_id=fake.uuid4(),
            formatted_address=f"{fake.street_address()}, {city.name}"
        )

    def create_users(self, count):
        users = []
        for _ in range(count):
            first = fake.first_name()
            last = fake.last_name()
            user = User.objects.create_user(
                email=f"{first.lower()}.{last.lower()}@example.com",
                first_name=first,
                last_name=last,
                password='testpass123'
            )
            users.append(user)
        return users

    def create_requests(self, users, cities, departments, entities, count):
        requests = []
        for _ in range(count):
            user = random.choice(users)
            city = random.choice(cities)
            location = self.create_location(city)
            dept = random.choice(departments)
            matching_entities = [e for e in entities if e.department == dept]
            entity = random.choice(matching_entities) if matching_entities else None

            request = CitizenRequest.objects.create(
                user=user,
                request_text=fake.sentence(),
                category=dept.category,
                urgency_level=random.choice(UrgencyLevel.choices)[0],
                confidence_score=random.uniform(0.7, 0.95),
                triage_source=random.choice(TriageSource.choices)[0],
                ai_response="Auto-routed to department",
                target_location=location,
                assigned_department=dept,
                assigned_entity=entity,
                status=random.choice(CaseStatus.choices)[0],
                is_emergency=random.choice([True, False]),
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            requests.append(request)
        return requests

    def create_additional_data(self, requests, departments, entities):
        for req in random.sample(requests, min(50, len(requests))):
            ActionLog.objects.create(
                citizen_request=req,
                agent_type=random.choice(AgentType.choices)[0],
                action_type=random.choice(ActionType.choices)[0],
                description=fake.text(),
                success=True,
                error_message='',
                details={'note': 'Simulated'},
                duration_seconds=random.randint(5, 60)
            )
