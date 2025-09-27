"""
Django Management Command to Generate Realistic Fake Data
Place this file in: your_app/management/commands/generate_fake_data.py
"""

import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from faker import Faker
from apps.depts.models import *  # Replace with your actual app name
from apps.depts.choices import *

# Initialize Faker with Pakistani locale
fake = Faker(['en_PK', 'en_US'])

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate realistic fake data for the emergency response system'

    def add_arguments(self, parser):
        parser.add_argument('--cities', type=int, default=20, help='Number of cities to create')
        parser.add_argument('--departments', type=int, default=15, help='Number of departments to create')
        parser.add_argument('--entities', type=int, default=100, help='Number of department entities to create')
        parser.add_argument('--users', type=int, default=50, help='Number of users to create')
        parser.add_argument('--requests', type=int, default=200, help='Number of citizen requests to create')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before creating new')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Generating fake data...')

        cities = self.create_cities(options['cities'])
        self.stdout.write(f'Created {len(cities)} cities')

        departments = self.create_departments(options['departments'])
        self.stdout.write(f'Created {len(departments)} departments')

        entities = self.create_entities(departments, cities, options['entities'])
        self.stdout.write(f'Created {len(entities)} entities')

        users = self.create_users(options['users'])
        self.stdout.write(f'Created {len(users)} users')

        requests = self.create_requests(users, cities, departments, entities, options['requests'])
        self.stdout.write(f'Created {len(requests)} requests')

        self.create_additional_data(requests, departments, entities)

        self.stdout.write(
            self.style.SUCCESS('Successfully generated realistic fake data!')
        )

    def clear_data(self):
        """Clear existing data"""
        models_to_clear = [
            RequestFeedback, NotificationLog, Appointment, EmergencyCall,
            ActionLog, CitizenRequestAssignment, CitizenRequest,
            DepartmentEntity, Department, Location, City
        ]

        for model in models_to_clear:
            model.objects.all().delete()

    def create_cities(self, count):
        """Create realistic Pakistani cities"""
        pakistani_cities = [
            # Punjab
            ("Karachi", "sindh", 24.8607, 67.0011, True),
            ("Lahore", "punjab", 31.5204, 74.3587, True),
            ("Faisalabad", "punjab", 31.4504, 73.1350, True),
            ("Rawalpindi", "punjab", 33.5651, 73.0169, True),
            ("Gujranwala", "punjab", 32.1614, 74.1883, False),
            ("Peshawar", "kp", 34.0151, 71.5249, True),
            ("Multan", "punjab", 30.1575, 71.5249, True),
            ("Hyderabad", "sindh", 25.3960, 68.3578, False),
            ("Islamabad", "ict", 33.6844, 73.0479, True),
            ("Quetta", "balochistan", 30.1798, 66.9750, True),
            ("Bahawalpur", "punjab", 29.4000, 71.6833, False),
            ("Sargodha", "punjab", 32.0836, 72.6711, False),
            ("Sialkot", "punjab", 32.4945, 74.5229, False),
            ("Sukkur", "sindh", 27.7058, 68.8574, False),
            ("Larkana", "sindh", 27.5590, 68.2123, False),
            ("Sheikhupura", "punjab", 31.7167, 73.9783, False),
            ("Jhang", "punjab", 31.2681, 72.3317, False),
            ("Rahimyar Khan", "punjab", 28.4212, 70.2989, False),
            ("Gujrat", "punjab", 32.5739, 74.0755, False),
            ("Kasur", "punjab", 31.1156, 74.4502, False),
            # Add more cities with random locations for testing
        ]

        cities = []
        for i, (name, province, lat, lng, is_major) in enumerate(pakistani_cities[:count]):
            city, created = City.objects.get_or_create(
                name=name,
                province=province,
                defaults={
                    'latitude': Decimal(str(lat)),
                    'longitude': Decimal(str(lng)),
                    'is_major_city': is_major
                }
            )
            cities.append(city)

        # Fill remaining with random cities if needed
        while len(cities) < count:
            province = random.choice(Province.choices)[0]
            city_name = f"{fake.city()} {random.choice(['Town', 'City', 'District'])}"

            city, created = City.objects.get_or_create(
                name=city_name,
                province=province,
                defaults={
                    'latitude': Decimal(str(fake.latitude())),
                    'longitude': Decimal(str(fake.longitude())),
                    'is_major_city': fake.boolean(chance_of_getting_true=20)
                }
            )
            cities.append(city)

        return cities

    def create_departments(self, count):
        """Create realistic emergency departments"""
        department_data = [
            ("Karachi Police", "police", "Primary law enforcement for Karachi", "+92-21-99212051",
             "emergency@karachipolice.gov.pk", "15"),
            ("Sindh Fire Brigade", "fire_brigade", "Fire and rescue services", "+92-21-99214444", "fire@sindh.gov.pk",
             "16"),
            ("Edhi Ambulance Service", "ambulance", "Emergency medical services", "+92-21-99201234",
             "ambulance@edhi.org", "115"),
            ("K-Electric Emergency", "electricity", "Power supply emergency repairs", "+92-21-99213456",
             "emergency@ke.com.pk", "118"),
            ("Sui Gas Emergency", "gas", "Gas leakage and emergency repairs", "+92-21-99215678",
             "emergency@ssgc.com.pk", "1199"),
            ("Karachi Water Board", "sewerage", "Water and sewerage issues", "+92-21-99216789",
             "complaints@kwsb.gos.pk", "1334"),
            ("Bomb Disposal Unit", "bomb_disposal", "Explosive ordnance disposal", "+92-21-99217890",
             "bdu@police.sindh.gov.pk", "15"),
            ("NADRA Karachi", "nadra", "National identity services", "+92-21-111-786-100", "helpdesk@nadra.gov.pk", ""),
            ("Sindh Health Department", "health", "Public health services", "+92-21-99218901", "health@sindh.gov.pk",
             ""),
            ("Karachi Metropolitan Corporation", "municipal", "Municipal services", "+92-21-99219012",
             "mayor@kmc.gos.pk", "1339"),
            ("Traffic Police Karachi", "traffic_police", "Traffic management", "+92-21-99220123",
             "traffic@karachipolice.gov.pk", "1915"),
            ("FIA Cybercrime", "cybercrime", "Cybercrime investigation", "+92-21-99221234", "cyber@fia.gov.pk", "1991"),
            ("PDMA Sindh", "disaster_mgmt", "Disaster management", "+92-21-99222345", "pdma@sindh.gov.pk", "1129"),
        ]

        departments = []
        for i, (name, category, desc, phone, email, emergency) in enumerate(department_data[:count]):
            dept = Department.objects.create(
                name=name,
                category=category,
                description=desc,
                main_phone=phone,
                main_email=email,
                emergency_number=emergency if emergency else "",  # Ensure empty string instead of None
                is_24x7=category in ['police', 'fire_brigade', 'ambulance', 'electricity'],
                response_time_minutes=random.randint(5, 45) if emergency else None,
                is_active=True,
                logo=f"https://example.com/logos/{category}.png"
            )
            departments.append(dept)

        # Fill remaining with random departments
        while len(departments) < count:
            category = random.choice(DepartmentCategory.choices)[0]
            emergency_num = str(fake.random_int(min=1000, max=9999)) if fake.boolean() else ""
            dept = Department.objects.create(
                name=f"{fake.company()} {category.title()} Department",
                category=category,
                description=fake.text(max_nb_chars=200),
                main_phone=f"+92-21-{fake.random_int(min=10000000, max=99999999)}",
                main_email=fake.email(),
                emergency_number=emergency_num,  # Ensure empty string instead of None
                is_24x7=fake.boolean(chance_of_getting_true=40),
                response_time_minutes=random.randint(5, 60),
                is_active=fake.boolean(chance_of_getting_true=90)
            )
            departments.append(dept)

        return departments

    def create_entities(self, departments, cities, count):
        """Create department entities (hospitals, police stations, etc.)"""
        entities = []

        # Realistic entity names by type
        entity_names = {
            'hospital': ['Civil Hospital', 'Jinnah Hospital', 'Aga Khan Hospital', 'Liaquat National Hospital',
                         'Dow Hospital'],
            'police_station': ['City Station', 'Saddar Station', 'Clifton Station', 'Gulshan Station',
                               'North Nazimabad Station'],
            'fire_station': ['Central Fire Station', 'Saddar Fire Station', 'Gulshan Fire Station',
                             'Korangi Fire Station'],
            'office': ['Head Office', 'Regional Office', 'District Office', 'Zonal Office'],
            'service_center': ['Customer Service Center', 'Complaint Center', 'Help Desk'],
            'clinic': ['Primary Health Center', 'Basic Health Unit', 'Community Clinic'],
            'headquarters': ['Regional Headquarters', 'Provincial Headquarters', 'District HQ']
        }

        for dept in departments:
            # Create 3-8 entities per department
            num_entities = random.randint(3, min(8, count // len(departments) + 2))

            for _ in range(num_entities):
                if len(entities) >= count:
                    break

                entity_type = self.get_entity_type_for_department(dept.category)
                base_names = entity_names.get(entity_type, ['Service Center'])

                city = random.choice(cities)
                location = self.create_location(city)

                entity = DepartmentEntity.objects.create(
                    name=f"{random.choice(base_names)} - {city.name}",
                    type=entity_type,
                    department=dept,
                    city=city,
                    location=location,
                    phone=f"+92-{random.randint(20, 99)}-{fake.random_int(min=10000000, max=99999999)}",
                    services=self.generate_services_data(entity_type),
                    capacity=random.randint(10, 500) if entity_type in ['hospital', 'clinic'] else None,
                    is_active=fake.boolean(chance_of_getting_true=95)
                )
                entities.append(entity)

        return entities

    def get_entity_type_for_department(self, dept_category):
        """Map department category to appropriate entity type"""
        mapping = {
            'police': 'police_station',
            'fire_brigade': 'fire_station',
            'ambulance': 'hospital',
            'health': 'hospital',
            'nadra': 'office',
            'municipal': 'office',
            'cybercrime': 'office',
        }
        return mapping.get(dept_category, 'service_center')

    def create_location(self, city):
        """Create a location within a city"""
        # Add some random offset to city coordinates
        base_lat = float(city.latitude) if city.latitude else 24.8607
        base_lng = float(city.longitude) if city.longitude else 67.0011

        location = Location.objects.create(
            lat=Decimal(str(base_lat + random.uniform(-0.1, 0.1))),
            lng=Decimal(str(base_lng + random.uniform(-0.1, 0.1))),
            area=fake.street_name(),
            city=city,
            raw_address=fake.address(),
            place_id=fake.uuid4(),
            formatted_address=f"{fake.street_address()}, {city.name}, Pakistan"
        )
        return location

    def generate_services_data(self, entity_type):
        """Generate realistic services data"""
        services = {
            'operating_hours': f"{random.randint(6, 9)}:00 - {random.randint(17, 22)}:00",
            '24x7': random.choice([True, False]),
        }

        if entity_type == 'hospital':
            services.update({
                'emergency_room': True,
                'departments': random.sample(
                    ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'General Medicine'], 3),
                'beds_available': random.randint(50, 300)
            })
        elif entity_type == 'police_station':
            services.update({
                'crime_reporting': True,
                'traffic_violations': random.choice([True, False]),
                'passport_services': random.choice([True, False])
            })

        return services

    def create_users(self, count):
        """Create realistic users"""
        users = []

        # Common Pakistani names
        first_names = ['Muhammad', 'Ali', 'Hassan', 'Ahmed', 'Fatima', 'Ayesha', 'Sara', 'Omar', 'Zain', 'Noor']
        last_names = ['Khan', 'Ali', 'Sheikh', 'Malik', 'Ahmed', 'Hassan', 'Hussain', 'Shah', 'Qureshi', 'Siddiqui']

        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"

            user = User.objects.create_user(
                email=f"{username}@{random.choice(['gmail.com', 'yahoo.com', 'hotmail.com'])}",
                first_name=first_name,
                last_name=last_name,
                password='testpass123'
            )
            users.append(user)

        return users

    def create_requests(self, users, cities, departments, entities, count):
        """Create realistic citizen requests"""
        requests = []

        # Realistic request templates by category
        request_templates = {
            'police': [
                "There's been a theft in our area. Someone broke into my neighbor's house last night.",
                "I want to report a mobile phone snatching incident that happened near {location}.",
                "There's suspicious activity in our street. Strange people gathering at odd hours.",
                "My car was stolen from outside my house. License plate number is ABC-123.",
                "There's a domestic violence situation in the apartment next to mine."
            ],
            'fire_brigade': [
                "There's a fire in a building near {location}. Please send help immediately!",
                "I can smell gas leak and there might be fire hazard in our area.",
                "A tree has fallen and is blocking the road after the storm.",
                "There's smoke coming from the electrical panel in our building."
            ],
            'ambulance': [
                "My father is having chest pain. We need an ambulance urgently at {location}.",
                "There's been a road accident near {location}. Multiple people are injured.",
                "My mother has fallen and can't move. Please send medical help.",
                "Emergency! Someone has collapsed in our office building."
            ],
            'electricity': [
                "Our area has been without power for 12 hours. When will it be restored?",
                "There are sparks coming from the electricity pole near our house.",
                "Power cables have fallen on the road after the rain.",
                "Our transformer is making loud noises and might explode."
            ],
            'gas': [
                "There's a strong smell of gas in our building. It might be a leak.",
                "The gas pressure is very low in our area for the past week.",
                "Gas pipeline seems to be damaged after the construction work."
            ],
            'sewerage': [
                "The sewerage system is overflowing in our street. It's been 3 days.",
                "There's no water supply in our area for 2 days.",
                "The manhole cover is broken and it's dangerous for pedestrians.",
                "Water quality is very poor. We suspect contamination."
            ]
        }

        for i in range(count):
            user = random.choice(users)
            city = random.choice(cities)
            location = self.create_location(city)

            # Choose category and template
            category = random.choice(list(request_templates.keys()))
            template = random.choice(request_templates[category])
            request_text = template.format(location=f"{location.area}, {city.name}")

            # Find matching department
            matching_departments = [d for d in departments if d.category == category]
            assigned_dept = random.choice(matching_departments) if matching_departments else random.choice(departments)

            # Find matching entity
            matching_entities = [e for e in entities if e.department == assigned_dept]
            assigned_entity = random.choice(matching_entities) if matching_entities else None

            urgency = random.choice(UrgencyLevel.choices)[0]
            status = random.choice(CaseStatus.choices)[0]

            # Create request
            created_time = fake.date_time_between(start_date='-30d', end_date='now',
                                                  tzinfo=timezone.get_current_timezone())

            request = CitizenRequest.objects.create(
                user=user,
                request_text=request_text,
                category=category,
                urgency_level=urgency,
                confidence_score=random.uniform(0.7, 0.98),
                triage_source=random.choice(TriageSource.choices)[0],
                ai_response=f"Analyzed request: {category} emergency with {urgency} priority. Routing to appropriate department.",
                target_location=location,
                assigned_department=assigned_dept,
                assigned_entity=assigned_entity,
                status=status,
                is_emergency=(urgency == 'critical'),
                created_at=created_time,
                updated_at=created_time + timedelta(minutes=random.randint(1, 120))
            )

            # Set resolution time for resolved cases
            if status in ['resolved', 'closed']:
                request.resolved_at = request.updated_at + timedelta(hours=random.randint(1, 48))
                request.save()

            requests.append(request)

        return requests

    def create_additional_data(self, requests, departments, entities):
        """Create additional related data"""
        # Create action logs
        for request in random.sample(requests, min(100, len(requests))):
            for _ in range(random.randint(1, 5)):
                ActionLog.objects.create(
                    citizen_request=request,
                    agent_type=random.choice(AgentType.choices)[0],
                    action_type=random.choice(ActionType.choices)[0],
                    description=fake.sentence(),
                    success=fake.boolean(chance_of_getting_true=85),
                    error_message=fake.sentence() if fake.boolean(chance_of_getting_true=15) else '',
                    details={'processed_at': timezone.now().isoformat()},
                    duration_seconds=random.randint(1, 30)
                )

        # Create some emergency calls
        for request in random.sample([r for r in requests if r.is_emergency],
                                     min(20, len([r for r in requests if r.is_emergency]))):
            phone_number = request.assigned_department.emergency_number if request.assigned_department.emergency_number else request.assigned_department.main_phone
            EmergencyCall.objects.create(
                citizen_request=request,
                department=request.assigned_department,
                call_id=fake.uuid4(),
                phone_number=phone_number,
                status=random.choice(CallStatus.choices)[0],
                script_used="Emergency call script for urgent assistance",
                message_sent=f"Emergency reported: {request.request_text[:100]}",
                duration_seconds=random.randint(30, 300)
            )

        # Create some appointments
        for request in random.sample([r for r in requests if r.status not in ['submitted', 'analyzing']],
                                     min(30, len(requests))):
            if random.random() < 0.3:  # 30% chance of having an appointment
                Appointment.objects.create(
                    citizen_request=request,
                    department=request.assigned_department,
                    entity=request.assigned_entity,
                    calendar_event_id=fake.uuid4(),
                    calendar_link=f"https://calendar.google.com/event/{fake.uuid4()}",
                    scheduled_at=timezone.now() + timedelta(days=random.randint(1, 7)),
                    duration_minutes=random.choice([30, 45, 60]),
                    location_details=f"{request.assigned_entity.name if request.assigned_entity else 'Office'} - {request.target_location.formatted_address}",
                    status=random.choice(AppointmentStatus.choices)[0],
                    notes=fake.sentence()
                )

        # Create feedback for some resolved requests
        for request in [r for r in requests if r.status in ['resolved', 'closed']]:
            if random.random() < 0.4:  # 40% chance of feedback
                RequestFeedback.objects.create(
                    citizen_request=request,
                    overall_rating=random.randint(3, 5),
                    response_time_rating=random.randint(2, 5),
                    accuracy_rating=random.randint(3, 5),
                    communication_rating=random.randint(3, 5),
                    comment=fake.sentence(),
                    would_recommend=fake.boolean(chance_of_getting_true=75)
                )

        # Create notification logs
        for request in random.sample(requests, min(150, len(requests))):
            NotificationLog.objects.create(
                citizen_request=request,
                notification_type=random.choice(['email', 'sms']),
                recipient=request.user.email if random.random() < 0.7 else f"+92-{fake.random_int(min=3000000000, max=3999999999)}",
                subject=f"Update on your request {request.case_code}",
                message=f"Your request has been updated. Current status: {request.get_status_display()}",
                sent_successfully=fake.boolean(chance_of_getting_true=95),
                external_id=fake.uuid4()
            )

    def style_text(self, text, style='SUCCESS'):
        """Helper to style console output"""
        colors = {
            'SUCCESS': '\033[92m',
            'WARNING': '\033[93m',
            'ERROR': '\033[91m',
            'INFO': '\033[94m',
            'ENDC': '\033[0m'
        }
        return f"{colors.get(style, '')}{text}{colors['ENDC']}"