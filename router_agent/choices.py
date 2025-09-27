from enum import Enum

class DepartmentCategory(str, Enum):
    """Department categories for Pakistani government services"""
    POLICE = "police"
    FIRE_BRIGADE = "fire_brigade"
    AMBULANCE = "ambulance"
    SEWERAGE = "sewerage"
    ELECTRICITY = "electricity"
    GAS = "gas"
    BOMB_DISPOSAL = "bomb_disposal"
    NADRA = "nadra"
    HEALTH = "health"
    MUNICIPAL = "municipal"
    TRAFFIC_POLICE = "traffic_police"
    CYBERCRIME = "cybercrime"
    DISASTER_MGMT = "disaster_mgmt"