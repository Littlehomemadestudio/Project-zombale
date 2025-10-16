"""
Radio system for BalletBot: Outbreak Dominion
Handles anonymous frequency-based communication
"""

import logging
from typing import Dict, List, Optional, Any

from utils.helpers import get_current_timestamp, sanitize_input
from utils.db import log_event

logger = logging.getLogger(__name__)

class RadioSystem:
    """Manages radio communication and frequencies"""
    
    def __init__(self):
        self.active_frequencies: Dict[str, List[str]] = {}  # freq -> list of player_ids
        self.player_frequencies: Dict[str, str] = {}  # player_id -> frequency
        self.radio_towers: Dict[str, Dict] = {}  # location -> tower info
    
    def set_frequency(self, player_id: str, frequency: str) -> Dict[str, Any]:
        """Set player's radio frequency"""
        # Validate frequency format (e.g., "101.5", "emergency", "alpha")
        if not self._is_valid_frequency(frequency):
            return {"success": False, "error": "Invalid frequency format"}
        
        # Remove player from previous frequency
        if player_id in self.player_frequencies:
            old_freq = self.player_frequencies[player_id]
            if old_freq in self.active_frequencies:
                self.active_frequencies[old_freq].remove(player_id)
                if not self.active_frequencies[old_freq]:
                    del self.active_frequencies[old_freq]
        
        # Add player to new frequency
        if frequency not in self.active_frequencies:
            self.active_frequencies[frequency] = []
        
        if player_id not in self.active_frequencies[frequency]:
            self.active_frequencies[frequency].append(player_id)
        
        self.player_frequencies[player_id] = frequency
        
        log_event("frequency_set", {
            "player_id": player_id,
            "frequency": frequency
        })
        
        return {
            "success": True,
            "frequency": frequency,
            "message": f"Tuned to frequency {frequency}"
        }
    
    def _is_valid_frequency(self, frequency: str) -> bool:
        """Validate frequency format"""
        # Allow numeric frequencies (101.5, 99.9) or named frequencies (emergency, alpha)
        if frequency.replace(".", "").isdigit():
            return True
        if frequency.isalpha():
            return True
        return False
    
    def send_radio_message(self, player_id: str, frequency: str, message: str) -> Dict[str, Any]:
        """Send a radio message"""
        from systems.player_system import player_system
        
        # Check if player is tuned to this frequency
        if self.player_frequencies.get(player_id) != frequency:
            return {"success": False, "error": "You're not tuned to this frequency"}
        
        # Check if player has radio access
        if not self._has_radio_access(player_id):
            return {"success": False, "error": "You need a radio to transmit"}
        
        # Sanitize message
        message = sanitize_input(message, 500)
        if not message:
            return {"success": False, "error": "Message cannot be empty"}
        
        # Get player info
        player = player_system.get_player(player_id)
        if not player:
            return {"success": False, "error": "Player not found"}
        
        # Get all players on this frequency
        listeners = self.active_frequencies.get(frequency, [])
        if not listeners:
            return {"success": False, "error": "No one is listening on this frequency"}
        
        # Create anonymous message
        anonymous_message = f"📻 **{frequency}** - anon@{frequency}: {message}"
        
        # Send to all listeners
        from bale_api import bale_api
        for listener_id in listeners:
            if listener_id != player_id:  # Don't send to sender
                await bale_api.send_message(listener_id, anonymous_message)
        
        log_event("radio_message_sent", {
            "sender_id": player_id,
            "frequency": frequency,
            "message": message,
            "listeners": len(listeners) - 1
        })
        
        return {
            "success": True,
            "message": anonymous_message,
            "listeners": len(listeners) - 1
        }
    
    def _has_radio_access(self, player_id: str) -> bool:
        """Check if player has radio access"""
        from systems.inventory_system import inventory_system
        
        # Check if player has radio item
        if inventory_system.has_item(player_id, "radio", 1):
            return True
        
        # Check if player is in a location with radio tower
        from systems.player_system import player_system
        player = player_system.get_player(player_id)
        if not player:
            return False
        
        location = player.get("location", "")
        return self._has_radio_tower(location)
    
    def _has_radio_tower(self, location: str) -> bool:
        """Check if location has a radio tower"""
        return location in self.radio_towers
    
    def get_frequency_info(self, frequency: str) -> Dict[str, Any]:
        """Get information about a frequency"""
        listeners = self.active_frequencies.get(frequency, [])
        
        return {
            "frequency": frequency,
            "listener_count": len(listeners),
            "active": len(listeners) > 0
        }
    
    def get_player_frequency(self, player_id: str) -> Optional[str]:
        """Get player's current frequency"""
        return self.player_frequencies.get(player_id)
    
    def get_available_frequencies(self) -> List[str]:
        """Get list of available frequencies"""
        return list(self.active_frequencies.keys())
    
    def leave_frequency(self, player_id: str) -> bool:
        """Remove player from their current frequency"""
        if player_id not in self.player_frequencies:
            return False
        
        frequency = self.player_frequencies[player_id]
        
        # Remove from frequency list
        if frequency in self.active_frequencies:
            if player_id in self.active_frequencies[frequency]:
                self.active_frequencies[frequency].remove(player_id)
            
            # Remove frequency if no listeners
            if not self.active_frequencies[frequency]:
                del self.active_frequencies[frequency]
        
        # Remove from player frequencies
        del self.player_frequencies[player_id]
        
        log_event("frequency_left", {
            "player_id": player_id,
            "frequency": frequency
        })
        
        return True
    
    def create_radio_tower(self, location: str, owner_id: str) -> bool:
        """Create a radio tower at a location"""
        self.radio_towers[location] = {
            "owner_id": owner_id,
            "created_at": get_current_timestamp(),
            "range": 5  # Can reach 5 connected areas
        }
        
        log_event("radio_tower_created", {
            "location": location,
            "owner_id": owner_id
        })
        
        return True
    
    def get_radio_tower_info(self, location: str) -> Optional[Dict[str, Any]]:
        """Get radio tower information for a location"""
        return self.radio_towers.get(location)
    
    def get_radio_display(self, player_id: str) -> str:
        """Get formatted radio display for player"""
        current_freq = self.get_player_frequency(player_id)
        
        if not current_freq:
            return "📻 **Radio Off**\nUse `/setfreq <frequency>` to tune in"
        
        freq_info = self.get_frequency_info(current_freq)
        
        display = f"📻 **Radio - Frequency {current_freq}**\n"
        display += f"Listeners: {freq_info['listener_count']}\n"
        display += f"Status: {'Active' if freq_info['active'] else 'Silent'}\n\n"
        display += "Use `/radio <frequency> <message>` to transmit"
        
        return display
    
    def get_frequency_list(self) -> str:
        """Get list of active frequencies"""
        if not self.active_frequencies:
            return "📻 **No active frequencies**"
        
        display = "📻 **Active Frequencies:**\n\n"
        
        for frequency, listeners in self.active_frequencies.items():
            display += f"**{frequency}** - {len(listeners)} listener(s)\n"
        
        return display

# Global radio system instance
radio_system = RadioSystem()