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

        self.stdout.write('Generating demo data for hackathon...')

        # Create 5-6 major Pakistani cities
        cities = self.create_major_cities()
        self.stdout.write(f'Created {len(cities)} major cities')

        # Create all departments with realistic data
        departments = self.create_all_departments()
        self.stdout.write(f'Created {len(departments)} departments')

        # Create 5-6 realistic entities per department per city
        entities = self.create_realistic_entities(departments, cities)
        self.stdout.write(f'Created {len(entities)} realistic entities')

        self.stdout.write(
            self.style.SUCCESS('Successfully generated demo data for hackathon!')
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

    def create_major_cities(self):
        """Create 5-6 major Pakistani cities for demo"""
        major_cities_data = [
            ("Karachi", "sindh", 24.8607, 67.0011),
            ("Lahore", "punjab", 31.5204, 74.3587),
            ("Islamabad", "ict", 33.6844, 73.0479),
            ("Peshawar", "kp", 34.0151, 71.5249),
            ("Faisalabad", "punjab", 31.4504, 73.1350),
            ("Quetta", "balochistan", 30.1798, 66.9750),
        ]

        cities = []
        for name, province, lat, lng in major_cities_data:
            city, created = City.objects.get_or_create(
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

    def create_all_departments(self):
        """Create all emergency departments with realistic data"""
        from apps.depts.choices import DepartmentCategory

        department_categories = [
            DepartmentCategory.POLICE, DepartmentCategory.FIRE_BRIGADE,
            DepartmentCategory.AMBULANCE, DepartmentCategory.HEALTH,
            DepartmentCategory.CYBERCRIME, DepartmentCategory.DISASTER_MGMT
        ]

        departments = []
        for category in department_categories:
            dept, created = Department.objects.get_or_create(
                category=category,
                defaults={
                    'name': self.get_department_name(category),
                    'description': self.get_department_description(category),
                    'main_phone': f"+92-{random.randint(20,99)}-{random.randint(10000000,99999999)}",
                    'emergency_number': self.get_emergency_number(category),
                    'is_active': True
                }
            )
            departments.append(dept)

        return departments

    def get_department_name(self, category):
        """Get realistic department name"""
        names = {
            "police": "Pakistan Police",
            "fire_brigade": "Fire & Rescue Services",
            "ambulance": "Emergency Medical Services",
            "health": "Department of Health",
            "sewerage": "Water & Sanitation Agency",
            "electricity": "Electric Supply Company",
            "gas": "Sui Gas Corporation",
            "bomb_disposal": "Bomb Disposal Squad",
            "nadra": "NADRA Services",
            "municipal": "Municipal Corporation",
            "traffic_police": "Traffic Police",
            "cybercrime": "Cybercrime Wing",
            "disaster_mgmt": "Provincial Disaster Management Authority"
        }
        return names.get(category, f"{category.title()} Department")

    def get_department_description(self, category):
        """Get realistic department description"""
        descriptions = {
            "police": "Law enforcement and public safety services",
            "fire_brigade": "Fire fighting and rescue operations",
            "ambulance": "Emergency medical response and patient transport",
            "health": "Healthcare services and medical facilities",
            "sewerage": "Water supply and sewerage management",
            "electricity": "Electrical power distribution and maintenance",
            "gas": "Natural gas supply and pipeline maintenance",
            "bomb_disposal": "Explosive ordnance disposal and security",
            "nadra": "National identity and registration services",
            "municipal": "City administration and public services",
            "traffic_police": "Traffic management and road safety",
            "cybercrime": "Digital crime investigation and prevention",
            "disaster_mgmt": "Disaster preparedness and response coordination"
        }
        return descriptions.get(category, f"Services related to {category}")

    def get_emergency_number(self, category):
        """Get emergency numbers for departments"""
        emergency_numbers = {
            "police": "15",
            "fire_brigade": "16",
            "ambulance": "1122",
            "health": "1122",
            "traffic_police": "15"
        }
        return emergency_numbers.get(category, "")

    def create_realistic_entities(self, departments, cities):
        """Create 5-6 realistic entities per department per city"""
        entities = []

        # Realistic entity names by department category
        entity_templates = {
            "police": [
                "City Police Station", "Saddar Police Station", "Clifton Police Station",
                "Gulshan Police Station", "Defence Police Station", "Cantt Police Station"
            ],
            "fire_brigade": [
                "Central Fire Station", "Saddar Fire Station", "Industrial Fire Station",
                "Airport Fire Station", "Port Fire Station", "City Fire Station"
            ],
            "ambulance": [
                "Emergency Medical Center", "Rescue Service Station", "Ambulance Hub",
                "Medical Emergency Unit", "First Aid Center", "Paramedic Station"
            ],
            "health": [
                "Civil Hospital", "Jinnah Hospital", "Government Hospital",
                "District Hospital", "Teaching Hospital", "General Hospital"
            ],
            "sewerage": [
                "Water Treatment Plant", "Pumping Station", "Filtration Plant",
                "Water Supply Office", "Sewerage Office", "WASA Office"
            ],
            "electricity": [
                "Grid Station", "Distribution Office", "Power House",
                "Electrical Division", "Load Dispatch Center", "Service Center"
            ],
            "gas": [
                "Gas Distribution Office", "Metering Station", "Gas Supply Office",
                "Pipeline Station", "Customer Service Center", "Gas Hub"
            ],
            "bomb_disposal": [
                "EOD Unit", "Bomb Squad HQ", "Explosive Unit",
                "Security Squad", "Anti-Terror Unit", "Special Unit"
            ],
            "nadra": [
                "NADRA Center", "Registration Office", "ID Card Center",
                "Citizen Service Center", "Document Center", "NADRA Hub"
            ],
            "municipal": [
                "Municipal Office", "City Council Office", "Town Hall",
                "Administrative Office", "Public Services Office", "Civic Center"
            ],
            "traffic_police": [
                "Traffic Police Station", "Traffic Control Room", "Road Safety Office",
                "Highway Patrol Office", "Traffic Management Center", "Checkpoint Office"
            ],
            "cybercrime": [
                "Cybercrime Unit", "Digital Forensics Lab", "Cyber Investigation Cell",
                "Tech Crime Unit", "Online Crime Division", "Cyber Security Center"
            ],
            "disaster_mgmt": [
                "Emergency Operations Center", "Disaster Response Unit", "Crisis Management Center",
                "Relief Office", "Emergency Coordination Center", "Disaster Control Room"
            ]
        }

        for department in departments:
            templates = entity_templates.get(department.category, ["Service Center", "Office", "Station"])

            for city in cities:
                # Create 5-6 entities per department per city
                for i, template in enumerate(templates):
                    entity_name = f"{template} - {city.name}"

                    # Create location for this entity
                    location = self.create_entity_location(city)

                    entity = DepartmentEntity.objects.create(
                        name=entity_name,
                        type=self.get_entity_type(department.category),
                        department=department,
                        city=city,
                        location=location,
                        phone=f"+92-{random.randint(20,99)}-{random.randint(10000000,99999999)}",
                        services=self.get_entity_services(department.category),
                        capacity=self.get_entity_capacity(department.category),
                        is_active=True
                    )
                    entities.append(entity)

        return entities

    def create_entity_location(self, city):
        """Create a location for an entity within the city"""
        # Add some random offset to city coordinates
        lat_offset = random.uniform(-0.05, 0.05)  # About 5km variance
        lng_offset = random.uniform(-0.05, 0.05)

        location = Location.objects.create(
            lat=city.latitude + Decimal(str(lat_offset)),
            lng=city.longitude + Decimal(str(lng_offset)),
            area=f"{random.choice(['Sector', 'Block', 'Area'])} {random.choice(['A', 'B', 'C', 'G', 'F'])}-{random.randint(1,15)}",
            city=city,
            raw_address=f"{fake.street_address()}, {city.name}",
            formatted_address=f"{fake.street_address()}, {city.name}, {city.get_province_display()}, Pakistan"
        )
        return location

    def get_entity_type(self, category):
        """Get appropriate entity type for department category"""
        type_mapping = {
            "police": "police_station",
            "fire_brigade": "fire_station",
            "ambulance": "emergency_center",
            "health": "hospital",
            "sewerage": "office",
            "electricity": "office",
            "gas": "office",
            "bomb_disposal": "headquarters",
            "nadra": "service_center",
            "municipal": "office",
            "traffic_police": "police_station",
            "cybercrime": "headquarters",
            "disaster_mgmt": "headquarters"
        }
        return type_mapping.get(category, "office")

    def get_entity_services(self, category):
        """Get services offered by entity type"""
        services = {
            "police": {"services": ["FIR Registration", "Traffic Violations", "Crime Investigation"], "24x7": True},
            "fire_brigade": {"services": ["Fire Fighting", "Rescue Operations", "Emergency Response"], "24x7": True},
            "ambulance": {"services": ["Emergency Transport", "First Aid", "Medical Response"], "24x7": True},
            "health": {"services": ["Emergency Care", "OPD", "Surgery", "ICU"], "24x7": True},
            "sewerage": {"services": ["Water Supply", "Sewerage Maintenance", "Complaints"], "24x7": False},
            "electricity": {"services": ["Power Outages", "New Connections", "Bill Complaints"], "24x7": True},
            "gas": {"services": ["Gas Leaks", "New Connections", "Meter Issues"], "24x7": True},
            "bomb_disposal": {"services": ["Explosive Disposal", "Threat Assessment", "Security"], "24x7": True},
            "nadra": {"services": ["ID Cards", "Certificates", "Registration"], "24x7": False},
            "municipal": {"services": ["City Services", "Licenses", "Public Works"], "24x7": False},
            "traffic_police": {"services": ["Traffic Control", "License Issues", "Accidents"], "24x7": True},
            "cybercrime": {"services": ["Online Crime", "Digital Investigation", "Cyber Security"], "24x7": False},
            "disaster_mgmt": {"services": ["Emergency Coordination", "Disaster Response", "Relief"], "24x7": True}
        }
        return services.get(category, {"services": ["General Services"], "24x7": False})

    def get_entity_capacity(self, category):
        """Get typical capacity for entity type"""
        capacities = {
            "police": random.randint(20, 100),      # Officers
            "fire_brigade": random.randint(15, 50), # Firefighters
            "ambulance": random.randint(5, 20),     # Ambulances
            "health": random.randint(50, 500),      # Beds
            "sewerage": random.randint(10, 30),     # Staff
            "electricity": random.randint(15, 40),  # Engineers
            "gas": random.randint(10, 25),          # Technicians
            "bomb_disposal": random.randint(5, 15), # Specialists
            "nadra": random.randint(20, 60),        # Counters
            "municipal": random.randint(25, 75),    # Staff
            "traffic_police": random.randint(15, 50), # Officers
            "cybercrime": random.randint(5, 20),    # Investigators
            "disaster_mgmt": random.randint(10, 30) # Coordinators
        }
        return capacities.get(category, random.randint(10, 50))

    def create_departments_old(self, count):
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