"""
Offline system for BalletBot: Outbreak Dominion
Handles offline player modes (ambush, scavenge)
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp, add_action_to_history
from config import OFFLINE_SCAVENGE_COOLDOWN

logger = logging.getLogger(__name__)

class OfflineSystem:
    """Manages offline player modes"""
    
    def __init__(self):
        self.ambush_regions: Dict[str, List[str]] = {}  # region -> list of player_ids
        self.scavenge_players: Dict[str, Dict] = {}  # player_id -> scavenge_data
    
    def set_offline_mode(self, player_id: str, mode: str, region: str = None) -> Dict[str, Any]:
        """Set player offline mode"""
        try:
            from systems.player_system import player_system
            
            player_data = file_manager.get_player(player_id)
            if not player_data:
                return {"success": False, "error": "Player not found"}
            
            valid_modes = ["none", "ambush", "scavenge"]
            if mode not in valid_modes:
                return {"success": False, "error": f"Invalid mode. Choose: {', '.join(valid_modes)}"}
            
            # Clear previous mode
            self._clear_offline_mode(player_id)
            
            if mode == "none":
                # Just clear the mode
                player_system.set_offline_mode(player_id, "none")
                return {"success": True, "message": "Offline mode cleared"}
            
            elif mode == "ambush":
                if not region:
                    return {"success": False, "error": "Region required for ambush mode"}
                
                # Set ambush mode
                player_system.set_offline_mode(player_id, "ambush")
                
                # Add to ambush regions
                if region not in self.ambush_regions:
                    self.ambush_regions[region] = []
                
                if player_id not in self.ambush_regions[region]:
                    self.ambush_regions[region].append(player_id)
                
                # Add to action history
                add_action_to_history(player_id, "ambush_mode_set", region=region)
                
                return {
                    "success": True,
                    "message": f"✅ Ambush mode set in {region}. You'll get first strike bonus if enemies enter your area."
                }
            
            elif mode == "scavenge":
                # Set scavenge mode
                player_system.set_offline_mode(player_id, "scavenge")
                
                # Initialize scavenge data
                self.scavenge_players[player_id] = {
                    "last_scavenge": 0,
                    "success_count": 0,
                    "region": player_data.get("location", "").split(":")[0]
                }
                
                # Add to action history
                add_action_to_history(player_id, "scavenge_mode_set", region=player_data.get("location", ""))
                
                return {
                    "success": True,
                    "message": "✅ Scavenge mode set. You'll passively gather resources while offline."
                }
            
        except Exception as e:
            logger.error(f"Error setting offline mode: {e}")
            return {"success": False, "error": "Failed to set offline mode"}
    
    def _clear_offline_mode(self, player_id: str):
        """Clear player's offline mode"""
        try:
            # Remove from ambush regions
            for region, players in self.ambush_regions.items():
                if player_id in players:
                    players.remove(player_id)
                    if not players:
                        del self.ambush_regions[region]
                    break
            
            # Remove from scavenge players
            if player_id in self.scavenge_players:
                del self.scavenge_players[player_id]
            
        except Exception as e:
            logger.error(f"Error clearing offline mode for player {player_id}: {e}")
    
    def process_ambush(self, player_id: str, target_region: str) -> Dict[str, Any]:
        """Process ambush when target enters region"""
        try:
            # Check if there are ambushers in the target region
            ambushers = self.ambush_regions.get(target_region, [])
            if not ambushers:
                return {"success": False, "message": "No ambushers in region"}
            
            # Find the best ambusher (highest intelligence or random)
            best_ambusher = None
            best_score = 0
            
            for ambusher_id in ambushers:
                ambusher_data = file_manager.get_player(ambusher_id)
                if ambusher_data and ambusher_data.get("status") == "alive":
                    # Score based on intelligence and random factor
                    score = ambusher_data.get("intelligence", 0) + random.randint(1, 50)
                    if score > best_score:
                        best_score = score
                        best_ambusher = ambusher_id
            
            if not best_ambusher:
                return {"success": False, "message": "No active ambushers found"}
            
            # Execute ambush
            return self._execute_ambush(best_ambusher, player_id, target_region)
            
        except Exception as e:
            logger.error(f"Error processing ambush: {e}")
            return {"success": False, "error": "Failed to process ambush"}
    
    def _execute_ambush(self, ambusher_id: str, target_id: str, region: str) -> Dict[str, Any]:
        """Execute ambush attack"""
        try:
            from systems.combat_system import combat_system
            from systems.player_system import player_system
            
            # Get ambusher data
            ambusher_data = file_manager.get_player(ambusher_id)
            target_data = file_manager.get_player(target_id)
            
            if not ambusher_data or not target_data:
                return {"success": False, "error": "Combatant not found"}
            
            # Create ambush combat
            combat_result = combat_system.initiate_combat(ambusher_id, target_id, "pvp")
            
            if not combat_result["success"]:
                return combat_result
            
            # Process ambush attack with bonus
            attack_data = {
                "alerted": True,  # Ambusher gets alerted bonus
                "ambush": True    # Ambusher gets ambush bonus
            }
            
            combat_result = combat_system.process_combat_turn(
                combat_result["combat_id"], 
                "attack", 
                attack_data
            )
            
            # Add to action history
            add_action_to_history(ambusher_id, "ambush_executed", target=target_id, region=region)
            add_action_to_history(target_id, "ambushed", attacker=ambusher_id, region=region)
            
            # Clear ambush mode for ambusher
            self._clear_offline_mode(ambusher_id)
            player_system.set_offline_mode(ambusher_id, "none")
            
            logger.info(f"Ambusher {ambusher_id} executed ambush on {target_id} in {region}")
            
            return {
                "success": True,
                "ambusher": ambusher_id,
                "target": target_id,
                "region": region,
                "combat_result": combat_result
            }
            
        except Exception as e:
            logger.error(f"Error executing ambush: {e}")
            return {"success": False, "error": "Failed to execute ambush"}
    
    def process_scavenge(self, player_id: str) -> Dict[str, Any]:
        """Process scavenge for offline player"""
        try:
            if player_id not in self.scavenge_players:
                return {"success": False, "error": "Player not in scavenge mode"}
            
            scavenge_data = self.scavenge_players[player_id]
            current_time = get_current_timestamp()
            
            # Check cooldown
            if current_time - scavenge_data["last_scavenge"] < OFFLINE_SCAVENGE_COOLDOWN:
                return {"success": False, "error": "Scavenge on cooldown"}
            
            # Get player data
            player_data = file_manager.get_player(player_id)
            if not player_data:
                return {"success": False, "error": "Player not found"}
            
            # Calculate scavenge success
            region = scavenge_data["region"]
            region_data = file_manager.get_region(region)
            if not region_data:
                return {"success": False, "error": "Region not found"}
            
            # Calculate success chance
            success_chance = self._calculate_scavenge_success(player_data, region_data)
            
            # Roll for success
            success = random.randint(1, 100) <= success_chance
            
            if success:
                # Get scavenge loot
                loot = self._get_scavenge_loot(region_data, player_data)
                
                # Add loot to inventory
                from systems.inventory_system import inventory_system
                for item_id, quantity in loot:
                    inventory_system.add_item(player_id, item_id, quantity)
                
                # Update scavenge data
                scavenge_data["last_scavenge"] = current_time
                scavenge_data["success_count"] += 1
                
                # Add to action history
                add_action_to_history(player_id, "scavenge_success", loot=loot, region=region)
                
                logger.info(f"Player {player_id} scavenged successfully in {region}")
                
                return {
                    "success": True,
                    "loot": loot,
                    "success_count": scavenge_data["success_count"],
                    "message": f"✅ Scavenged successfully! Found: {', '.join([f'{item} x{qty}' for item, qty in loot])}"
                }
            else:
                # Scavenge failed
                scavenge_data["last_scavenge"] = current_time
                
                # Add to action history
                add_action_to_history(player_id, "scavenge_failed", region=region)
                
                return {
                    "success": False,
                    "message": "Scavenge failed. No resources found."
                }
            
        except Exception as e:
            logger.error(f"Error processing scavenge: {e}")
            return {"success": False, "error": "Failed to process scavenge"}
    
    def _calculate_scavenge_success(self, player_data: Dict, region_data: Dict) -> int:
        """Calculate scavenge success chance"""
        try:
            # Base success chance
            base_chance = 30
            
            # Intelligence bonus
            intelligence = player_data.get("intelligence", 0)
            intelligence_bonus = intelligence // 10  # +1% per 10 intelligence
            
            # Class bonus
            char_class = player_data.get("class", "")
            class_bonus = 0
            if char_class == "Scavenger":
                class_bonus = 15  # +15% for Scavengers
            
            # Region danger penalty
            danger = region_data.get("danger", 0)
            danger_penalty = danger // 2  # -1% per 2 danger
            
            # Calculate final chance
            success_chance = base_chance + intelligence_bonus + class_bonus - danger_penalty
            
            # Clamp between 5% and 80%
            return max(5, min(80, success_chance))
            
        except Exception as e:
            logger.error(f"Error calculating scavenge success: {e}")
            return 30  # Default chance
    
    def _get_scavenge_loot(self, region_data: Dict, player_data: Dict) -> List[Tuple[str, int]]:
        """Get scavenge loot"""
        try:
            # Base loot items
            base_loot = [
                ("wood", 1, 3),
                ("metal", 1, 2),
                ("cloth", 1, 2),
                ("water", 1, 2)
            ]
            
            # Region-specific loot
            region_type = region_data.get("type", "forest")
            region_loot = {
                "forest": [("wood", 2, 5), ("herbs", 1, 2)],
                "urban": [("metal", 2, 4), ("cloth", 1, 3)],
                "military": [("ammo", 1, 3), ("circuit", 1, 2)],
                "coast": [("water", 2, 4), ("fish", 1, 2)]
            }
            
            # Get region-specific loot
            loot_items = region_loot.get(region_type, base_loot)
            
            # Calculate loot amount based on intelligence
            intelligence = player_data.get("intelligence", 0)
            loot_multiplier = 1 + (intelligence // 50)  # +1x per 50 intelligence
            
            # Generate loot
            final_loot = []
            for item_id, min_qty, max_qty in loot_items:
                if random.random() < 0.7:  # 70% chance for each item
                    quantity = random.randint(min_qty, max_qty)
                    quantity = int(quantity * loot_multiplier)
                    final_loot.append((item_id, quantity))
            
            return final_loot
            
        except Exception as e:
            logger.error(f"Error getting scavenge loot: {e}")
            return [("wood", 1)]
    
    def get_offline_status(self, player_id: str) -> Dict[str, Any]:
        """Get player's offline status"""
        try:
            player_data = file_manager.get_player(player_id)
            if not player_data:
                return {"success": False, "error": "Player not found"}
            
            offline_mode = player_data.get("offline_mode", "none")
            
            status = {
                "mode": offline_mode,
                "active": False
            }
            
            if offline_mode == "ambush":
                # Find which region player is ambushing
                for region, players in self.ambush_regions.items():
                    if player_id in players:
                        status["active"] = True
                        status["region"] = region
                        break
            
            elif offline_mode == "scavenge":
                if player_id in self.scavenge_players:
                    scavenge_data = self.scavenge_players[player_id]
                    status["active"] = True
                    status["region"] = scavenge_data["region"]
                    status["success_count"] = scavenge_data["success_count"]
                    status["last_scavenge"] = scavenge_data["last_scavenge"]
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting offline status: {e}")
            return {"success": False, "error": "Failed to get offline status"}
    
    def format_offline_status(self, player_id: str) -> str:
        """Format offline status for display"""
        try:
            status = self.get_offline_status(player_id)
            if not status.get("active"):
                return "💤 **Offline Mode: None**\nUse `/setmode ambush <region>` or `/setmode scavenge` to set offline mode."
            
            mode = status.get("mode", "none")
            
            if mode == "ambush":
                region = status.get("region", "Unknown")
                return f"🎯 **Offline Mode: Ambush**\nRegion: {region}\nYou'll get first strike bonus if enemies enter your area."
            
            elif mode == "scavenge":
                region = status.get("region", "Unknown")
                success_count = status.get("success_count", 0)
                last_scavenge = status.get("last_scavenge", 0)
                
                display = f"🔍 **Offline Mode: Scavenge**\n"
                display += f"Region: {region}\n"
                display += f"Successful scavenges: {success_count}\n"
                
                if last_scavenge > 0:
                    from utils.helpers import format_duration
                    time_since = get_current_timestamp() - last_scavenge
                    display += f"Last scavenge: {format_duration(time_since)} ago\n"
                
                return display
            
            return "💤 **Offline Mode: None**"
            
        except Exception as e:
            logger.error(f"Error formatting offline status: {e}")
            return "❌ Error getting offline status"
    
    def cleanup_offline_modes(self):
        """Clean up expired offline modes"""
        try:
            current_time = get_current_timestamp()
            
            # Clean up scavenge players who haven't been active
            inactive_players = []
            for player_id, scavenge_data in self.scavenge_players.items():
                if current_time - scavenge_data["last_scavenge"] > 86400:  # 24 hours
                    inactive_players.append(player_id)
            
            for player_id in inactive_players:
                del self.scavenge_players[player_id]
                logger.info(f"Cleaned up inactive scavenge player {player_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up offline modes: {e}")

# Global offline system instance
offline_system = OfflineSystem()