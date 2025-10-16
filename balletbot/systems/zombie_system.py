"""
Zombie system for BalletBot: Outbreak Dominion
Handles zombie AI, spawning, and behavior
"""

import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from utils.helpers import get_current_timestamp, roll_percentage, clamp
from utils.db import log_event
from config import ZOMBIE_BASE_SPAWN_RATE, ZOMBIE_NIGHT_BONUS, ZOMBIE_NOISE_THRESHOLD

logger = logging.getLogger(__name__)

class ZombieSystem:
    """Manages zombie spawning, AI, and behavior"""
    
    def __init__(self):
        self.zombie_types = {
            "normal": {
                "base_hp": 50,
                "damage": 20,
                "speed": 1,
                "spawn_weight": 70
            },
            "fast": {
                "base_hp": 30,
                "damage": 15,
                "speed": 2,
                "spawn_weight": 20
            },
            "tank": {
                "base_hp": 100,
                "damage": 35,
                "speed": 0.5,
                "spawn_weight": 8
            },
            "mutant": {
                "base_hp": 80,
                "damage": 40,
                "speed": 1.5,
                "spawn_weight": 2
            }
        }
    
    def calculate_spawn_probability(self, region_danger: int, noise_level: int, 
                                  is_night: bool = False) -> float:
        """Calculate zombie spawn probability for a region"""
        probability = ZOMBIE_BASE_SPAWN_RATE
        probability += region_danger * 0.01
        probability += min(noise_level / ZOMBIE_NOISE_THRESHOLD, 1.0) * 0.2
        probability += ZOMBIE_NIGHT_BONUS if is_night else 0
        
        return clamp(probability, 0.0, 1.0)
    
    def calculate_zombie_spawn_count(self, spawn_probability: float) -> int:
        """Calculate number of zombies to spawn based on probability"""
        if spawn_probability <= 0:
            return 0
        
        # Use weighted random to determine spawn count
        spawn_weights = [
            (0, 1.0 - spawn_probability),  # No spawn
            (1, spawn_probability * 0.7),  # 1 zombie
            (2, spawn_probability * 0.2),  # 2 zombies
            (3, spawn_probability * 0.08), # 3 zombies
            (4, spawn_probability * 0.02)  # 4+ zombies
        ]
        
        # Normalize weights
        total_weight = sum(weight for _, weight in spawn_weights)
        normalized_weights = [(count, weight / total_weight) for count, weight in spawn_weights]
        
        # Random selection
        rand = random.random()
        cumulative = 0
        
        for count, weight in normalized_weights:
            cumulative += weight
            if rand <= cumulative:
                return count
        
        return 0
    
    def generate_zombie(self, region_type: str = "urban", floor_difficulty: int = 0) -> Dict[str, Any]:
        """Generate a zombie with random stats"""
        # Select zombie type based on region and weights
        zombie_type = self._select_zombie_type(region_type)
        base_stats = self.zombie_types[zombie_type]
        
        # Calculate stats with difficulty modifier
        difficulty_modifier = 1 + (floor_difficulty / 100)
        
        hp = int(base_stats["base_hp"] * difficulty_modifier * random.uniform(0.8, 1.2))
        damage = int(base_stats["damage"] * difficulty_modifier * random.uniform(0.9, 1.1))
        speed = base_stats["speed"] * random.uniform(0.9, 1.1)
        
        # Generate alertness (affects sneak success)
        alertness = random.randint(10, 90)
        
        # Generate aggressiveness (affects combat initiative)
        aggressiveness = random.randint(1, 100)
        
        zombie = {
            "id": f"zombie_{get_current_timestamp()}_{random.randint(1000, 9999)}",
            "type": zombie_type,
            "hp": hp,
            "max_hp": hp,
            "damage": damage,
            "speed": speed,
            "alertness": alertness,
            "aggressiveness": aggressiveness,
            "spawn_time": get_current_timestamp(),
            "last_action": get_current_timestamp()
        }
        
        return zombie
    
    def _select_zombie_type(self, region_type: str) -> str:
        """Select zombie type based on region and weights"""
        # Adjust weights based on region type
        weights = self.zombie_types.copy()
        
        if region_type == "military":
            # Military areas have more dangerous zombies
            weights["mutant"]["spawn_weight"] *= 3
            weights["tank"]["spawn_weight"] *= 2
        elif region_type == "forest":
            # Forest areas have more fast zombies
            weights["fast"]["spawn_weight"] *= 1.5
        elif region_type == "coast":
            # Coast areas have more normal zombies
            weights["normal"]["spawn_weight"] *= 1.2
        
        # Calculate total weight
        total_weight = sum(zombie["spawn_weight"] for zombie in weights.values())
        
        # Random selection
        rand = random.random() * total_weight
        cumulative = 0
        
        for zombie_type, stats in weights.items():
            cumulative += stats["spawn_weight"]
            if rand <= cumulative:
                return zombie_type
        
        return "normal"  # Fallback
    
    def calculate_zombie_alertness(self, zombie: Dict[str, Any], 
                                 player_stealth: int, is_night: bool = False) -> int:
        """Calculate zombie alertness for sneak attempts"""
        base_alertness = zombie.get("alertness", 50)
        
        # Night reduces alertness
        if is_night:
            base_alertness -= 10
        
        # Player stealth reduces alertness
        base_alertness -= player_stealth // 2
        
        return clamp(base_alertness, 5, 95)
    
    def calculate_zombie_damage(self, zombie: Dict[str, Any], 
                              player_armor: int = 0) -> int:
        """Calculate damage dealt by zombie"""
        base_damage = zombie.get("damage", 20)
        
        # Add random variation
        damage = base_damage + random.randint(-5, 10)
        
        # Apply armor reduction
        damage = max(1, damage - player_armor)
        
        return damage
    
    def process_zombie_ai(self, zombie: Dict[str, Any], 
                         player_location: str, noise_level: int) -> str:
        """Process zombie AI and return action"""
        current_time = get_current_timestamp()
        
        # Check if zombie should act
        if current_time - zombie.get("last_action", 0) < 30:  # 30 second cooldown
            return "wait"
        
        # Update last action time
        zombie["last_action"] = current_time
        
        # Simple AI: move toward noise or player
        if noise_level > ZOMBIE_NOISE_THRESHOLD:
            return "investigate_noise"
        elif player_location:
            return "hunt_player"
        else:
            return "wander"
    
    def get_zombie_display(self, zombie: Dict[str, Any]) -> str:
        """Get formatted zombie display"""
        zombie_type = zombie.get("type", "normal").title()
        hp = zombie.get("hp", 0)
        max_hp = zombie.get("max_hp", 100)
        damage = zombie.get("damage", 20)
        
        # Health bar
        health_percent = (hp / max_hp) * 100
        health_bar = "█" * int(health_percent // 10) + "░" * (10 - int(health_percent // 10))
        
        return f"""
🧟 **{zombie_type} Zombie**
❤️ HP: {hp}/{max_hp} [{health_bar}]
⚔️ Damage: {damage}
👁️ Alertness: {zombie.get('alertness', 50)}
        """.strip()
    
    def get_zombie_encounter_text(self, zombies: List[Dict[str, Any]]) -> str:
        """Get formatted encounter text for multiple zombies"""
        if not zombies:
            return "The area appears to be clear of zombies."
        
        if len(zombies) == 1:
            zombie = zombies[0]
            return f"You encounter a {zombie.get('type', 'normal')} zombie!\n\n{self.get_zombie_display(zombie)}"
        else:
            text = f"You encounter {len(zombies)} zombies!\n\n"
            for i, zombie in enumerate(zombies, 1):
                text += f"**Zombie {i}:**\n{self.get_zombie_display(zombie)}\n\n"
            return text.strip()
    
    def calculate_zombie_spawn_for_region(self, region_name: str, 
                                        region_danger: int, noise_level: int,
                                        is_night: bool = False) -> List[Dict[str, Any]]:
        """Calculate and generate zombies for a region"""
        spawn_prob = self.calculate_spawn_probability(region_danger, noise_level, is_night)
        spawn_count = self.calculate_zombie_spawn_count(spawn_prob)
        
        zombies = []
        for _ in range(spawn_count):
            zombie = self.generate_zombie(region_name.lower(), region_danger)
            zombies.append(zombie)
        
        if zombies:
            log_event("zombies_spawned", {
                "region": region_name,
                "count": len(zombies),
                "types": [z["type"] for z in zombies]
            })
        
        return zombies
    
    def process_zombie_combat(self, zombie: Dict[str, Any], 
                            player_damage: int) -> Dict[str, Any]:
        """Process zombie taking damage in combat"""
        current_hp = zombie.get("hp", 0)
        new_hp = max(0, current_hp - player_damage)
        
        zombie["hp"] = new_hp
        
        result = {
            "zombie_died": new_hp <= 0,
            "damage_dealt": player_damage,
            "zombie_hp": new_hp
        }
        
        if new_hp <= 0:
            log_event("zombie_killed", {
                "zombie_id": zombie.get("id"),
                "zombie_type": zombie.get("type"),
                "damage_dealt": player_damage
            })
        
        return result
    
    def get_zombie_loot(self, zombie: Dict[str, Any]) -> List[Tuple[str, int]]:
        """Get loot dropped by zombie"""
        zombie_type = zombie.get("type", "normal")
        loot = []
        
        # Base loot chance
        loot_chance = 0.3
        
        # Type-specific loot
        if zombie_type == "normal":
            if random.random() < loot_chance:
                loot.append(("cloth", random.randint(1, 2)))
        elif zombie_type == "fast":
            if random.random() < loot_chance * 0.8:
                loot.append(("metal", random.randint(1, 2)))
        elif zombie_type == "tank":
            if random.random() < loot_chance * 1.5:
                loot.append(("metal", random.randint(2, 4)))
                loot.append(("ammo", random.randint(1, 3)))
        elif zombie_type == "mutant":
            if random.random() < loot_chance * 2.0:
                loot.append(("circuit", random.randint(1, 2)))
                loot.append(("ammo", random.randint(2, 5)))
        
        return loot

# Global zombie system instance
zombie_system = ZombieSystem()