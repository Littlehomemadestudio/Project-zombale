"""
Building system for BalletBot: Outbreak Dominion
Handles building entry, floor encounters, and decision windows
"""

import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from utils.helpers import get_current_timestamp, parse_location
from utils.db import log_event
from config import DECISION_WINDOW

logger = logging.getLogger(__name__)

class BuildingSystem:
    """Manages building entry and floor encounters"""
    
    def __init__(self):
        self.active_encounters: Dict[str, Dict] = {}
    
    def enter_building(self, player_id: str, building_name: str) -> Dict[str, Any]:
        """Enter a building"""
        from systems.player_system import player_system
        from core.world_manager import world_manager
        
        player = player_system.get_player(player_id)
        if not player:
            return {"success": False, "error": "Player not found"}
        
        location = player.get("location", "")
        region, subarea, _ = parse_location(location)
        
        # Find building
        building_id = f"{region}:{building_name}"
        building = world_manager.get_building(building_id)
        
        if not building:
            return {"success": False, "error": f"Building {building_name} not found in {region}"}
        
        # Get building floors
        floors = world_manager.get_building_floors(building_id)
        if not floors:
            return {"success": False, "error": "Building has no floors"}
        
        # Create building entry display
        display = self._create_building_display(building, floors, player_id)
        
        return {
            "success": True,
            "building_id": building_id,
            "building_name": building_name,
            "floors": floors,
            "display": display
        }
    
    def _create_building_display(self, building: Dict[str, Any], 
                               floors: List[Dict[str, Any]], 
                               player_id: str) -> str:
        """Create formatted building display"""
        building_name = building.get("name", "Unknown Building")
        region = building.get("region", "Unknown")
        
        display = f"🏢 **{building_name}** ({region})\n\n"
        display += "**Available Floors:**\n"
        
        for floor in floors:
            floor_num = floor.get("floor", 0)
            difficulty = floor.get("difficulty", 0)
            zombies = floor.get("zombies", 0)
            
            # Check if floor is cleared
            cleared_by = building.get("cleared_by", {})
            is_cleared = str(floor_num) in cleared_by and player_id in cleared_by[str(floor_num)]
            
            status = "✅ Cleared" if is_cleared else "⚠️ Dangerous"
            
            display += f"**Floor {floor_num}:** {status}\n"
            display += f"  Difficulty: {difficulty} | Zombies: {zombies}\n"
        
        display += "\nUse `/floor <number> <action>` to enter a floor.\n"
        display += "Actions: `sneak`, `attack`, `search`"
        
        return display
    
    def enter_floor(self, player_id: str, building_id: str, 
                   floor_number: int, action: str) -> Dict[str, Any]:
        """Enter a specific floor with an action"""
        from systems.player_system import player_system
        from core.world_manager import world_manager
        from core.scheduler import scheduler
        
        player = player_system.get_player(player_id)
        if not player:
            return {"success": False, "error": "Player not found"}
        
        # Get floor info
        floor_info = world_manager.get_floor_info(building_id, floor_number)
        if not floor_info:
            return {"success": False, "error": f"Floor {floor_number} not found"}
        
        # Check if floor is already cleared
        if world_manager.is_floor_cleared(building_id, floor_number, player_id):
            return {"success": False, "error": "Floor already cleared"}
        
        # Check if player can act
        if not player_system.can_player_act(player_id, "floor"):
            return {"success": False, "error": "Action on cooldown"}
        
        # Generate floor encounter
        encounter = self._generate_floor_encounter(floor_info, player)
        
        if encounter["zombies"]:
            # Create decision window
            encounter_id = f"encounter_{get_current_timestamp()}_{random.randint(1000, 9999)}"
            
            self.active_encounters[encounter_id] = {
                "player_id": player_id,
                "building_id": building_id,
                "floor_number": floor_number,
                "zombies": encounter["zombies"],
                "action": action,
                "start_time": get_current_timestamp(),
                "expires_at": get_current_timestamp() + DECISION_WINDOW
            }
            
            # Create pending action for timeout
            scheduler.create_pending_action(
                player_id,
                "combat_timeout",
                {"encounter_id": encounter_id, "action": action},
                DECISION_WINDOW
            )
            
            # Create encounter display
            display = self._create_encounter_display(encounter, DECISION_WINDOW)
            
            return {
                "success": True,
                "encounter_id": encounter_id,
                "encounter": encounter,
                "display": display,
                "decision_window": DECISION_WINDOW
            }
        else:
            # No zombies, safe to proceed
            return {
                "success": True,
                "encounter": encounter,
                "display": "The floor appears to be clear of zombies.",
                "safe": True
            }
    
    def _generate_floor_encounter(self, floor_info: Dict[str, Any], 
                                player: Dict[str, Any]) -> Dict[str, Any]:
        """Generate floor encounter with zombies"""
        from systems.zombie_system import zombie_system
        
        difficulty = floor_info.get("difficulty", 0)
        zombie_count = floor_info.get("zombies", 0)
        
        zombies = []
        for _ in range(zombie_count):
            zombie = zombie_system.generate_zombie("urban", difficulty)
            zombies.append(zombie)
        
        return {
            "zombies": zombies,
            "difficulty": difficulty,
            "loot_table": floor_info.get("loot_table", "default")
        }
    
    def _create_encounter_display(self, encounter: Dict[str, Any], 
                                decision_window: int) -> str:
        """Create formatted encounter display"""
        from systems.zombie_system import zombie_system
        
        zombies = encounter.get("zombies", [])
        
        if not zombies:
            return "The area appears to be clear."
        
        display = f"⚠️ **ENCOUNTER!**\n\n"
        display += f"You have {decision_window} seconds to decide!\n\n"
        
        if len(zombies) == 1:
            display += zombie_system.get_zombie_display(zombies[0])
        else:
            display += f"You encounter {len(zombies)} zombies!\n\n"
            for i, zombie in enumerate(zombies, 1):
                display += f"**Zombie {i}:**\n"
                display += zombie_system.get_zombie_display(zombie) + "\n"
        
        display += "\n**Choose your action:**\n"
        display += "`/sneak` - Attempt to sneak past\n"
        display += "`/attack` - Attack the zombies\n"
        
        return display.strip()
    
    def handle_floor_action(self, player_id: str, action: str, 
                          encounter_id: str = None) -> Dict[str, Any]:
        """Handle floor action (sneak, attack)"""
        from systems.combat_system import combat_system
        from systems.player_system import player_system
        
        # Find active encounter
        encounter = None
        if encounter_id:
            encounter = self.active_encounters.get(encounter_id)
        
        if not encounter:
            # Try to find encounter by player
            for enc in self.active_encounters.values():
                if enc["player_id"] == player_id:
                    encounter = enc
                    encounter_id = enc.get("id", "unknown")
                    break
        
        if not encounter:
            return {"success": False, "error": "No active encounter found"}
        
        # Check if encounter is still valid
        current_time = get_current_timestamp()
        if current_time > encounter["expires_at"]:
            del self.active_encounters[encounter_id]
            return {"success": False, "error": "Encounter expired"}
        
        # Process action
        if action == "sneak":
            return self._handle_sneak_action(player_id, encounter)
        elif action == "attack":
            return self._handle_attack_action(player_id, encounter)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def _handle_sneak_action(self, player_id: str, encounter: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sneak action"""
        from systems.player_system import player_system
        from systems.zombie_system import zombie_system
        from utils.helpers import calculate_stealth_success, is_night_time
        
        player = player_system.get_player(player_id)
        if not player:
            return {"success": False, "error": "Player not found"}
        
        zombies = encounter.get("zombies", [])
        if not zombies:
            return {"success": True, "result": "safe", "message": "No zombies to sneak past"}
        
        # Calculate sneak success
        player_stealth = player.get("intelligence", 0) // 2
        is_night = is_night_time()
        
        # Check against each zombie
        success = True
        for zombie in zombies:
            zombie_alertness = zombie_system.calculate_zombie_alertness(
                zombie, player_stealth, is_night
            )
            
            if not calculate_stealth_success(player_stealth, zombie_alertness, is_night):
                success = False
                break
        
        if success:
            # Sneak successful
            self._clear_encounter(encounter)
            return {
                "success": True,
                "result": "sneak_success",
                "message": "You successfully sneak past the zombies!"
            }
        else:
            # Sneak failed, start combat
            return self._start_floor_combat(player_id, encounter)
    
    def _handle_attack_action(self, player_id: str, encounter: Dict[str, Any]) -> Dict[str, Any]:
        """Handle attack action"""
        return self._start_floor_combat(player_id, encounter)
    
    def _start_floor_combat(self, player_id: str, encounter: Dict[str, Any]) -> Dict[str, Any]:
        """Start combat with floor zombies"""
        from systems.combat_system import combat_system
        
        zombies = encounter.get("zombies", [])
        if not zombies:
            return {"success": True, "result": "safe", "message": "No zombies to fight"}
        
        # Start combat with first zombie
        zombie = zombies[0]
        combat = combat_system.initiate_combat(player_id, zombie["id"], "pvz")
        
        # Process attack
        attack_data = {
            "weapon_damage": 25,  # Base weapon damage
            "zombie": zombie
        }
        
        result = combat_system.process_combat_turn(combat["id"], "attack", attack_data)
        
        if result.get("combat_ended") and result.get("winner") == player_id:
            # Player won, clear the encounter
            self._clear_encounter(encounter)
            return {
                "success": True,
                "result": "combat_victory",
                "message": "You defeated the zombies!",
                "loot": result.get("loot", [])
            }
        else:
            return {
                "success": True,
                "result": "combat_ongoing",
                "message": "Combat continues...",
                "combat_id": combat["id"]
            }
    
    def _clear_encounter(self, encounter: Dict[str, Any]):
        """Clear an encounter"""
        encounter_id = encounter.get("id")
        if encounter_id and encounter_id in self.active_encounters:
            del self.active_encounters[encounter_id]
    
    def get_active_encounters(self, player_id: str) -> List[Dict[str, Any]]:
        """Get active encounters for a player"""
        return [enc for enc in self.active_encounters.values() 
                if enc["player_id"] == player_id]

# Global building system instance
building_system = BuildingSystem()