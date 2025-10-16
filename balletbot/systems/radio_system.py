"""
Radio system for BalletBot: Outbreak Dominion
Handles anonymous frequency-based communication
"""

import logging
from typing import Dict, List, Optional, Any
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp, add_action_to_history

logger = logging.getLogger(__name__)

class RadioSystem:
    """Manages radio communication and frequencies"""
    
    def __init__(self):
        self.active_frequencies: Dict[str, List[str]] = {}  # freq -> list of player_ids
        self.player_frequencies: Dict[str, str] = {}  # player_id -> frequency
        self.radio_towers: Dict[str, Dict] = {}  # location -> tower info
    
    def set_frequency(self, player_id: str, frequency: str) -> Dict[str, Any]:
        """Set player's radio frequency"""
        try:
            # Validate frequency format
            if not self._is_valid_frequency(frequency):
                return {"success": False, "error": "Invalid frequency format. Use numbers (101.5) or letters (alpha)"}
            
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
            
            # Add to action history
            add_action_to_history(player_id, "frequency_set", frequency=frequency)
            
            return {
                "success": True,
                "frequency": frequency,
                "message": f"✅ Tuned to frequency {frequency}"
            }
            
        except Exception as e:
            logger.error(f"Error setting frequency: {e}")
            return {"success": False, "error": "Failed to set frequency"}
    
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
        try:
            from systems.inventory_system import inventory_system
            
            # Check if player is tuned to this frequency
            if self.player_frequencies.get(player_id) != frequency:
                return {"success": False, "error": "You're not tuned to this frequency"}
            
            # Check if player has radio access
            if not self._has_radio_access(player_id):
                return {"success": False, "error": "You need a radio to transmit"}
            
            # Validate message
            if not message or len(message) > 500:
                return {"success": False, "error": "Message must be 1-500 characters"}
            
            # Get player info
            player_data = file_manager.get_player(player_id)
            if not player_data:
                return {"success": False, "error": "Player not found"}
            
            # Get all players on this frequency
            listeners = self.active_frequencies.get(frequency, [])
            if not listeners:
                return {"success": False, "error": "No one is listening on this frequency"}
            
            # Create anonymous message
            anonymous_message = f"📻 **{frequency}** - anon@{frequency}: {message}"
            
            # Add to action history
            add_action_to_history(player_id, "radio_message_sent", frequency=frequency, message=message, listeners=len(listeners))
            
            return {
                "success": True,
                "message": anonymous_message,
                "listeners": len(listeners),
                "frequency": frequency
            }
            
        except Exception as e:
            logger.error(f"Error sending radio message: {e}")
            return {"success": False, "error": "Failed to send radio message"}
    
    def _has_radio_access(self, player_id: str) -> bool:
        """Check if player has radio access"""
        try:
            from systems.inventory_system import inventory_system
            
            # Check if player has radio item
            if inventory_system.has_item(player_id, "radio", 1):
                return True
            
            # Check if player is in a location with radio tower
            player_data = file_manager.get_player(player_id)
            if not player_data:
                return False
            
            location = player_data.get("location", "")
            return self._has_radio_tower(location)
            
        except Exception as e:
            logger.error(f"Error checking radio access: {e}")
            return False
    
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
        try:
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
            
            # Add to action history
            add_action_to_history(player_id, "frequency_left", frequency=frequency)
            
            return True
            
        except Exception as e:
            logger.error(f"Error leaving frequency: {e}")
            return False
    
    def create_radio_tower(self, location: str, owner_id: str) -> bool:
        """Create a radio tower at a location"""
        try:
            self.radio_towers[location] = {
                "owner_id": owner_id,
                "created_at": get_current_timestamp(),
                "range": 5  # Can reach 5 connected areas
            }
            
            # Add to action history
            add_action_to_history(owner_id, "radio_tower_created", location=location)
            
            logger.info(f"Radio tower created at {location} by {owner_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating radio tower: {e}")
            return False
    
    def get_radio_tower_info(self, location: str) -> Optional[Dict[str, Any]]:
        """Get radio tower information for a location"""
        return self.radio_towers.get(location)
    
    def get_radio_display(self, player_id: str) -> str:
        """Get formatted radio display for player"""
        try:
            current_freq = self.get_player_frequency(player_id)
            
            if not current_freq:
                return "📻 **Radio Off**\nUse `/setfreq <frequency>` to tune in"
            
            freq_info = self.get_frequency_info(current_freq)
            
            display = f"📻 **Radio - Frequency {current_freq}**\n"
            display += f"Listeners: {freq_info['listener_count']}\n"
            display += f"Status: {'Active' if freq_info['active'] else 'Silent'}\n\n"
            display += "Use `/radio <frequency> <message>` to transmit"
            
            return display
            
        except Exception as e:
            logger.error(f"Error getting radio display: {e}")
            return "❌ Error getting radio status"
    
    def get_frequency_list(self) -> str:
        """Get list of active frequencies"""
        try:
            if not self.active_frequencies:
                return "📻 **No active frequencies**"
            
            display = "📻 **Active Frequencies:**\n\n"
            
            for frequency, listeners in self.active_frequencies.items():
                display += f"**{frequency}** - {len(listeners)} listener(s)\n"
            
            return display
            
        except Exception as e:
            logger.error(f"Error getting frequency list: {e}")
            return "❌ Error getting frequency list"
    
    def get_radio_status(self, player_id: str) -> Dict[str, Any]:
        """Get player's radio status"""
        try:
            current_freq = self.get_player_frequency(player_id)
            has_access = self._has_radio_access(player_id)
            
            return {
                "has_access": has_access,
                "current_frequency": current_freq,
                "can_transmit": has_access and current_freq is not None
            }
            
        except Exception as e:
            logger.error(f"Error getting radio status: {e}")
            return {"has_access": False, "current_frequency": None, "can_transmit": False}
    
    def format_radio_status(self, player_id: str) -> str:
        """Format radio status for display"""
        try:
            status = self.get_radio_status(player_id)
            
            if not status["has_access"]:
                return "📻 **No Radio Access**\nYou need a radio item or be near a radio tower to use radio."
            
            if not status["current_frequency"]:
                return "📻 **Radio Off**\nUse `/setfreq <frequency>` to tune in"
            
            return self.get_radio_display(player_id)
            
        except Exception as e:
            logger.error(f"Error formatting radio status: {e}")
            return "❌ Error getting radio status"

# Global radio system instance
radio_system = RadioSystem()