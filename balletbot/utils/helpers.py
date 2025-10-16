"""
Helper utilities for BalletBot: Outbreak Dominion
"""

import random
import string
import time
from typing import Any, Dict, List, Optional, Tuple
from config import GAME_CODE_LENGTH, GAME_CODE_CHARS, TIME_MULTIPLIER

def generate_game_code() -> str:
    """Generate a random game code"""
    return ''.join(random.choices(GAME_CODE_CHARS, k=GAME_CODE_LENGTH))

def get_current_timestamp() -> int:
    """Get current Unix timestamp"""
    return int(time.time())

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(value, max_val))

def roll_dice(sides: int = 100) -> int:
    """Roll a dice with given number of sides"""
    return random.randint(1, sides)

def roll_percentage() -> int:
    """Roll a percentage (1-100)"""
    return roll_dice(100)

def calculate_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Calculate Euclidean distance between two positions"""
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

def is_night_time() -> bool:
    """Check if it's currently night time in game"""
    from config import DAY_LENGTH_SECONDS
    current_time = get_current_timestamp()
    day_phase = (current_time % DAY_LENGTH_SECONDS) / DAY_LENGTH_SECONDS
    return day_phase > 0.5  # Night is second half of day

def get_day_phase() -> str:
    """Get current day phase"""
    return "night" if is_night_time() else "day"

def sanitize_input(text: str, max_length: int = 100) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()

def parse_location(location: str) -> Tuple[str, str, str]:
    """Parse location string into region, subarea, building"""
    parts = location.split(':')
    region = parts[0] if len(parts) > 0 else "Forest"
    subarea = parts[1] if len(parts) > 1 else "Camp"
    building = parts[2] if len(parts) > 2 else "Area1"
    return region, subarea, building

def format_location(region: str, subarea: str, building: str = None) -> str:
    """Format location components into location string"""
    if building:
        return f"{region}:{subarea}:{building}"
    return f"{region}:{subarea}"

def calculate_stealth_success(player_stealth: int, zombie_alertness: int, 
                             is_night: bool = False) -> bool:
    """Calculate if sneak attempt succeeds"""
    from config import COMBAT_CRITICAL_HIT_CHANCE
    
    base_sneak = 30
    sneak = base_sneak
    sneak += player_stealth
    sneak -= zombie_alertness * 0.6
    sneak -= 10 if is_night else 0
    sneak = clamp(sneak, 1, 95)
    
    return roll_percentage() <= sneak

def calculate_combat_damage(weapon_damage: int, class_bonus: float = 1.0, 
                           is_critical: bool = False) -> int:
    """Calculate combat damage"""
    damage = weapon_damage * class_bonus
    damage += random.randint(-5, 10)  # Random variation
    
    if is_critical:
        damage *= 2
    
    return max(1, int(damage))

def calculate_zombie_spawn_probability(region_danger: int, noise_level: int, 
                                     is_night: bool = False) -> float:
    """Calculate zombie spawn probability for a region"""
    from config import ZOMBIE_BASE_SPAWN_RATE, ZOMBIE_NIGHT_BONUS, ZOMBIE_NOISE_THRESHOLD
    
    probability = ZOMBIE_BASE_SPAWN_RATE
    probability += region_danger * 0.01
    probability += min(noise_level / ZOMBIE_NOISE_THRESHOLD, 1.0) * 0.2
    probability += ZOMBIE_NIGHT_BONUS if is_night else 0
    
    return clamp(probability, 0.0, 1.0)

def format_inventory_item(item: Dict[str, Any]) -> str:
    """Format inventory item for display"""
    name = item.get('name', 'Unknown Item')
    qty = item.get('qty', 0)
    item_type = item.get('type', 'unknown')
    
    return f"• {name} x{qty} ({item_type})"

def format_player_stats(player: Dict[str, Any]) -> str:
    """Format player stats for display"""
    return f"""
🩺 HP: {player.get('hp', 0)}/100
⚡ Stamina: {player.get('stamina', 0)}/100
🍖 Hunger: {player.get('hunger', 0)}/100
🦠 Infection: {player.get('infection', 0)}/100
🧠 Intelligence: {player.get('intelligence', 0)}/100
📍 Location: {player.get('location', 'Unknown')}
🏠 Shelter: {player.get('shelter_id', 'None')}
👤 Status: {player.get('status', 'Unknown')}
    """.strip()

def get_scaled_time() -> int:
    """Get current time scaled by TIME_MULTIPLIER"""
    return int(time.time() * TIME_MULTIPLIER)

def is_action_available(player_id: str, action: str, last_actions: List[Dict]) -> bool:
    """Check if action is available based on cooldowns"""
    from config import ACTION_COOLDOWNS
    
    if action not in ACTION_COOLDOWNS:
        return True
    
    cooldown = ACTION_COOLDOWNS[action]
    current_time = get_current_timestamp()
    
    # Check last action time
    for action_data in reversed(last_actions):
        if action_data.get('action') == action:
            last_time = action_data.get('timestamp', 0)
            if current_time - last_time < cooldown:
                return False
            break
    
    return True

def add_action_to_history(player_id: str, action: str, details: Dict = None) -> Dict:
    """Add action to player's action history"""
    action_data = {
        'action': action,
        'timestamp': get_current_timestamp(),
        'details': details or {}
    }
    return action_data

def truncate_action_history(actions: List[Dict], max_actions: int = 50) -> List[Dict]:
    """Truncate action history to max length"""
    return actions[-max_actions:] if len(actions) > max_actions else actions