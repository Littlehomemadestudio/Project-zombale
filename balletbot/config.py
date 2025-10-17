"""
Configuration settings for BalletBot: Outbreak Dominion
"""

# Bot Configuration
BOT_TOKEN = "YOUR_BALE_BOT_TOKEN_HERE"  # Replace with actual token
USE_REAL_BALE_API = True  # Set to False for mock mode during development

# Time Configuration
TIME_MULTIPLIER = 1  # For dev/testing: 0.1 = 10x faster, 10 = 10x slower
DAY_LENGTH_SECONDS = 1800 * TIME_MULTIPLIER  # 30 minutes per day (scaled)
WORLD_TICK_SECONDS = 30  # Zombie/noise processing loop
DECISION_WINDOW = 7  # Seconds for building-floor sneak/attack (5-10 range)

# Map Costs
MAP_FIRST_COST = {"wood": 10, "stone": 10}
MAP_DETAILED_COST = {"wood": 50, "stone": 25, "metal": 10}

# Spotter Costs
SPOTTER_COST = {"circuit": 3, "metal": 5}

# Offline Mode Settings
OFFLINE_SCAVENGE_COOLDOWN = 3600  # 1 hour in seconds

# Vehicle Settings
VEHICLE_CONDITION_THRESHOLD = 40  # Minimum condition to drive
VEHICLE_REPAIR_RATE = 20  # Condition restored per repair kit
TANK_BUILD_DEFAULT_DAYS = 7  # Real-time duration (scaled by multiplier)

# Action Cooldowns (in seconds)
ACTION_COOLDOWNS = {
    "move": 30,
    "loot": 60,
    "attack": 10,
    "craft": 120,
    "build": 300,
    "mine": 180,
    "chop": 180,
    "seek": 60,
    "radio": 5,
    "intel": 300,
    "map": 10
}

# Combat Settings
COMBAT_CRITICAL_HIT_CHANCE = 5  # Percentage
COMBAT_ALERTED_BONUS = 15  # Damage bonus when alerted
COMBAT_AMBUSH_BONUS = 100  # Double damage for ambush

# Zombie Settings
ZOMBIE_BASE_SPAWN_CHANCE = 0.1  # Base spawn probability
ZOMBIE_NOISE_THRESHOLD = 50  # Noise level for zombie attraction
ZOMBIE_NIGHT_BONUS = 0.15  # Night spawn bonus

# Player Settings
DEFAULT_HP = 100
DEFAULT_STAMINA = 100
DEFAULT_HUNGER = 0
DEFAULT_INFECTION = 0
DEFAULT_INTELLIGENCE = 0
DEFAULT_LOCATION = "Forest:Camp:Area1"

# Character Class Bonuses
CLASS_BONUSES = {
    "Scavenger": {
        "loot_yield": 0.10,  # +10% loot yield
        "stealth": 10,       # +10 stealth
        "description": "Expert at finding resources and staying hidden"
    },
    "Mechanic": {
        "crafting_speed": 0.15,  # +15% crafting speed
        "intelligence_gain": 10,  # +10 intelligence gain
        "description": "Skilled at building and repairing equipment"
    },
    "Soldier": {
        "weapon_damage": 0.10,  # +10% weapon damage
        "health": 10,           # +10 health
        "description": "Trained in combat and survival tactics"
    }
}

# Item Types
ITEM_TYPES = [
    "resource", "weapon", "component", "vehicle_part", 
    "tool", "med", "ammo", "food", "misc"
]

# World Regions
WORLD_REGIONS = {
    "Forest": {
        "type": "forest",
        "danger": 20,
        "zombies": 0,
        "connected": ["Urban", "Coast"],
        "buildings": [],
        "properties": {"loot_modifier": 1.0}
    },
    "Urban": {
        "type": "urban", 
        "danger": 40,
        "zombies": 0,
        "connected": ["Forest", "Downtown"],
        "buildings": ["Warehouse", "Shop"],
        "properties": {"loot_modifier": 1.2}
    },
    "Downtown": {
        "type": "urban",
        "danger": 60,
        "zombies": 0,
        "connected": ["Urban", "Military"],
        "buildings": ["Hospital", "Office", "Mall"],
        "properties": {"loot_modifier": 1.5}
    },
    "Military": {
        "type": "military",
        "danger": 80,
        "zombies": 0,
        "connected": ["Downtown", "Coast"],
        "buildings": ["Base", "Armory", "Command"],
        "properties": {"loot_modifier": 2.0, "mutant_chance": 0.3}
    },
    "Coast": {
        "type": "coast",
        "danger": 30,
        "zombies": 0,
        "connected": ["Forest", "Military"],
        "buildings": ["Lighthouse", "Dock"],
        "properties": {"loot_modifier": 1.1}
    }
}

# Building Floors
BUILDING_FLOORS = {
    "Hospital": [
        {"floor": 1, "difficulty": 30, "zombies": 2, "loot_table": "hospital_floor_1"},
        {"floor": 2, "difficulty": 45, "zombies": 3, "loot_table": "hospital_floor_2"},
        {"floor": 3, "difficulty": 60, "zombies": 4, "loot_table": "hospital_floor_3"},
        {"floor": 4, "difficulty": 75, "zombies": 5, "loot_table": "hospital_floor_4"}
    ],
    "Office": [
        {"floor": 1, "difficulty": 25, "zombies": 1, "loot_table": "office_floor_1"},
        {"floor": 2, "difficulty": 35, "zombies": 2, "loot_table": "office_floor_2"},
        {"floor": 3, "difficulty": 50, "zombies": 3, "loot_table": "office_floor_3"}
    ],
    "Mall": [
        {"floor": 1, "difficulty": 40, "zombies": 3, "loot_table": "mall_floor_1"},
        {"floor": 2, "difficulty": 55, "zombies": 4, "loot_table": "mall_floor_2"},
        {"floor": 3, "difficulty": 70, "zombies": 5, "loot_table": "mall_floor_3"}
    ],
    "Base": [
        {"floor": 1, "difficulty": 60, "zombies": 4, "loot_table": "base_floor_1"},
        {"floor": 2, "difficulty": 80, "zombies": 6, "loot_table": "base_floor_2"},
        {"floor": 3, "difficulty": 100, "zombies": 8, "loot_table": "base_floor_3"}
    ]
}

# Vehicle Types
VEHICLE_TYPES = {
    "bike": {
        "name": "Bicycle",
        "condition_max": 100,
        "fuel_capacity": 0,
        "storage": 5,
        "speed": 1,
        "repair_cost": {"metal": 2}
    },
    "jeep": {
        "name": "Jeep",
        "condition_max": 100,
        "fuel_capacity": 50,
        "storage": 20,
        "speed": 3,
        "repair_cost": {"metal": 5, "circuit": 1}
    },
    "truck": {
        "name": "Truck",
        "condition_max": 100,
        "fuel_capacity": 100,
        "storage": 50,
        "speed": 2,
        "repair_cost": {"metal": 10, "circuit": 2}
    },
    "tank": {
        "name": "Tank",
        "condition_max": 100,
        "fuel_capacity": 200,
        "storage": 100,
        "speed": 1,
        "repair_cost": {"steel": 20, "circuit": 5}
    },
    "heli": {
        "name": "Helicopter",
        "condition_max": 100,
        "fuel_capacity": 150,
        "storage": 30,
        "speed": 5,
        "repair_cost": {"steel": 15, "circuit": 8}
    },
    "warship": {
        "name": "Warship",
        "condition_max": 100,
        "fuel_capacity": 500,
        "storage": 200,
        "speed": 2,
        "repair_cost": {"steel": 50, "circuit": 20}
    }
}

# File Paths
DATA_DIR = "data"
PLAYERS_FILE = f"{DATA_DIR}/players.txt"
INVENTORIES_FILE = f"{DATA_DIR}/inventories.txt"
WORLD_FILE = f"{DATA_DIR}/world.txt"
BUILDINGS_FILE = f"{DATA_DIR}/buildings.txt"
VEHICLES_FILE = f"{DATA_DIR}/vehicles.txt"
PENDING_ACTIONS_FILE = f"{DATA_DIR}/pending_actions.txt"
CONSTRUCTION_FILE = f"{DATA_DIR}/construction.txt"
EVENTS_FILE = f"{DATA_DIR}/events.txt"
LOGS_FILE = f"{DATA_DIR}/logs.txt"

# Asset Paths
MAP_OVERVIEW_PATH = f"{DATA_DIR}/assets/map_overview.png"
MAP_DETAILED_PATH = f"{DATA_DIR}/assets/map_detailed.png"

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/balletbot.log"

# Game Settings
MAX_PLAYERS_PER_GAME = 50
MAX_ACTIONS_HISTORY = 50
GAME_CODE_LENGTH = 6

# Safety Settings
RATE_LIMIT_WINDOW = 60  # seconds
MAX_COMMANDS_PER_WINDOW = 10
ADMIN_CONFIRMATION_REQUIRED = True

# Debug Settings
DEBUG_MODE = False
SIMULATION_MODE = False