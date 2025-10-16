"""
Spotter/Intel system for BalletBot: Outbreak Dominion
Handles intelligence gathering and player surveillance
"""

import logging
from typing import Dict, List, Optional, Any

from utils.helpers import get_current_timestamp, sanitize_input
from utils.db import log_event
from config import SPOTTER_COST

logger = logging.getLogger(__name__)

class SpotterSystem:
    """Manages intelligence gathering and surveillance"""
    
    def __init__(self):
        self.spotter_uses: Dict[str, int] = {}  # player_id -> last use timestamp
        self.spotter_cooldown = 300  # 5 minutes
    
    def buy_spotter(self, player_id: str) -> Dict[str, Any]:
        """Buy a spotter device"""
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
        
        log_event("spotter_purchased", {
            "player_id": player_id,
            "cost": SPOTTER_COST
        })
        
        return {
            "success": True,
            "message": "Spotter device purchased successfully"
        }
    
    def use_spotter(self, player_id: str, target: str) -> Dict[str, Any]:
        """Use spotter device to gather intelligence"""
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
        target_player = None
        
        # Try by username first
        if target.startswith("@"):
            username = target[1:]  # Remove @
            target_player = player_system.get_player_by_username(username, "DEFAULT")  # TODO: Get actual group code
        else:
            # Try by player ID
            target_player = player_system.get_player(target)
        
        if not target_player:
            return {"success": False, "error": "Target player not found"}
        
        # Get target's recent actions
        recent_actions = self._get_recent_actions(target_player["id"])
        
        # Update cooldown
        self.spotter_uses[player_id] = get_current_timestamp()
        
        # Create intelligence report
        report = self._create_intelligence_report(target_player, recent_actions)
        
        log_event("spotter_used", {
            "user_id": player_id,
            "target_id": target_player["id"],
            "target_username": target_player["username"]
        })
        
        return {
            "success": True,
            "report": report,
            "target": target_player["username"]
        }
    
    def _can_use_spotter(self, player_id: str) -> bool:
        """Check if player can use spotter (cooldown)"""
        if player_id not in self.spotter_uses:
            return True
        
        last_use = self.spotter_uses[player_id]
        return (get_current_timestamp() - last_use) >= self.spotter_cooldown
    
    def _get_recent_actions(self, player_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent actions for a player"""
        from systems.player_system import player_system
        
        player = player_system.get_player(player_id)
        if not player:
            return []
        
        actions = player.get("last_actions", [])
        return actions[-limit:] if actions else []
    
    def _create_intelligence_report(self, target_player: Dict[str, Any], 
                                  recent_actions: List[Dict[str, Any]]) -> str:
        """Create formatted intelligence report"""
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
    
    def get_spotter_info(self, player_id: str) -> Dict[str, Any]:
        """Get spotter information for a player"""
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
    
    def get_spotter_display(self, player_id: str) -> str:
        """Get formatted spotter display for player"""
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
    
    def get_spotter_cost_display(self) -> str:
        """Get formatted spotter cost display"""
        cost_items = []
        for item, qty in SPOTTER_COST.items():
            cost_items.append(f"{item} x{qty}")
        
        return f"🕵️ **Spotter Device Cost:**\n{', '.join(cost_items)}"
    
    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get intelligence system summary"""
        total_uses = len(self.spotter_uses)
        active_users = sum(1 for last_use in self.spotter_uses.values() 
                          if (get_current_timestamp() - last_use) < 3600)  # Active in last hour
        
        return {
            "total_spotter_uses": total_uses,
            "active_users": active_users,
            "cooldown_duration": self.spotter_cooldown
        }

# Global spotter system instance
spotter_system = SpotterSystem()