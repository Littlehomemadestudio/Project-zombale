"""
Combat system for BalletBot: Outbreak Dominion
Handles player vs player and player vs zombie combat
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp, calculate_damage, add_action_to_history
from config import COMBAT_CRITICAL_HIT_CHANCE, COMBAT_ALERTED_BONUS, COMBAT_AMBUSH_BONUS

logger = logging.getLogger(__name__)

class CombatSystem:
    """Manages combat encounters"""
    
    def __init__(self):
        self.active_combats: Dict[str, Dict] = {}  # combat_id -> combat_data
        self.combat_counter = 0
    
    def initiate_combat(self, attacker_id: str, target_id: str, combat_type: str, 
                       weapon_data: Dict = None) -> Dict[str, Any]:
        """Initiate a combat encounter"""
        try:
            self.combat_counter += 1
            combat_id = f"combat_{self.combat_counter}_{get_current_timestamp()}"
            
            # Get combatants
            attacker = file_manager.get_player(attacker_id)
            target = file_manager.get_player(target_id)
            
            if not attacker or not target:
                return {"success": False, "error": "Combatant not found"}
            
            # Create combat data
            combat_data = {
                "id": combat_id,
                "type": combat_type,  # "pvp" or "pvz"
                "attacker_id": attacker_id,
                "target_id": target_id,
                "attacker_hp": attacker.get("hp", 100),
                "target_hp": target.get("hp", 100),
                "attacker_weapon": weapon_data,
                "target_weapon": None,
                "turn": "attacker",
                "round": 1,
                "status": "active",
                "created_at": get_current_timestamp(),
                "actions": []
            }
            
            # Set target weapon for PvP
            if combat_type == "pvp":
                target_weapons = self._get_player_weapons(target_id)
                if target_weapons:
                    combat_data["target_weapon"] = target_weapons[0]
            
            self.active_combats[combat_id] = combat_data
            
            # Add to action history
            add_action_to_history(attacker_id, "combat_started", combat_id=combat_id, target_id=target_id)
            if combat_type == "pvp":
                add_action_to_history(target_id, "combat_started", combat_id=combat_id, attacker_id=attacker_id)
            
            logger.info(f"Combat {combat_id} initiated: {attacker_id} vs {target_id}")
            
            return {
                "success": True,
                "combat_id": combat_id,
                "combat_data": combat_data
            }
            
        except Exception as e:
            logger.error(f"Error initiating combat: {e}")
            return {"success": False, "error": "Failed to initiate combat"}
    
    def process_combat_turn(self, combat_id: str, action: str, action_data: Dict = None) -> Dict[str, Any]:
        """Process a combat turn"""
        try:
            if combat_id not in self.active_combats:
                return {"success": False, "error": "Combat not found"}
            
            combat = self.active_combats[combat_id]
            if combat["status"] != "active":
                return {"success": False, "error": "Combat not active"}
            
            # Process action
            if action == "attack":
                result = self._process_attack(combat, action_data)
            elif action == "sneak":
                result = self._process_sneak(combat, action_data)
            elif action == "flee":
                result = self._process_flee(combat, action_data)
            else:
                return {"success": False, "error": "Invalid action"}
            
            # Check for combat end
            if combat["attacker_hp"] <= 0 or combat["target_hp"] <= 0:
                result["combat_ended"] = True
                result["winner"] = self._determine_winner(combat)
                self._end_combat(combat_id, result["winner"])
            else:
                # Switch turns
                combat["turn"] = "target" if combat["turn"] == "attacker" else "attacker"
                if combat["turn"] == "attacker":
                    combat["round"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing combat turn: {e}")
            return {"success": False, "error": "Failed to process combat turn"}
    
    def _process_attack(self, combat: Dict, action_data: Dict) -> Dict[str, Any]:
        """Process attack action"""
        try:
            attacker_id = combat["attacker_id"]
            target_id = combat["target_id"]
            
            # Get attacker data
            attacker = file_manager.get_player(attacker_id)
            if not attacker:
                return {"success": False, "error": "Attacker not found"}
            
            # Calculate damage
            weapon_damage = 10  # Default melee damage
            class_bonus = 0.0
            
            if combat["turn"] == "attacker" and combat["attacker_weapon"]:
                weapon_damage = combat["attacker_weapon"].get("damage", 10)
            elif combat["turn"] == "target" and combat["target_weapon"]:
                weapon_damage = combat["target_weapon"].get("damage", 10)
            
            # Apply class bonus
            char_class = attacker.get("class", "")
            if char_class == "Soldier":
                class_bonus = 0.10  # +10% weapon damage
            
            # Check for critical hit
            critical_hit = self._roll_critical_hit()
            
            # Check for alerted bonus
            alerted_bonus = action_data.get("alerted", False)
            
            # Calculate final damage
            damage = calculate_damage(
                weapon_damage, 
                class_bonus, 
                critical_hit, 
                alerted_bonus
            )
            
            # Apply damage
            if combat["turn"] == "attacker":
                combat["target_hp"] = max(0, combat["target_hp"] - damage)
            else:
                combat["attacker_hp"] = max(0, combat["attacker_hp"] - damage)
            
            # Record action
            action_record = {
                "action": "attack",
                "attacker": attacker_id,
                "target": target_id,
                "damage": damage,
                "critical": critical_hit,
                "timestamp": get_current_timestamp()
            }
            combat["actions"].append(action_record)
            
            # Add to action history
            add_action_to_history(attacker_id, "attack", damage=damage, target=target_id, critical=critical_hit)
            
            return {
                "success": True,
                "action": "attack",
                "damage": damage,
                "critical": critical_hit,
                "attacker_hp": combat["attacker_hp"],
                "target_hp": combat["target_hp"]
            }
            
        except Exception as e:
            logger.error(f"Error processing attack: {e}")
            return {"success": False, "error": "Failed to process attack"}
    
    def _process_sneak(self, combat: Dict, action_data: Dict) -> Dict[str, Any]:
        """Process sneak action"""
        try:
            attacker_id = combat["attacker_id"]
            target_id = combat["target_id"]
            
            # Get attacker data
            attacker = file_manager.get_player(attacker_id)
            if not attacker:
                return {"success": False, "error": "Attacker not found"}
            
            # Calculate sneak success
            from utils.helpers import calculate_stealth, is_night_time
            from systems.zombie_system import zombie_system
            
            if combat["type"] == "pvz":
                # Zombie combat - use zombie alertness
                zombie_alertness = action_data.get("zombie_alertness", 50)
                sneak_chance = calculate_stealth(attacker, zombie_alertness, is_night_time())
            else:
                # PvP combat - use target's awareness
                target = file_manager.get_player(target_id)
                target_awareness = target.get("intelligence", 0) if target else 50
                sneak_chance = calculate_stealth(attacker, target_awareness, is_night_time())
            
            # Roll for success
            success = random.randint(1, 100) <= sneak_chance
            
            # Record action
            action_record = {
                "action": "sneak",
                "attacker": attacker_id,
                "target": target_id,
                "success": success,
                "sneak_chance": sneak_chance,
                "timestamp": get_current_timestamp()
            }
            combat["actions"].append(action_record)
            
            # Add to action history
            add_action_to_history(attacker_id, "sneak", success=success, target=target_id)
            
            if success:
                # Sneak successful - end combat
                self._end_combat(combat["id"], attacker_id)
                return {
                    "success": True,
                    "action": "sneak",
                    "sneak_success": True,
                    "combat_ended": True,
                    "winner": attacker_id
                }
            else:
                # Sneak failed - continue combat
                return {
                    "success": True,
                    "action": "sneak",
                    "sneak_success": False,
                    "message": "Sneak failed! Combat continues."
                }
            
        except Exception as e:
            logger.error(f"Error processing sneak: {e}")
            return {"success": False, "error": "Failed to process sneak"}
    
    def _process_flee(self, combat: Dict, action_data: Dict) -> Dict[str, Any]:
        """Process flee action"""
        try:
            attacker_id = combat["attacker_id"]
            target_id = combat["target_id"]
            
            # Calculate flee success (based on stamina and class)
            attacker = file_manager.get_player(attacker_id)
            if not attacker:
                return {"success": False, "error": "Attacker not found"}
            
            stamina = attacker.get("stamina", 100)
            flee_chance = min(80, stamina + 20)  # Higher stamina = better flee chance
            
            # Apply class bonus
            char_class = attacker.get("class", "")
            if char_class == "Scavenger":
                flee_chance += 10  # Scavengers are better at fleeing
            
            # Roll for success
            success = random.randint(1, 100) <= flee_chance
            
            # Record action
            action_record = {
                "action": "flee",
                "attacker": attacker_id,
                "target": target_id,
                "success": success,
                "flee_chance": flee_chance,
                "timestamp": get_current_timestamp()
            }
            combat["actions"].append(action_record)
            
            # Add to action history
            add_action_to_history(attacker_id, "flee", success=success, target=target_id)
            
            if success:
                # Flee successful - end combat
                self._end_combat(combat["id"], target_id)  # Target wins by default
                return {
                    "success": True,
                    "action": "flee",
                    "flee_success": True,
                    "combat_ended": True,
                    "winner": target_id
                }
            else:
                # Flee failed - continue combat
                return {
                    "success": True,
                    "action": "flee",
                    "flee_success": False,
                    "message": "Flee failed! Combat continues."
                }
            
        except Exception as e:
            logger.error(f"Error processing flee: {e}")
            return {"success": False, "error": "Failed to process flee"}
    
    def _roll_critical_hit(self) -> bool:
        """Roll for critical hit"""
        return random.randint(1, 100) <= COMBAT_CRITICAL_HIT_CHANCE
    
    def _determine_winner(self, combat: Dict) -> str:
        """Determine combat winner"""
        if combat["attacker_hp"] <= 0:
            return combat["target_id"]
        elif combat["target_hp"] <= 0:
            return combat["attacker_id"]
        else:
            return None
    
    def _end_combat(self, combat_id: str, winner_id: str):
        """End combat and update player stats"""
        try:
            if combat_id not in self.active_combats:
                return
            
            combat = self.active_combats[combat_id]
            combat["status"] = "ended"
            combat["winner"] = winner_id
            combat["ended_at"] = get_current_timestamp()
            
            # Update player HP
            from systems.player_system import player_system
            
            attacker_id = combat["attacker_id"]
            target_id = combat["target_id"]
            
            # Update HP
            player_system.update_hp(attacker_id, combat["attacker_hp"] - 100)
            player_system.update_hp(target_id, combat["target_hp"] - 100)
            
            # Handle death
            if combat["attacker_hp"] <= 0:
                self._handle_player_death(attacker_id, target_id)
            if combat["target_hp"] <= 0:
                self._handle_player_death(target_id, attacker_id)
            
            # Add to action history
            add_action_to_history(winner_id, "combat_won", combat_id=combat_id)
            
            logger.info(f"Combat {combat_id} ended. Winner: {winner_id}")
            
        except Exception as e:
            logger.error(f"Error ending combat {combat_id}: {e}")
    
    def _handle_player_death(self, dead_player_id: str, killer_id: str):
        """Handle player death"""
        try:
            from systems.player_system import player_system
            
            # Update player status
            player_system.update_player(dead_player_id, {"status": "dead"})
            
            # Add to action history
            add_action_to_history(dead_player_id, "died", killer=killer_id)
            add_action_to_history(killer_id, "killed_player", victim=dead_player_id)
            
            # TODO: Handle zombie conversion, loot drops, etc.
            
            logger.info(f"Player {dead_player_id} died (killed by {killer_id})")
            
        except Exception as e:
            logger.error(f"Error handling player death: {e}")
    
    def _get_player_weapons(self, player_id: str) -> List[Dict]:
        """Get player's weapons"""
        from systems.inventory_system import inventory_system
        
        weapons = inventory_system.get_weapons(player_id)
        weapon_list = []
        
        for item_id, quantity in weapons.items():
            item_def = inventory_system.get_item_definition(item_id)
            if item_def and quantity > 0:
                weapon_list.append({
                    "id": item_id,
                    "name": item_def.get("name", item_id),
                    "damage": item_def.get("properties", {}).get("damage", 10),
                    "quantity": quantity
                })
        
        return weapon_list
    
    def get_combat(self, combat_id: str) -> Optional[Dict]:
        """Get combat data"""
        return self.active_combats.get(combat_id)
    
    def get_active_combats(self, player_id: str = None) -> List[Dict]:
        """Get active combats"""
        if player_id:
            return [combat for combat in self.active_combats.values() 
                   if combat["status"] == "active" and 
                   (combat["attacker_id"] == player_id or combat["target_id"] == player_id)]
        else:
            return [combat for combat in self.active_combats.values() 
                   if combat["status"] == "active"]
    
    def format_combat_status(self, combat: Dict) -> str:
        """Format combat status for display"""
        status = f"⚔️ **Combat Status**\n"
        status += f"Round: {combat['round']}\n"
        status += f"Turn: {combat['turn']}\n"
        status += f"Attacker HP: {combat['attacker_hp']}/100\n"
        status += f"Target HP: {combat['target_hp']}/100\n"
        
        if combat["status"] == "ended":
            status += f"Winner: {combat.get('winner', 'Unknown')}\n"
        
        return status

# Global combat system instance
combat_system = CombatSystem()