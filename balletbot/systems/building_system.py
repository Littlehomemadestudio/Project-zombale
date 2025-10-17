"""
Building system for BalletBot: Outbreak Dominion
Handles building entry, floor encounters, and decision windows
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp, add_action_to_history
from config import DECISION_WINDOW, BUILDING_FLOORS

logger = logging.getLogger(__name__)

class BuildingSystem:
    """Manages building encounters and floor clearing"""
    
    def __init__(self):
        self.active_encounters: Dict[str, Dict] = {}  # encounter_id -> encounter_data
        self.encounter_counter = 0
    
    def enter_building(self, player_id: str, building_name: str) -> Dict[str, Any]:
        """Enter a building"""
        try:
            player_data = file_manager.get_player(player_id)
            if not player_data:
                return {"success": False, "error": "Player not found"}
            
            # Check if building exists
            building_id = self._get_building_id(player_data.get("location", ""), building_name)
            if not building_id:
                return {"success": False, "error": f"Building {building_name} not found in this area"}
            
            # Get building data
            building_data = file_manager.get_building(building_id)
            if not building_data:
                # Create building if it doesn't exist
                building_data = self._create_building(building_id, building_name, player_data.get("location", ""))
                file_manager.save_building(building_id, building_data)
            
            # Get available floors
            floors = building_data.get("floors", [])
            if not floors:
                return {"success": False, "error": "No floors available in this building"}
            
            # Format floor information
            floor_info = self._format_floor_info(floors, building_data.get("cleared_by", {}))
            
            # Add to action history
            add_action_to_history(player_id, "entered_building", building_name=building_name)
            
            return {
                "success": True,
                "building_name": building_name,
                "floors": floors,
                "floor_info": floor_info,
                "message": f"🏢 **{building_name}**\n\n{floor_info}"
            }
            
        except Exception as e:
            logger.error(f"Error entering building: {e}")
            return {"success": False, "error": "Failed to enter building"}
    
    def enter_floor(self, player_id: str, floor_number: int, action: str) -> Dict[str, Any]:
        """Enter a building floor"""
        try:
            player_data = file_manager.get_player(player_id)
            if not player_data:
                return {"success": False, "error": "Player not found"}
            
            # Get building data
            building_id = self._get_building_id(player_data.get("location", ""), "Unknown")
            if not building_id:
                return {"success": False, "error": "Building not found"}
            
            building_data = file_manager.get_building(building_id)
            if not building_data:
                return {"success": False, "error": "Building data not found"}
            
            # Find floor
            floors = building_data.get("floors", [])
            floor_data = None
            for floor in floors:
                if floor.get("floor") == floor_number:
                    floor_data = floor
                    break
            
            if not floor_data:
                return {"success": False, "error": f"Floor {floor_number} not found"}
            
            # Check if floor is already cleared
            cleared_by = building_data.get("cleared_by", {})
            if str(floor_number) in cleared_by:
                return {"success": False, "error": f"Floor {floor_number} has already been cleared"}
            
            # Create encounter
            encounter = self._create_encounter(player_id, building_id, floor_data, action)
            if not encounter:
                return {"success": False, "error": "Failed to create encounter"}
            
            # Add to action history
            add_action_to_history(player_id, "entered_floor", floor=floor_number, action=action)
            
            return {
                "success": True,
                "encounter_id": encounter["id"],
                "floor": floor_number,
                "action": action,
                "message": self._format_encounter_message(encounter)
            }
            
        except Exception as e:
            logger.error(f"Error entering floor: {e}")
            return {"success": False, "error": "Failed to enter floor"}
    
    def _create_encounter(self, player_id: str, building_id: str, floor_data: Dict, action: str) -> Optional[Dict]:
        """Create a floor encounter"""
        try:
            self.encounter_counter += 1
            encounter_id = f"encounter_{self.encounter_counter}_{get_current_timestamp()}"
            
            # Generate zombies for encounter
            zombie_count = floor_data.get("zombies", 1)
            zombies = []
            
            for _ in range(zombie_count):
                from systems.zombie_system import zombie_system
                zombie = zombie_system.generate_zombie("urban")  # Default to urban
                if zombie:
                    zombies.append(zombie)
            
            # Create encounter data
            encounter = {
                "id": encounter_id,
                "player_id": player_id,
                "building_id": building_id,
                "floor": floor_data.get("floor", 1),
                "action": action,
                "zombies": zombies,
                "status": "active",
                "created_at": get_current_timestamp(),
                "expires_at": get_current_timestamp() + DECISION_WINDOW,
                "decision_made": False
            }
            
            self.active_encounters[encounter_id] = encounter
            
            # Add pending action for timeout
            self._add_pending_action(encounter_id, player_id, action)
            
            return encounter
            
        except Exception as e:
            logger.error(f"Error creating encounter: {e}")
            return None
    
    def _add_pending_action(self, encounter_id: str, player_id: str, action: str):
        """Add pending action for encounter timeout"""
        try:
            pending_action = {
                "id": f"pending_{encounter_id}",
                "player_id": player_id,
                "action_type": "encounter_timeout",
                "payload": {
                    "encounter_id": encounter_id,
                    "default_action": "sneak"
                },
                "expire_at": get_current_timestamp() + DECISION_WINDOW,
                "created_at": get_current_timestamp()
            }
            
            file_manager.add_pending_action(pending_action)
            
        except Exception as e:
            logger.error(f"Error adding pending action: {e}")
    
    def process_encounter_action(self, player_id: str, action: str, encounter_id: str = None) -> Dict[str, Any]:
        """Process encounter action (sneak/attack)"""
        try:
            # Find encounter
            if not encounter_id:
                encounter = self._find_player_encounter(player_id)
            else:
                encounter = self.active_encounters.get(encounter_id)
            
            if not encounter:
                return {"success": False, "error": "No active encounter found"}
            
            if encounter["player_id"] != player_id:
                return {"success": False, "error": "Not your encounter"}
            
            if encounter["status"] != "active":
                return {"success": False, "error": "Encounter not active"}
            
            # Check if decision window expired
            if get_current_timestamp() > encounter["expires_at"]:
                return {"success": False, "error": "Decision window expired"}
            
            # Process action
            if action == "sneak":
                result = self._process_sneak_action(encounter)
            elif action == "attack":
                result = self._process_attack_action(encounter)
            else:
                return {"success": False, "error": "Invalid action. Use /sneak or /attack"}
            
            # Mark decision as made
            encounter["decision_made"] = True
            encounter["status"] = "resolved"
            
            # Remove from active encounters
            if encounter_id in self.active_encounters:
                del self.active_encounters[encounter_id]
            
            # Remove pending action
            file_manager.remove_pending_action(f"pending_{encounter_id}")
            
            # Add to action history
            add_action_to_history(player_id, "encounter_action", action=action, result=result.get("success", False))
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing encounter action: {e}")
            return {"success": False, "error": "Failed to process encounter action"}
    
    def _process_sneak_action(self, encounter: Dict) -> Dict[str, Any]:
        """Process sneak action"""
        try:
            player_id = encounter["player_id"]
            player_data = file_manager.get_player(player_id)
            if not player_data:
                return {"success": False, "error": "Player not found"}
            
            # Calculate sneak success
            from utils.helpers import calculate_stealth, is_night_time
            from systems.zombie_system import zombie_system
            
            # Use first zombie's alertness
            zombies = encounter.get("zombies", [])
            if not zombies:
                return {"success": False, "error": "No zombies in encounter"}
            
            zombie_alertness = zombies[0].get("alertness", 50)
            sneak_chance = calculate_stealth(player_data, zombie_alertness, is_night_time())
            
            # Roll for success
            success = random.randint(1, 100) <= sneak_chance
            
            if success:
                # Sneak successful - get limited loot
                loot = self._get_floor_loot(encounter, limited=True)
                if loot:
                    from systems.inventory_system import inventory_system
                    for item_id, quantity in loot:
                        inventory_system.add_item(player_id, item_id, quantity)
                
                return {
                    "success": True,
                    "action": "sneak",
                    "sneak_success": True,
                    "loot": loot,
                    "message": f"✅ Sneak successful! You avoided combat and found some loot."
                }
            else:
                # Sneak failed - start combat
                return self._process_attack_action(encounter, sneak_failed=True)
            
        except Exception as e:
            logger.error(f"Error processing sneak action: {e}")
            return {"success": False, "error": "Failed to process sneak action"}
    
    def _process_attack_action(self, encounter: Dict, sneak_failed: bool = False) -> Dict[str, Any]:
        """Process attack action"""
        try:
            player_id = encounter["player_id"]
            player_data = file_manager.get_player(player_id)
            if not player_data:
                return {"success": False, "error": "Player not found"}
            
            zombies = encounter.get("zombies", [])
            if not zombies:
                return {"success": False, "error": "No zombies in encounter"}
            
            # Start combat with zombies
            from systems.combat_system import combat_system
            
            combat_results = []
            total_damage_dealt = 0
            total_damage_taken = 0
            
            for zombie in zombies:
                # Calculate damage dealt to zombie
                weapon_damage = 15  # Default melee damage
                zombie_damage = random.randint(weapon_damage - 5, weapon_damage + 10)
                total_damage_dealt += zombie_damage
                
                # Calculate damage taken from zombie
                zombie_damage_to_player = zombie.get("damage", 15) + random.randint(-3, 7)
                total_damage_taken += zombie_damage_to_player
                
                combat_results.append({
                    "zombie": zombie["name"],
                    "damage_dealt": zombie_damage,
                    "damage_taken": zombie_damage_to_player
                })
            
            # Apply damage to player
            from systems.player_system import player_system
            player_system.update_hp(player_id, -total_damage_taken)
            
            # Get floor loot
            loot = self._get_floor_loot(encounter, limited=False)
            if loot:
                from systems.inventory_system import inventory_system
                for item_id, quantity in loot:
                    inventory_system.add_item(player_id, item_id, quantity)
            
            # Mark floor as cleared
            self._mark_floor_cleared(encounter)
            
            # Add to action history
            add_action_to_history(player_id, "floor_cleared", floor=encounter["floor"], damage_taken=total_damage_taken)
            
            return {
                "success": True,
                "action": "attack",
                "combat_results": combat_results,
                "damage_taken": total_damage_taken,
                "loot": loot,
                "floor_cleared": True,
                "message": f"⚔️ Combat resolved! You took {total_damage_taken} damage and cleared the floor."
            }
            
        except Exception as e:
            logger.error(f"Error processing attack action: {e}")
            return {"success": False, "error": "Failed to process attack action"}
    
    def _get_floor_loot(self, encounter: Dict, limited: bool = False) -> List[Tuple[str, int]]:
        """Get loot from floor clearing"""
        try:
            floor = encounter.get("floor", 1)
            difficulty = encounter.get("zombies", [{}])[0].get("difficulty", 30)
            
            # Get loot table
            loot_table = f"floor_{floor}"
            
            # Calculate loot amount
            base_loot = 2 if limited else 5
            loot_amount = base_loot + (difficulty // 20)
            
            # Generate loot
            loot_items = []
            for _ in range(loot_amount):
                from utils.helpers import get_random_loot_item
                loot_item = get_random_loot_item(loot_table)
                if loot_item:
                    item_id, quantity = loot_item
                    loot_items.append((item_id, quantity))
            
            return loot_items
            
        except Exception as e:
            logger.error(f"Error getting floor loot: {e}")
            return []
    
    def _mark_floor_cleared(self, encounter: Dict):
        """Mark floor as cleared"""
        try:
            building_id = encounter["building_id"]
            floor = encounter["floor"]
            player_id = encounter["player_id"]
            
            building_data = file_manager.get_building(building_id)
            if building_data:
                cleared_by = building_data.get("cleared_by", {})
                cleared_by[str(floor)] = player_id
                building_data["cleared_by"] = cleared_by
                file_manager.save_building(building_id, building_data)
            
        except Exception as e:
            logger.error(f"Error marking floor cleared: {e}")
    
    def _get_building_id(self, location: str, building_name: str) -> Optional[str]:
        """Get building ID from location and name"""
        try:
            region = location.split(":")[0] if ":" in location else location
            return f"{region}:{building_name}"
        except:
            return None
    
    def _create_building(self, building_id: str, building_name: str, location: str) -> Dict:
        """Create building data"""
        try:
            region = location.split(":")[0] if ":" in location else location
            
            # Get floor data from config
            floors = BUILDING_FLOORS.get(building_name, [])
            
            return {
                "id": building_id,
                "region": region,
                "name": building_name,
                "floors": floors,
                "cleared_by": {},
                "last_checked": get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Error creating building: {e}")
            return {}
    
    def _format_floor_info(self, floors: List[Dict], cleared_by: Dict) -> str:
        """Format floor information for display"""
        info = "🏢 **Available Floors:**\n\n"
        
        for floor in floors:
            floor_num = floor.get("floor", 1)
            difficulty = floor.get("difficulty", 30)
            zombies = floor.get("zombies", 0)
            
            status = "✅ Cleared" if str(floor_num) in cleared_by else "❌ Not cleared"
            
            info += f"**Floor {floor_num}**\n"
            info += f"  Difficulty: {difficulty}\n"
            info += f"  Zombies: {zombies}\n"
            info += f"  Status: {status}\n\n"
        
        info += "Use `/floor <number> <action>` to enter a floor.\n"
        info += "Actions: `sneak` (stealth) or `attack` (combat)"
        
        return info
    
    def _format_encounter_message(self, encounter: Dict) -> str:
        """Format encounter message"""
        zombies = encounter.get("zombies", [])
        floor = encounter.get("floor", 1)
        
        message = f"🏢 **Floor {floor} Encounter**\n\n"
        message += f"👁️ You see movement...\n"
        message += f"🧟 Zombies detected: {len(zombies)}\n\n"
        
        for i, zombie in enumerate(zombies):
            message += f"**Zombie {i+1}:**\n"
            message += f"  Alertness: {zombie.get('alertness', 0)}%\n"
            message += f"  HP: {zombie.get('hp', 0)}\n\n"
        
        message += f"⏰ You have {DECISION_WINDOW} seconds to decide:\n"
        message += f"• `/sneak` - Try to sneak past\n"
        message += f"• `/attack` - Attack the zombies"
        
        return message
    
    def _find_player_encounter(self, player_id: str) -> Optional[Dict]:
        """Find active encounter for player"""
        for encounter in self.active_encounters.values():
            if encounter["player_id"] == player_id and encounter["status"] == "active":
                return encounter
        return None
    
    def get_active_encounters(self, player_id: str = None) -> List[Dict]:
        """Get active encounters"""
        if player_id:
            return [encounter for encounter in self.active_encounters.values() 
                   if encounter["player_id"] == player_id and encounter["status"] == "active"]
        else:
            return [encounter for encounter in self.active_encounters.values() 
                   if encounter["status"] == "active"]
    
    def cleanup_expired_encounters(self):
        """Clean up expired encounters"""
        try:
            current_time = get_current_timestamp()
            expired_encounters = []
            
            for encounter_id, encounter in self.active_encounters.items():
                if current_time > encounter.get("expires_at", 0):
                    expired_encounters.append(encounter_id)
            
            for encounter_id in expired_encounters:
                encounter = self.active_encounters[encounter_id]
                
                # Process default action (sneak)
                self._process_sneak_action(encounter)
                
                # Remove from active encounters
                del self.active_encounters[encounter_id]
                
                # Remove pending action
                file_manager.remove_pending_action(f"pending_{encounter_id}")
                
                logger.info(f"Cleaned up expired encounter {encounter_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired encounters: {e}")

# Global building system instance
building_system = BuildingSystem()