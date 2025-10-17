"""
BalletBot: Outbreak Dominion - Configuration
Default values and settings for the game
"""

# Time scaling for development/testing
TIME_MULTIPLIER = 1  # Scale long real durations for testing

# Game timing
DAY_LENGTH_SECONDS = 1800 * TIME_MULTIPLIER  # 30 minutes per day (scaled)
WORLD_TICK_SECONDS = 30  # Zombie/noise processing loop
DECISION_WINDOW = 7  # Seconds for building-floor sneak/attack (5-10 range)

# Map costs
MAP_FIRST_COST = {"wood": 10, "stone": 10}
MAP_DETAILED_COST = {"wood": 50, "stone": 25, "metal": 10}

# Spotter costs
SPOTTER_COST = {"circuit": 3, "metal": 5}

# Offline mechanics
OFFLINE_SCAVENGE_COOLDOWN = 3600  # seconds

# Vehicle mechanics
VEHICLE_CONDITION_THRESHOLD = 40  # minimum condition to drive
VEHICLE_REPAIR_RATE = 20  # condition restored per repair kit

# Construction
TANK_BUILD_DEFAULT_DAYS = 7  # create real-time duration (scaled via multiplier)

# Action cooldowns (in seconds)
ACTION_COOLDOWNS = {
    "move": 60,
    "loot": 30,
    "attack": 45,
    "craft": 120,
    "build": 300,
    "mine": 180,
    "chop": 120,
    "seek": 30,
    "radio": 10,
    "reload": 15
}

# Combat settings
BASE_SNEAK = 30
CRITICAL_HIT_CHANCE = 5  # percentage
ALERT_BONUS_DURATION = 120  # seconds

# Zombie spawn settings
BASE_SPAWN_PROBABILITY = 0.1
NOISE_THRESHOLD = 50
NIGHT_SPAWN_BONUS = 0.15

# Player class bonuses
CLASS_BONUSES = {
    "Scavenger": {"loot_yield": 0.10, "stealth": 10},
    "Mechanic": {"crafting_speed": 0.15, "intelligence_gain": 10},
    "Soldier": {"weapon_damage": 0.10, "health": 10}
}

# Default player stats
DEFAULT_STATS = {
    "hp": 100,
    "stamina": 100,
    "hunger": 0,
    "infection": 0,
    "intelligence": 0
}

# Map regions and their properties
REGIONS = {
    "Forest": {
        "type": "forest",
        "danger": 20,
        "zombies": 0,
        "connected": ["Downtown", "Coast"],
        "buildings": ["Camp"],
        "properties": {"resource_rich": True}
    },
    "Downtown": {
        "type": "urban",
        "danger": 60,
        "zombies": 0,
        "connected": ["Forest", "Military"],
        "buildings": ["Hospital", "Police Station", "Warehouse"],
        "properties": {"loot_rich": True}
    },
    "Military": {
        "type": "military",
        "danger": 90,
        "zombies": 0,
        "connected": ["Downtown"],
        "buildings": ["Bunker", "Armory"],
        "properties": {"high_tech": True, "cost_multiplier": 3}
    },
    "Coast": {
        "type": "coast",
        "danger": 40,
        "zombies": 0,
        "connected": ["Forest"],
        "buildings": ["Lighthouse", "Dock"],
        "properties": {"fishing": True}
    }
}

# Database file path
DB_PATH = "data/world.sqlite"

# Asset paths
ASSETS_PATH = "data/assets/"
MAP_OVERVIEW_PATH = "data/assets/map_overview.png"
MAP_DETAILED_PATH = "data/assets/map_detailed.png"