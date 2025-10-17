"""
Zombie system for BalletBot: Outbreak Dominion
Manages zombie AI, spawning, and encounters
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp, calculate_zombie_spawn_probability, generate_zombie_stats
from config import ZOMBIE_BASE_SPAWN_CHANCE, ZOMBIE_NOISE_THRESHOLD, ZOMBIE_NIGHT_BONUS

logger = logging.getLogger(__name__)

class ZombieSystem:
    """Manages zombie AI and spawning"""
    
    def __init__(self):
        self.zombie_types = {
            "walker": {
                "name": "Walker",
                "base_hp": 50,
                "base_damage": 15,
                "speed": 1,
                "alertness_range": 20,
                "description": "Slow but persistent zombie"
            },
            "runner": {
                "name": "Runner", 
                "base_hp": 30,
                "base_damage": 20,
                "speed": 3,
                "alertness_range": 30,
                "description": "Fast and aggressive zombie"
            },
            "brute": {
                "name": "Brute",
                "base_hp": 100,
                "base_damage": 25,
                "speed": 1,
                "alertness_range": 15,
                "description": "Strong but slow zombie"
            },
            "mutant": {
                "name": "Mutant",
                "base_hp": 80,
                "base_damage": 30,
                "speed": 2,
                "alertness_range": 25,
                "description": "Enhanced zombie with special abilities"
            }
        }
    
    def calculate_spawn_probability(self, region_danger: int, noise_level: int, is_night: bool) -> float:
        """Calculate zombie spawn probability for a region"""
        return calculate_zombie_spawn_probability(
            region_danger, 
            noise_level, 
            is_night, 
            ZOMBIE_BASE_SPAWN_CHANCE
        )
    
    def spawn_zombies(self, region_name: str, spawn_count: int) -> List[Dict]:
        """Spawn zombies in a region"""
        try:
            spawned_zombies = []
            
            for _ in range(spawn_count):
                zombie = self.generate_zombie(region_name.lower())
                if zombie:
                    spawned_zombies.append(zombie)
            
            # Update region zombie count
            region_data = file_manager.get_region(region_name)
            if region_data:
                current_zombies = region_data.get("zombies", 0)
                region_data["zombies"] = current_zombies + len(spawned_zombies)
                file_manager.save_region(region_name, region_data)
            
            logger.info(f"Spawned {len(spawned_zombies)} zombies in {region_name}")
            return spawned_zombies
            
        except Exception as e:
            logger.error(f"Error spawning zombies in {region_name}: {e}")
            return []
    
    def generate_zombie(self, region_type: str) -> Optional[Dict]:
        """Generate a zombie for encounter"""
        try:
            # Determine zombie type based on region
            zombie_type = self._select_zombie_type(region_type)
            type_data = self.zombie_types[zombie_type]
            
            # Generate stats
            stats = generate_zombie_stats(0)  # Base difficulty
            
            # Create zombie
            zombie = {
                "id": f"zombie_{get_current_timestamp()}_{random.randint(1000, 9999)}",
                "type": zombie_type,
                "name": type_data["name"],
                "hp": type_data["base_hp"] + random.randint(-10, 20),
                "max_hp": type_data["base_hp"] + random.randint(-10, 20),
                "damage": type_data["base_damage"] + random.randint(-5, 10),
                "speed": type_data["speed"],
                "alertness": stats["alertness"],
                "aggressiveness": stats["aggressiveness"],
                "loot_modifier": stats["loot_modifier"],
                "alertness_range": type_data["alertness_range"],
                "created_at": get_current_timestamp(),
                "status": "alive"
            }
            
            return zombie
            
        except Exception as e:
            logger.error(f"Error generating zombie: {e}")
            return None
    
    def _select_zombie_type(self, region_type: str) -> str:
        """Select zombie type based on region"""
        # Base probabilities
        type_probs = {
            "walker": 0.6,
            "runner": 0.25,
            "brute": 0.10,
            "mutant": 0.05
        }
        
        # Adjust probabilities based on region
        if region_type in ["military", "base"]:
            type_probs["mutant"] = 0.3
            type_probs["brute"] = 0.2
            type_probs["walker"] = 0.4
            type_probs["runner"] = 0.1
        elif region_type in ["urban", "downtown"]:
            type_probs["runner"] = 0.4
            type_probs["walker"] = 0.5
            type_probs["brute"] = 0.08
            type_probs["mutant"] = 0.02
        elif region_type in ["forest", "coast"]:
            type_probs["walker"] = 0.7
            type_probs["runner"] = 0.2
            type_probs["brute"] = 0.08
            type_probs["mutant"] = 0.02
        
        # Roll for type
        roll = random.random()
        cumulative = 0
        
        for zombie_type, prob in type_probs.items():
            cumulative += prob
            if roll <= cumulative:
                return zombie_type
        
        return "walker"  # Fallback
    
    def process_zombie_ai(self, zombie: Dict, player_location: str) -> Dict[str, Any]:
        """Process zombie AI behavior"""
        try:
            # Simple AI: move towards noise/players
            actions = []
            
            # Check for nearby players
            nearby_players = self._get_nearby_players(player_location, zombie["alertness_range"])
            
            if nearby_players:
                # Move towards nearest player
                nearest_player = nearby_players[0]
                actions.append({
                    "type": "move_towards",
                    "target": nearest_player["id"],
                    "target_location": nearest_player["location"]
                })
                
                # Check if close enough to attack
                if self._is_within_attack_range(zombie, nearest_player):
                    actions.append({
                        "type": "attack",
                        "target": nearest_player["id"]
                    })
            else:
                # Random movement
                actions.append({
                    "type": "wander",
                    "direction": random.choice(["north", "south", "east", "west"])
                })
            
            return {
                "zombie_id": zombie["id"],
                "actions": actions,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error processing zombie AI: {e}")
            return {"zombie_id": zombie["id"], "actions": [], "status": "error"}
    
    def _get_nearby_players(self, location: str, range_distance: int) -> List[Dict]:
        """Get players within range of zombie"""
        try:
            from systems.player_system import player_system
            
            # Get all players
            all_players = file_manager.get_all_players()
            nearby_players = []
            
            for player_data in all_players.values():
                if player_data.get("status") != "alive":
                    continue
                
                player_location = player_data.get("location", "")
                if self._calculate_distance(location, player_location) <= range_distance:
                    nearby_players.append(player_data)
            
            return nearby_players
            
        except Exception as e:
            logger.error(f"Error getting nearby players: {e}")
            return []
    
    def _calculate_distance(self, loc1: str, loc2: str) -> int:
        """Calculate distance between two locations"""
        # Simple distance calculation
        if loc1 == loc2:
            return 0
        
        # Parse locations
        parts1 = loc1.split(":")
        parts2 = loc2.split(":")
        
        if len(parts1) >= 1 and len(parts2) >= 1:
            region1 = parts1[0]
            region2 = parts2[0]
            
            if region1 == region2:
                return 1
            else:
                return 3  # Different regions
        
        return 5  # Default distance
    
    def _is_within_attack_range(self, zombie: Dict, player: Dict) -> bool:
        """Check if zombie is within attack range of player"""
        # Simple range check
        return self._calculate_distance(zombie.get("location", ""), player.get("location", "")) <= 1
    
    def calculate_zombie_damage(self, zombie: Dict, player_data: Dict) -> int:
        """Calculate damage dealt by zombie"""
        try:
            base_damage = zombie.get("damage", 15)
            
            # Apply random variation
            damage = base_damage + random.randint(-3, 7)
            
            # Apply armor reduction (if player has armor)
            armor = player_data.get("armor", 0)
            damage = max(1, damage - armor)
            
            return damage
            
        except Exception as e:
            logger.error(f"Error calculating zombie damage: {e}")
            return 15  # Default damage
    
    def get_zombie_loot(self, zombie: Dict) -> List[Tuple[str, int]]:
        """Get loot dropped by zombie"""
        try:
            loot_items = []
            zombie_type = zombie.get("type", "walker")
            
            # Base loot chances
            loot_chances = {
                "walker": {"cloth": 0.3, "bone": 0.2, "rotten_flesh": 0.5},
                "runner": {"cloth": 0.4, "bone": 0.3, "rotten_flesh": 0.6},
                "brute": {"bone": 0.5, "rotten_flesh": 0.7, "metal": 0.2},
                "mutant": {"bone": 0.6, "rotten_flesh": 0.8, "metal": 0.4, "circuit": 0.1}
            }
            
            chances = loot_chances.get(zombie_type, loot_chances["walker"])
            
            for item, chance in chances.items():
                if random.random() < chance:
                    quantity = random.randint(1, 3)
                    loot_items.append((item, quantity))
            
            return loot_items
            
        except Exception as e:
            logger.error(f"Error getting zombie loot: {e}")
            return []
    
    def format_zombie_info(self, zombie: Dict) -> str:
        """Format zombie information for display"""
        info = f"🧟 **{zombie.get('name', 'Zombie')}**\n"
        info += f"❤️ HP: {zombie.get('hp', 0)}/{zombie.get('max_hp', 0)}\n"
        info += f"⚔️ Damage: {zombie.get('damage', 0)}\n"
        info += f"👁️ Alertness: {zombie.get('alertness', 0)}%\n"
        info += f"🏃 Speed: {zombie.get('speed', 0)}\n"
        info += f"📝 {self.zombie_types.get(zombie.get('type', 'walker'), {}).get('description', 'Unknown zombie')}\n"
        
        return info
    
    def get_zombie_types(self) -> Dict[str, Dict]:
        """Get all zombie types"""
        return self.zombie_types.copy()
    
    def get_region_zombie_count(self, region_name: str) -> int:
        """Get zombie count in region"""
        try:
            region_data = file_manager.get_region(region_name)
            if region_data:
                return region_data.get("zombies", 0)
            return 0
            
        except Exception as e:
            logger.error(f"Error getting zombie count for {region_name}: {e}")
            return 0
    
    def update_region_zombies(self, region_name: str, change: int):
        """Update zombie count in region"""
        try:
            region_data = file_manager.get_region(region_name)
            if region_data:
                current_zombies = region_data.get("zombies", 0)
                region_data["zombies"] = max(0, current_zombies + change)
                file_manager.save_region(region_name, region_data)
                
        except Exception as e:
            logger.error(f"Error updating zombie count for {region_name}: {e}")
    
    def process_zombie_movement(self, region_name: str):
        """Process zombie movement between regions"""
        try:
            region_data = file_manager.get_region(region_name)
            if not region_data:
                return
            
            current_zombies = region_data.get("zombies", 0)
            if current_zombies <= 0:
                return
            
            # Check for noise in connected regions
            connected_regions = region_data.get("connected", [])
            noise_threshold = ZOMBIE_NOISE_THRESHOLD
            
            for connected_region in connected_regions:
                connected_data = file_manager.get_region(connected_region)
                if connected_data:
                    # Simple noise calculation (could be based on player activity)
                    noise_level = random.randint(0, 100)
                    
                    if noise_level > noise_threshold and current_zombies > 0:
                        # Move some zombies to the noisy region
                        zombies_to_move = min(current_zombies, random.randint(1, 3))
                        
                        # Update both regions
                        region_data["zombies"] = current_zombies - zombies_to_move
                        connected_data["zombies"] = connected_data.get("zombies", 0) + zombies_to_move
                        
                        file_manager.save_region(region_name, region_data)
                        file_manager.save_region(connected_region, connected_data)
                        
                        logger.info(f"Moved {zombies_to_move} zombies from {region_name} to {connected_region}")
                        break
            
        except Exception as e:
            logger.error(f"Error processing zombie movement: {e}")

# Global zombie system instance
zombie_system = ZombieSystem()