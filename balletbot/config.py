"""
Configuration settings for BalletBot: Outbreak Dominion
"""

# Time scaling for development/testing
TIME_MULTIPLIER = 1  # Set to 0.1 for 10x faster, 10 for 10x slower

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
OFFLINE_SCAVENGE_COOLDOWN = 3600  # 1 hour in seconds

# Vehicle mechanics
VEHICLE_CONDITION_THRESHOLD = 40  # Minimum condition to drive
VEHICLE_REPAIR_RATE = 20  # Condition restored per repair kit

# Construction
TANK_BUILD_DEFAULT_DAYS = 7  # Create real-time duration; scaled via multiplier

# Action cooldowns (in seconds)
ACTION_COOLDOWNS = {
    "move": 30,
    "loot": 60,
    "attack": 10,
    "reload": 5,
    "craft": 120,
    "mine": 300,
    "chop": 300,
    "seek": 60,
    "radio": 10,
    "intel": 300,
}

# Combat settings
COMBAT_CRITICAL_HIT_CHANCE = 5  # Percentage
COMBAT_ALERTED_BONUS = 15  # Damage/initiative bonus when alerted
COMBAT_AMBUSH_BONUS = 100  # Double damage for first strike in ambush

# Zombie spawn settings
ZOMBIE_BASE_SPAWN_RATE = 0.1  # Base probability per tick
ZOMBIE_NIGHT_BONUS = 0.15  # Additional spawn chance at night
ZOMBIE_NOISE_THRESHOLD = 50  # Noise level that attracts zombies

# Player stats
PLAYER_MAX_HP = 100
PLAYER_MAX_STAMINA = 100
PLAYER_MAX_HUNGER = 100
PLAYER_MAX_INFECTION = 100
PLAYER_MAX_INTELLIGENCE = 100

# Character class bonuses
CLASS_BONUSES = {
    "Scavenger": {
        "loot_yield": 1.1,  # +10%
        "stealth": 10,
    },
    "Mechanic": {
        "crafting_speed": 1.15,  # +15%
        "intelligence_gain": 10,
    },
    "Soldier": {
        "weapon_damage": 1.1,  # +10%
        "health": 10,
    }
}

# Map region types and their properties
REGION_TYPES = {
    "forest": {
        "danger": 20,
        "resources": ["wood", "herbs"],
        "buildings": ["camp", "cabin"]
    },
    "urban": {
        "danger": 60,
        "resources": ["metal", "circuit", "cloth"],
        "buildings": ["hospital", "police_station", "store"]
    },
    "military": {
        "danger": 80,
        "resources": ["ammo", "weapon_parts", "fuel"],
        "buildings": ["bunker", "armory", "command_center"]
    },
    "coast": {
        "danger": 40,
        "resources": ["fish", "salt", "fuel"],
        "buildings": ["lighthouse", "harbor", "research_station"]
    }
}

# Database settings
DATABASE_PATH = "data/world.sqlite"

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# File paths
ASSETS_PATH = "data/assets"
MAP_OVERVIEW_PATH = f"{ASSETS_PATH}/map_overview.png"
MAP_DETAILED_PATH = f"{ASSETS_PATH}/map_detailed.png"
RECIPES_PATH = "data/recipes.json"
ITEMS_PATH = "data/items.json"

# Game codes
GAME_CODE_LENGTH = 6
GAME_CODE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# Safety settings
MAX_MESSAGE_LENGTH = 4000
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_COMMANDS = 10  # per window per user

# Admin settings
ADMIN_CONFIRMATION_TIMEOUT = 30  # seconds for dangerous commands

def get_scaled_duration(seconds: int) -> int:
    """Get duration scaled by TIME_MULTIPLIER"""
    return int(seconds * TIME_MULTIPLIER)

def get_scaled_days(days: int) -> int:
    """Get days converted to seconds and scaled by TIME_MULTIPLIER"""
    return get_scaled_duration(days * 24 * 3600)