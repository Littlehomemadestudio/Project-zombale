"""
Helper functions for BalletBot: Outbreak Dominion
"""

import random
import time
import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta

def get_current_timestamp() -> int:
    """Get current Unix timestamp"""
    return int(time.time())

def generate_game_code() -> str:
    """Generate a random game code"""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choice(chars) for _ in range(6))

def format_duration(seconds: int) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"

def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))

def roll_dice(sides: int = 100) -> int:
    """Roll a dice with given sides"""
    return random.randint(1, sides)

def is_night_time() -> bool:
    """Check if it's currently night time"""
    # Simple day/night cycle based on hour
    current_hour = datetime.now().hour
    return current_hour < 6 or current_hour > 18

def get_day_phase() -> str:
    """Get current day phase"""
    current_hour = datetime.now().hour
    if current_hour < 6:
        return "night"
    elif current_hour < 12:
        return "morning"
    elif current_hour < 18:
        return "day"
    else:
        return "evening"

def sanitize_input(text: str, max_length: int = 100) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove special characters and limit length
    text = re.sub(r'[^\w\s\-.,!?]', '', text)
    text = text.strip()[:max_length]
    
    return text

def parse_location(location: str) -> Tuple[str, str, str]:
    """Parse location string into region, subarea, area"""
    parts = location.split(':')
    region = parts[0] if len(parts) > 0 else "Forest"
    subarea = parts[1] if len(parts) > 1 else "Camp"
    area = parts[2] if len(parts) > 2 else "Area1"
    
    return region, subarea, area

def format_location(region: str, subarea: str, area: str) -> str:
    """Format location string"""
    return f"{region}:{subarea}:{area}"

def calculate_stealth(player_data: Dict, zombie_alertness: int, is_night: bool) -> int:
    """Calculate sneak success chance"""
    base_sneak = 30
    sneak = base_sneak
    
    # Add player bonuses
    sneak += player_data.get('stealth_bonus', 0)
    sneak += player_data.get('stamina', 100) // 10
    
    # Subtract zombie alertness
    sneak -= zombie_alertness * 0.6
    
    # Night penalty
    if is_night:
        sneak -= 10
    
    return clamp(sneak, 1, 95)

def calculate_damage(weapon_damage: int, class_bonus: float = 0.0, 
                    critical_hit: bool = False, alerted_bonus: bool = False) -> int:
    """Calculate damage dealt"""
    damage = weapon_damage
    
    # Add random variation
    damage += random.randint(-5, 10)
    
    # Apply class bonus
    damage = int(damage * (1 + class_bonus))
    
    # Apply critical hit
    if critical_hit:
        damage = int(damage * 1.5)
    
    # Apply alerted bonus
    if alerted_bonus:
        damage = int(damage * 1.15)
    
    return max(1, damage)

def calculate_zombie_spawn_probability(region_danger: int, noise_level: int, 
                                     is_night: bool, base_chance: float = 0.1) -> float:
    """Calculate zombie spawn probability"""
    probability = base_chance
    probability += region_danger * 0.01
    probability += noise_level / 100
    
    if is_night:
        probability += 0.15
    
    return min(probability, 1.0)

def generate_zombie_stats(floor_difficulty: int) -> Dict[str, Any]:
    """Generate zombie stats for encounter"""
    base_hp = random.randint(20, 100)
    hp = int(base_hp * (1 + floor_difficulty / 100))
    
    return {
        "hp": hp,
        "alertness": random.randint(10, 90),
        "aggressiveness": random.randint(1, 10),
        "loot_modifier": random.uniform(0.8, 1.2)
    }

def calculate_loot_yield(base_yield: int, loot_modifier: float, 
                        class_bonus: float = 0.0) -> int:
    """Calculate loot yield"""
    yield_amount = int(base_yield * loot_modifier * (1 + class_bonus))
    return max(1, yield_amount)

def format_inventory(inventory: Dict[str, int]) -> str:
    """Format inventory for display"""
    if not inventory:
        return "Empty"
    
    items = []
    for item_id, quantity in inventory.items():
        items.append(f"{item_id} x{quantity}")
    
    return ", ".join(items)

def format_player_status(player_data: Dict) -> str:
    """Format player status for display"""
    status = f"👤 **{player_data.get('username', 'Unknown')}**\n"
    status += f"🏷️ Class: {player_data.get('class', 'Unknown')}\n"
    status += f"❤️ HP: {player_data.get('hp', 0)}/100\n"
    status += f"⚡ Stamina: {player_data.get('stamina', 0)}/100\n"
    status += f"🍖 Hunger: {player_data.get('hunger', 0)}/100\n"
    status += f"🦠 Infection: {player_data.get('infection', 0)}/100\n"
    status += f"🧠 Intelligence: {player_data.get('intelligence', 0)}\n"
    status += f"📍 Location: {player_data.get('location', 'Unknown')}\n"
    status += f"🛡️ Status: {player_data.get('status', 'alive')}\n"
    
    return status

def format_combat_result(attacker: str, defender: str, damage: int, 
                        critical: bool = False) -> str:
    """Format combat result message"""
    result = f"⚔️ **Combat Result**\n"
    result += f"🎯 {attacker} attacks {defender}\n"
    result += f"💥 Damage: {damage}"
    
    if critical:
        result += " (CRITICAL HIT!)"
    
    return result

def format_item_info(item_data: Dict) -> str:
    """Format item information"""
    info = f"📦 **{item_data.get('name', 'Unknown Item')}**\n"
    info += f"🏷️ Type: {item_data.get('type', 'Unknown')}\n"
    
    properties = item_data.get('properties', {})
    if properties:
        info += "📊 Properties:\n"
        for key, value in properties.items():
            info += f"  • {key}: {value}\n"
    
    return info

def format_recipe_info(recipe_data: Dict) -> str:
    """Format recipe information"""
    info = f"🔧 **{recipe_data.get('name', 'Unknown Recipe')}**\n"
    info += f"⏱️ Time: {recipe_data.get('time_required', 0)}s\n"
    info += f"🧠 Intelligence: {recipe_data.get('intelligence', 0)}\n"
    
    resources = recipe_data.get('resources', {})
    if resources:
        info += "📦 Resources needed:\n"
        for resource, qty in resources.items():
            info += f"  • {resource} x{qty}\n"
    
    return info

def calculate_distance(location1: str, location2: str) -> int:
    """Calculate distance between two locations"""
    # Simple distance calculation based on region
    regions = ["Forest", "Urban", "Downtown", "Military", "Coast"]
    
    try:
        region1, _, _ = parse_location(location1)
        region2, _, _ = parse_location(location2)
        
        if region1 == region2:
            return 1
        
        idx1 = regions.index(region1) if region1 in regions else 0
        idx2 = regions.index(region2) if region2 in regions else 0
        
        return abs(idx1 - idx2) + 1
    except:
        return 5  # Default distance

def is_valid_username(username: str) -> bool:
    """Validate username"""
    if not username or len(username) < 2 or len(username) > 20:
        return False
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False
    
    return True

def is_valid_class(class_name: str) -> bool:
    """Validate character class"""
    valid_classes = ["Scavenger", "Mechanic", "Soldier"]
    return class_name in valid_classes

def format_time_remaining(expire_time: int) -> str:
    """Format time remaining until expiration"""
    current_time = get_current_timestamp()
    remaining = expire_time - current_time
    
    if remaining <= 0:
        return "Expired"
    
    return format_duration(remaining)

def get_random_loot_item(loot_table: str) -> Optional[Tuple[str, int]]:
    """Get random loot item from loot table"""
    loot_tables = {
        "hospital_floor_1": [
            ("bandage", 2), ("cloth", 3), ("alcohol", 1)
        ],
        "hospital_floor_2": [
            ("medkit", 1), ("bandage", 3), ("alcohol", 2)
        ],
        "office_floor_1": [
            ("paper", 5), ("pen", 2), ("circuit", 1)
        ],
        "mall_floor_1": [
            ("cloth", 4), ("food", 3), ("battery", 2)
        ],
        "base_floor_1": [
            ("ammo", 10), ("metal", 5), ("circuit", 3)
        ]
    }
    
    items = loot_tables.get(loot_table, [])
    if not items:
        return None
    
    return random.choice(items)

def add_action_to_history(player_id: str, action: str, **kwargs):
    """Add action to player history"""
    from utils.file_manager import file_manager
    
    player_data = file_manager.get_player(player_id)
    if not player_data:
        return
    
    actions = player_data.get('last_actions', [])
    action_entry = {
        "action": action,
        "timestamp": get_current_timestamp(),
        **kwargs
    }
    
    actions.append(action_entry)
    
    # Keep only last 50 actions
    if len(actions) > 50:
        actions = actions[-50:]
    
    player_data['last_actions'] = actions
    file_manager.save_player(player_id, player_data)

def get_action_history(player_id: str, limit: int = 10) -> List[Dict]:
    """Get player action history"""
    from utils.file_manager import file_manager
    
    player_data = file_manager.get_player(player_id)
    if not player_data:
        return []
    
    actions = player_data.get('last_actions', [])
    return actions[-limit:] if actions else []