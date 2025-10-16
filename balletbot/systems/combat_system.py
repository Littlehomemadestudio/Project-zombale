"""
Combat system for BalletBot: Outbreak Dominion
Handles player vs player and player vs zombie combat
"""

import random
import logging
from typing import Dict, List, Optional, Any, Tuple

from utils.helpers import get_current_timestamp, roll_percentage, calculate_combat_damage
from utils.db import log_event
from config import COMBAT_CRITICAL_HIT_CHANCE, COMBAT_ALERTED_BONUS, COMBAT_AMBUSH_BONUS

logger = logging.getLogger(__name__)

class CombatSystem:
    """Manages combat between players and zombies"""
    
    def __init__(self):
        self.active_combats: Dict[str, Dict] = {}
        self.pending_actions: Dict[str, Dict] = {}
    
    def initiate_combat(self, attacker_id: str, target_id: str, 
                       combat_type: str = "pvp") -> Dict[str, Any]:
        """Initiate combat between two entities"""
        combat_id = f"combat_{get_current_timestamp()}_{random.randint(1000, 9999)}"
        
        combat_data = {
            "id": combat_id,
            "attacker_id": attacker_id,
            "target_id": target_id,
            "type": combat_type,
            "start_time": get_current_timestamp(),
            "round": 1,
            "status": "active",
            "actions": []
        }
        
        self.active_combats[combat_id] = combat_data
        
        log_event("combat_initiated", {
            "combat_id": combat_id,
            "attacker_id": attacker_id,
            "target_id": target_id,
            "type": combat_type
        })
        
        return combat_data
    
    def process_combat_turn(self, combat_id: str, action: str, 
                          action_data: Dict = None) -> Dict[str, Any]:
        """Process a combat turn"""
        if combat_id not in self.active_combats:
            return {"success": False, "error": "Combat not found"}
        
        combat = self.active_combats[combat_id]
        action_data = action_data or {}
        
        result = {
            "success": True,
            "combat_id": combat_id,
            "action": action,
            "round": combat["round"],
            "damage_dealt": 0,
            "target_hp": 0,
            "combat_ended": False,
            "winner": None
        }
        
        if action == "attack":
            result.update(self._process_attack(combat, action_data))
        elif action == "sneak":
            result.update(self._process_sneak(combat, action_data))
        elif action == "flee":
            result.update(self._process_flee(combat, action_data))
        
        # Add action to combat history
        combat["actions"].append({
            "round": combat["round"],
            "action": action,
            "data": action_data,
            "result": result,
            "timestamp": get_current_timestamp()
        })
        
        # Check if combat should end
        if result.get("combat_ended"):
            self._end_combat(combat_id, result.get("winner"))
        
        # Advance round
        combat["round"] += 1
        
        return result
    
    def _process_attack(self, combat: Dict[str, Any], action_data: Dict) -> Dict[str, Any]:
        """Process an attack action"""
        from systems.player_system import player_system
        from systems.zombie_system import zombie_system
        
        attacker_id = combat["attacker_id"]
        target_id = combat["target_id"]
        combat_type = combat["type"]
        
        # Get attacker stats
        attacker = player_system.get_player(attacker_id)
        if not attacker:
            return {"success": False, "error": "Attacker not found"}
        
        # Calculate damage
        weapon_damage = action_data.get("weapon_damage", 20)
        class_bonus = player_system.get_player_class_bonus(attacker_id, "weapon_damage")
        is_critical = roll_percentage() <= COMBAT_CRITICAL_HIT_CHANCE
        
        damage = calculate_combat_damage(weapon_damage, class_bonus, is_critical)
        
        result = {
            "damage_dealt": damage,
            "is_critical": is_critical,
            "combat_ended": False,
            "winner": None
        }
        
        if combat_type == "pvp":
            # Player vs Player combat
            target = player_system.get_player(target_id)
            if not target:
                return {"success": False, "error": "Target not found"}
            
            # Apply damage
            new_hp = max(0, target.get("hp", 100) - damage)
            player_system.update_player(target_id, {"hp": new_hp})
            
            result["target_hp"] = new_hp
            
            if new_hp <= 0:
                result["combat_ended"] = True
                result["winner"] = attacker_id
                # Handle player death
                self._handle_player_death(target_id, attacker_id)
        
        elif combat_type == "pvz":
            # Player vs Zombie combat
            zombie = action_data.get("zombie")
            if not zombie:
                return {"success": False, "error": "Zombie data not found"}
            
            # Process zombie damage
            zombie_result = zombie_system.process_zombie_combat(zombie, damage)
            result.update(zombie_result)
            
            if zombie_result["zombie_died"]:
                result["combat_ended"] = True
                result["winner"] = attacker_id
                # Give loot
                loot = zombie_system.get_zombie_loot(zombie)
                self._give_combat_loot(attacker_id, loot)
        
        return result
    
    def _process_sneak(self, combat: Dict[str, Any], action_data: Dict) -> Dict[str, Any]:
        """Process a sneak action"""
        from systems.player_system import player_system
        from systems.zombie_system import zombie_system
        
        attacker_id = combat["attacker_id"]
        combat_type = combat["type"]
        
        # Get attacker stats
        attacker = player_system.get_player(attacker_id)
        if not attacker:
            return {"success": False, "error": "Attacker not found"}
        
        player_stealth = attacker.get("intelligence", 0) // 2  # Basic stealth calculation
        is_night = action_data.get("is_night", False)
        
        result = {
            "sneak_success": False,
            "combat_ended": False,
            "winner": None
        }
        
        if combat_type == "pvz":
            # Sneak past zombie
            zombie = action_data.get("zombie")
            if not zombie:
                return {"success": False, "error": "Zombie data not found"}
            
            zombie_alertness = zombie_system.calculate_zombie_alertness(
                zombie, player_stealth, is_night
            )
            
            # Calculate sneak success
            from utils.helpers import calculate_stealth_success
            success = calculate_stealth_success(player_stealth, zombie_alertness, is_night)
            
            result["sneak_success"] = success
            
            if success:
                result["combat_ended"] = True
                result["winner"] = attacker_id
                # Sneak success - no combat
            else:
                # Sneak failed - start combat with penalty
                result["combat_ended"] = False
                result["sneak_failed"] = True
        
        return result
    
    def _process_flee(self, combat: Dict[str, Any], action_data: Dict) -> Dict[str, Any]:
        """Process a flee action"""
        # Fleeing always ends combat
        return {
            "flee_success": True,
            "combat_ended": True,
            "winner": None  # No winner when fleeing
        }
    
    def _handle_player_death(self, player_id: str, killer_id: str):
        """Handle player death"""
        from systems.player_system import player_system
        
        # Set player status to dead
        player_system.set_player_status(player_id, "dead")
        
        # Log death event
        log_event("player_died", {
            "player_id": player_id,
            "killer_id": killer_id,
            "timestamp": get_current_timestamp()
        })
        
        # TODO: Handle inventory drop, respawn mechanics, etc.
    
    def _give_combat_loot(self, player_id: str, loot: List[Tuple[str, int]]):
        """Give loot to player after combat"""
        from systems.inventory_system import inventory_system
        
        for item_id, quantity in loot:
            inventory_system.add_item(player_id, item_id, quantity)
    
    def _end_combat(self, combat_id: str, winner: Optional[str]):
        """End combat and clean up"""
        if combat_id in self.active_combats:
            combat = self.active_combats[combat_id]
            combat["status"] = "ended"
            combat["winner"] = winner
            combat["end_time"] = get_current_timestamp()
            
            log_event("combat_ended", {
                "combat_id": combat_id,
                "winner": winner,
                "duration": combat["end_time"] - combat["start_time"]
            })
            
            # Remove from active combats after a delay
            # (keep for a while for logging purposes)
            del self.active_combats[combat_id]
    
    def get_combat_status(self, combat_id: str) -> Optional[Dict[str, Any]]:
        """Get current combat status"""
        return self.active_combats.get(combat_id)
    
    def get_player_combats(self, player_id: str) -> List[Dict[str, Any]]:
        """Get all active combats involving a player"""
        player_combats = []
        
        for combat in self.active_combats.values():
            if combat["attacker_id"] == player_id or combat["target_id"] == player_id:
                player_combats.append(combat)
        
        return player_combats
    
    def handle_combat_timeout(self, player_id: str, action_data: Dict):
        """Handle combat action timeout"""
        combat_id = action_data.get("combat_id")
        if not combat_id or combat_id not in self.active_combats:
            return
        
        # Default to sneak attempt (which will likely fail)
        self.process_combat_turn(combat_id, "sneak", action_data)
    
    def handle_ambush_trigger(self, player_id: str, action_data: Dict):
        """Handle ambush trigger"""
        target_id = action_data.get("target_id")
        if not target_id:
            return
        
        # Initiate ambush combat with bonus
        combat = self.initiate_combat(player_id, target_id, "pvp")
        
        # Process ambush attack with bonus
        ambush_data = {
            "weapon_damage": action_data.get("weapon_damage", 20),
            "ambush_bonus": COMBAT_AMBUSH_BONUS
        }
        
        self.process_combat_turn(combat["id"], "attack", ambush_data)
    
    def create_combat_display(self, combat: Dict[str, Any]) -> str:
        """Create formatted combat display"""
        from systems.player_system import player_system
        
        attacker = player_system.get_player(combat["attacker_id"])
        target = player_system.get_player(combat["target_id"])
        
        if not attacker or not target:
            return "Combat data unavailable"
        
        display = f"""
⚔️ **Combat in Progress**
Round: {combat['round']}

**Attacker:** {attacker['username']} (HP: {attacker['hp']})
**Target:** {target['username']} (HP: {target['hp']})

Choose your action:
/sneak - Attempt to sneak past
/attack - Attack the target
/flee - Attempt to flee
        """.strip()
        
        return display

# Global combat system instance
combat_system = CombatSystem()