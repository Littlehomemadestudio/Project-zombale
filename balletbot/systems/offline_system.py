"""
Offline system for BalletBot: Outbreak Dominion
Handles offline player actions (ambush, scavenge)
"""

import random
import logging
from typing import Dict, List, Optional, Any

from utils.helpers import get_current_timestamp
from utils.db import log_event
from config import OFFLINE_SCAVENGE_COOLDOWN

logger = logging.getLogger(__name__)

class OfflineSystem:
    """Manages offline player actions"""
    
    def __init__(self):
        self.offline_actions: Dict[str, Dict] = {}
    
    async def process_offline_player(self, player: Dict[str, Any]):
        """Process offline actions for a player"""
        player_id = player["id"]
        offline_mode = player.get("offline_mode", "none")
        
        if offline_mode == "ambush":
            await self._process_ambush_mode(player)
        elif offline_mode == "scavenge":
            await self._process_scavenge_mode(player)
    
    async def _process_ambush_mode(self, player: Dict[str, Any]):
        """Process ambush mode for offline player"""
        player_id = player["id"]
        location = player.get("location", "")
        
        # Check if any players are in the same location
        from systems.player_system import player_system
        nearby_players = player_system.get_players_in_location(location)
        
        # Filter out the ambushing player
        targets = [p for p in nearby_players if p["id"] != player_id and p.get("status") == "alive"]
        
        if targets:
            # Trigger ambush on random target
            target = random.choice(targets)
            await self._trigger_ambush(player, target)
    
    async def _trigger_ambush(self, ambusher: Dict[str, Any], target: Dict[str, Any]):
        """Trigger an ambush attack"""
        from systems.combat_system import combat_system
        
        # Create ambush action data
        action_data = {
            "target_id": target["id"],
            "weapon_damage": 25,  # Base ambush damage
            "ambush_bonus": True
        }
        
        # Trigger ambush combat
        combat_system.handle_ambush_trigger(ambusher["id"], action_data)
        
        log_event("ambush_triggered", {
            "ambusher_id": ambusher["id"],
            "target_id": target["id"],
            "location": ambusher.get("location", "")
        })
    
    async def _process_scavenge_mode(self, player: Dict[str, Any]):
        """Process scavenge mode for offline player"""
        player_id = player["id"]
        last_active = player.get("last_active", 0)
        current_time = get_current_timestamp()
        
        # Check if enough time has passed since last scavenge
        if current_time - last_active < OFFLINE_SCAVENGE_COOLDOWN:
            return
        
        # Get player location and region info
        location = player.get("location", "")
        region_name = location.split(":")[0] if ":" in location else "Forest"
        
        from core.world_manager import world_manager
        region = world_manager.get_region(region_name)
        
        if not region:
            return
        
        # Calculate scavenge success based on region danger and base defense
        success_chance = self._calculate_scavenge_success(region, player)
        
        if random.random() < success_chance:
            await self._give_scavenge_loot(player, region)
        
        # Update last active time
        from systems.player_system import player_system
        player_system.update_player(player_id, {"last_active": current_time})
    
    def _calculate_scavenge_success(self, region: Dict[str, Any], player: Dict[str, Any]) -> float:
        """Calculate scavenge success chance"""
        base_chance = 0.3
        region_danger = region.get("danger", 50)
        
        # Higher danger = lower success chance
        danger_penalty = region_danger * 0.002
        
        # Player intelligence helps
        intelligence_bonus = player.get("intelligence", 0) * 0.001
        
        # Base defense level (simplified)
        base_defense = 1.0  # TODO: Calculate based on player's base
        
        success_chance = base_chance - danger_penalty + intelligence_bonus + (base_defense * 0.1)
        
        return max(0.05, min(0.8, success_chance))  # Clamp between 5% and 80%
    
    async def _give_scavenge_loot(self, player: Dict[str, Any], region: Dict[str, Any]):
        """Give loot to player from scavenging"""
        from systems.inventory_system import inventory_system
        
        region_type = region.get("type", "forest")
        loot_items = self._get_scavenge_loot(region_type)
        
        for item_id, quantity in loot_items:
            inventory_system.add_item(player["id"], item_id, quantity)
        
        log_event("scavenge_success", {
            "player_id": player["id"],
            "region": region.get("name", "Unknown"),
            "loot": loot_items
        })
    
    def _get_scavenge_loot(self, region_type: str) -> List[tuple]:
        """Get loot items based on region type"""
        loot = []
        
        if region_type == "forest":
            loot.extend([
                ("wood", random.randint(1, 3)),
                ("herbs", random.randint(1, 2))
            ])
        elif region_type == "urban":
            loot.extend([
                ("metal", random.randint(1, 2)),
                ("cloth", random.randint(1, 2)),
                ("circuit", random.randint(0, 1))
            ])
        elif region_type == "military":
            loot.extend([
                ("ammo", random.randint(1, 3)),
                ("metal", random.randint(2, 4)),
                ("circuit", random.randint(1, 2))
            ])
        elif region_type == "coast":
            loot.extend([
                ("fish", random.randint(1, 2)),
                ("salt", random.randint(1, 2)),
                ("fuel", random.randint(0, 1))
            ])
        
        # Random chance for rare items
        if random.random() < 0.1:  # 10% chance
            rare_items = ["medkit", "repair_kit", "ammo"]
            rare_item = random.choice(rare_items)
            loot.append((rare_item, 1))
        
        return loot
    
    def set_offline_mode(self, player_id: str, mode: str, location: str = None) -> bool:
        """Set player offline mode"""
        from systems.player_system import player_system
        
        valid_modes = ["none", "ambush", "scavenge"]
        if mode not in valid_modes:
            return False
        
        updates = {"offline_mode": mode}
        if location:
            updates["location"] = location
        
        success = player_system.update_player(player_id, updates)
        
        if success:
            log_event("offline_mode_set", {
                "player_id": player_id,
                "mode": mode,
                "location": location
            })
        
        return success
    
    def get_offline_mode_display(self, mode: str) -> str:
        """Get formatted display for offline mode"""
        if mode == "ambush":
            return "🥷 **Ambush Mode**\nYou're lying in wait for enemies to enter your area."
        elif mode == "scavenge":
            return "🔍 **Scavenge Mode**\nYou're passively gathering resources from your location."
        else:
            return "😴 **No Offline Mode**\nYou're not performing any offline actions."
    
    def get_offline_players_count(self) -> Dict[str, int]:
        """Get count of players in each offline mode"""
        from utils.db import db
        
        result = db.execute_query("""
            SELECT offline_mode, COUNT(*) as count
            FROM players
            WHERE status = 'alive' AND offline_mode != 'none'
            GROUP BY offline_mode
        """)
        
        counts = {"ambush": 0, "scavenge": 0}
        for row in result:
            counts[row["offline_mode"]] = row["count"]
        
        return counts

# Global offline system instance
offline_system = OfflineSystem()