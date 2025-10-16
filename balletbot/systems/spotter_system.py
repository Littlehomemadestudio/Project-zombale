"""
Spotter/Intel system for BalletBot: Outbreak Dominion
Handles intelligence gathering and player surveillance
"""

import logging
from typing import Dict, List, Optional, Any
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp, add_action_to_history
from config import SPOTTER_COST

logger = logging.getLogger(__name__)

class SpotterSystem:
    """Manages intelligence gathering and surveillance"""
    
    def __init__(self):
        self.spotter_uses: Dict[str, int] = {}  # player_id -> last use timestamp
        self.spotter_cooldown = 300  # 5 minutes
    
    def buy_spotter(self, player_id: str) -> Dict[str, Any]:
        """Buy a spotter device"""
        try:
            from systems.inventory_system import inventory_system
            
            # Check if player has required resources
            can_afford, missing = inventory_system.can_craft_item(player_id, {
                "resources": SPOTTER_COST
            })
            
            if not can_afford:
                return {
                    "success": False,
                    "error": f"Insufficient resources. Missing: {', '.join(missing)}"
                }
            
            # Consume resources
            if not inventory_system.consume_crafting_materials(player_id, {
                "resources": SPOTTER_COST
            }):
                return {"success": False, "error": "Failed to consume resources"}
            
            # Give spotter device
            if not inventory_system.add_item(player_id, "spotter_device", 1):
                return {"success": False, "error": "Failed to create spotter device"}
            
            # Add to action history
            add_action_to_history(player_id, "spotter_purchased", cost=SPOTTER_COST)
            
            logger.info(f"Player {player_id} purchased spotter device")
            
            return {
                "success": True,
                "message": "✅ Spotter device purchased successfully"
            }
            
        except Exception as e:
            logger.error(f"Error buying spotter: {e}")
            return {"success": False, "error": "Failed to buy spotter device"}
    
    def use_spotter(self, player_id: str, target: str) -> Dict[str, Any]:
        """Use spotter device to gather intelligence"""
        try:
            from systems.inventory_system import inventory_system
            from systems.player_system import player_system
            
            # Check if player has spotter device
            if not inventory_system.has_item(player_id, "spotter_device", 1):
                return {"success": False, "error": "You need a spotter device"}
            
            # Check cooldown
            if not self._can_use_spotter(player_id):
                last_use = self.spotter_uses.get(player_id, 0)
                time_remaining = self.spotter_cooldown - (get_current_timestamp() - last_use)
                return {
                    "success": False,
                    "error": f"Spotter on cooldown. {time_remaining} seconds remaining"
                }
            
            # Find target player
            target_player = self._find_target_player(target)
            if not target_player:
                return {"success": False, "error": "Target player not found"}
            
            # Get target's recent actions
            recent_actions = self._get_recent_actions(target_player["id"])
            
            # Update cooldown
            self.spotter_uses[player_id] = get_current_timestamp()
            
            # Create intelligence report
            report = self._create_intelligence_report(target_player, recent_actions)
            
            # Add to action history
            add_action_to_history(player_id, "spotter_used", target_id=target_player["id"], target_username=target_player["username"])
            
            logger.info(f"Player {player_id} used spotter on {target_player['username']}")
            
            return {
                "success": True,
                "report": report,
                "target": target_player["username"]
            }
            
        except Exception as e:
            logger.error(f"Error using spotter: {e}")
            return {"success": False, "error": "Failed to use spotter device"}
    
    def _find_target_player(self, target: str) -> Optional[Dict]:
        """Find target player by username or ID"""
        try:
            from systems.player_system import player_system
            
            # Try by username first
            if target.startswith("@"):
                username = target[1:]  # Remove @
                # Search all players for matching username
                all_players = file_manager.get_all_players()
                for player_data in all_players.values():
                    if player_data.get("username", "").lower() == username.lower():
                        return player_data
            else:
                # Try by player ID
                return file_manager.get_player(target)
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding target player: {e}")
            return None
    
    def _can_use_spotter(self, player_id: str) -> bool:
        """Check if player can use spotter (cooldown)"""
        if player_id not in self.spotter_uses:
            return True
        
        last_use = self.spotter_uses[player_id]
        return (get_current_timestamp() - last_use) >= self.spotter_cooldown
    
    def _get_recent_actions(self, player_id: str, limit: int = 10) -> List[Dict]:
        """Get recent actions for a player"""
        try:
            from utils.helpers import get_action_history
            return get_action_history(player_id, limit)
            
        except Exception as e:
            logger.error(f"Error getting recent actions: {e}")
            return []
    
    def _create_intelligence_report(self, target_player: Dict, recent_actions: List[Dict]) -> str:
        """Create formatted intelligence report"""
        try:
            username = target_player["username"]
            location = target_player.get("location", "Unknown")
            status = target_player.get("status", "Unknown")
            hp = target_player.get("hp", 0)
            intelligence = target_player.get("intelligence", 0)
            
            report = f"🕵️ **Intelligence Report: {username}**\n\n"
            report += f"📍 **Location:** {location}\n"
            report += f"👤 **Status:** {status}\n"
            report += f"❤️ **Health:** {hp}/100\n"
            report += f"🧠 **Intelligence:** {intelligence}\n\n"
            
            if recent_actions:
                report += "📋 **Recent Actions:**\n"
                for action in recent_actions[-5:]:  # Show last 5 actions
                    action_name = action.get("action", "Unknown")
                    timestamp = action.get("timestamp", 0)
                    time_ago = get_current_timestamp() - timestamp
                    
                    # Format time ago
                    if time_ago < 60:
                        time_str = f"{time_ago}s ago"
                    elif time_ago < 3600:
                        time_str = f"{time_ago // 60}m ago"
                    else:
                        time_str = f"{time_ago // 3600}h ago"
                    
                    report += f"• {action_name} ({time_str})\n"
            else:
                report += "📋 **Recent Actions:** None recorded\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Error creating intelligence report: {e}")
            return "❌ Error creating intelligence report"
    
    def get_spotter_info(self, player_id: str) -> Dict[str, Any]:
        """Get spotter information for a player"""
        try:
            from systems.inventory_system import inventory_system
            
            has_spotter = inventory_system.has_item(player_id, "spotter_device", 1)
            can_use = self._can_use_spotter(player_id)
            
            cooldown_remaining = 0
            if not can_use and player_id in self.spotter_uses:
                last_use = self.spotter_uses[player_id]
                cooldown_remaining = self.spotter_cooldown - (get_current_timestamp() - last_use)
            
            return {
                "has_spotter": has_spotter,
                "can_use": can_use,
                "cooldown_remaining": cooldown_remaining,
                "cooldown_duration": self.spotter_cooldown
            }
            
        except Exception as e:
            logger.error(f"Error getting spotter info: {e}")
            return {"has_spotter": False, "can_use": False, "cooldown_remaining": 0, "cooldown_duration": 0}
    
    def get_spotter_display(self, player_id: str) -> str:
        """Get formatted spotter display for player"""
        try:
            info = self.get_spotter_info(player_id)
            
            if not info["has_spotter"]:
                return "🕵️ **No Spotter Device**\nUse `/intel buy_spotter` to purchase one"
            
            if info["can_use"]:
                return "🕵️ **Spotter Ready**\nUse `/intel use_spotter <target>` to gather intelligence"
            else:
                cooldown = info["cooldown_remaining"]
                minutes = cooldown // 60
                seconds = cooldown % 60
                return f"🕵️ **Spotter on Cooldown**\nReady in {minutes}m {seconds}s"
                
        except Exception as e:
            logger.error(f"Error getting spotter display: {e}")
            return "❌ Error getting spotter status"
    
    def get_spotter_cost_display(self) -> str:
        """Get formatted spotter cost display"""
        try:
            cost_items = []
            for item, qty in SPOTTER_COST.items():
                cost_items.append(f"{item} x{qty}")
            
            return f"🕵️ **Spotter Device Cost:**\n{', '.join(cost_items)}"
            
        except Exception as e:
            logger.error(f"Error getting spotter cost display: {e}")
            return "❌ Error getting spotter cost"
    
    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get intelligence system summary"""
        try:
            total_uses = len(self.spotter_uses)
            active_users = sum(1 for last_use in self.spotter_uses.values() 
                              if (get_current_timestamp() - last_use) < 3600)  # Active in last hour
            
            return {
                "total_spotter_uses": total_uses,
                "active_users": active_users,
                "cooldown_duration": self.spotter_cooldown
            }
            
        except Exception as e:
            logger.error(f"Error getting intelligence summary: {e}")
            return {"total_spotter_uses": 0, "active_users": 0, "cooldown_duration": 0}
    
    def format_intelligence_summary(self) -> str:
        """Format intelligence summary for display"""
        try:
            summary = self.get_intelligence_summary()
            
            display = "🕵️ **Intelligence System Summary**\n\n"
            display += f"Total spotter uses: {summary['total_spotter_uses']}\n"
            display += f"Active users (last hour): {summary['active_users']}\n"
            display += f"Cooldown duration: {summary['cooldown_duration']}s\n"
            
            return display
            
        except Exception as e:
            logger.error(f"Error formatting intelligence summary: {e}")
            return "❌ Error getting intelligence summary"

# Global spotter system instance
spotter_system = SpotterSystem()