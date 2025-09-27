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

    @classmethod
    def get_display_name(cls, value: str) -> str:
        """Get display name for department"""
        display_names = {
            "police": "Police",
            "fire_brigade": "Fire Brigade",
            "ambulance": "Ambulance/Medical Emergency",
            "sewerage": "Sewerage & Water",
            "electricity": "Electricity",
            "gas": "Gas Company",
            "bomb_disposal": "Bomb Disposal",
            "nadra": "NADRA",
            "health": "Health Department",
            "municipal": "Municipal Services",
            "traffic_police": "Traffic Police",
            "cybercrime": "Cybercrime",
            "disaster_mgmt": "Disaster Management"
        }
        return display_names.get(value, value.title())