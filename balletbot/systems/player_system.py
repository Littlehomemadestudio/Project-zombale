"""
Player system for BalletBot: Outbreak Dominion
Handles player creation, character classes, and player management
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from utils.db import db, get_player, create_player, update_player, add_item_to_inventory
from utils.helpers import get_current_timestamp, sanitize_input, format_player_stats
from config import CLASS_BONUSES, PLAYER_MAX_HP, PLAYER_MAX_STAMINA

logger = logging.getLogger(__name__)

@dataclass
class CharacterClass:
    """Character class definition"""
    name: str
    description: str
    bonuses: Dict[str, Any]

# Available character classes
CHARACTER_CLASSES = {
    "Scavenger": CharacterClass(
        name="Scavenger",
        description="Expert at finding resources and staying hidden",
        bonuses=CLASS_BONUSES["Scavenger"]
    ),
    "Mechanic": CharacterClass(
        name="Mechanic", 
        description="Skilled at crafting and repairing equipment",
        bonuses=CLASS_BONUSES["Mechanic"]
    ),
    "Soldier": CharacterClass(
        name="Soldier",
        description="Combat specialist with enhanced weapon skills",
        bonuses=CLASS_BONUSES["Soldier"]
    )
}

class PlayerSystem:
    """Manages player operations and character classes"""
    
    def __init__(self):
        self.active_players: Dict[str, Dict] = {}
    
    def get_character_class(self, class_name: str) -> Optional[CharacterClass]:
        """Get character class by name"""
        return CHARACTER_CLASSES.get(class_name.title())
    
    def list_character_classes(self) -> List[CharacterClass]:
        """Get list of available character classes"""
        return list(CHARACTER_CLASSES.values())
    
    def create_character(self, user_id: str, username: str, class_name: str, 
                        group_code: str) -> Dict[str, Any]:
        """Create a new player character"""
        # Validate class
        char_class = self.get_character_class(class_name)
        if not char_class:
            return {"success": False, "error": f"Invalid class: {class_name}"}
        
        # Check if player already exists
        existing = get_player(user_id)
        if existing:
            return {"success": False, "error": "Player already exists"}
        
        # Create player data
        player_data = {
            "id": user_id,
            "username": sanitize_input(username),
            "group_code": group_code,
            "class": char_class.name,
            "hp": PLAYER_MAX_HP,
            "stamina": PLAYER_MAX_STAMINA,
            "hunger": 0,
            "infection": 0,
            "intelligence": 0,
            "location": "Forest:Camp:Area1",
            "shelter_id": None,
            "status": "alive",
            "offline_mode": "none",
            "last_active": get_current_timestamp(),
            "last_actions": [],
            "created_at": get_current_timestamp()
        }
        
        # Create player in database
        if not create_player(player_data):
            return {"success": False, "error": "Failed to create player"}
        
        # Give starter items
        self._give_starter_items(user_id)
        
        # Cache player data
        self.active_players[user_id] = player_data
        
        logger.info(f"Created character {username} ({char_class.name}) for user {user_id}")
        
        return {
            "success": True,
            "player": player_data,
            "message": f"Character created! Welcome {username}, the {char_class.name}!"
        }
    
    def _give_starter_items(self, player_id: str):
        """Give starter items to new player"""
        starter_items = [
            ("knife", 1),
            ("small_backpack", 1),
            ("basic_rations", 3),
            ("bandage", 2),
            ("water_bottle", 1)
        ]
        
        for item_id, quantity in starter_items:
            add_item_to_inventory(player_id, item_id, quantity)
    
    def get_player(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get player data"""
        # Check cache first
        if player_id in self.active_players:
            return self.active_players[player_id]
        
        # Load from database
        player = get_player(player_id)
        if player:
            # Convert JSON fields
            if isinstance(player.get('last_actions'), str):
                player['last_actions'] = json.loads(player['last_actions'])
            self.active_players[player_id] = player
        
        return player
    
    def update_player(self, player_id: str, updates: Dict[str, Any]) -> bool:
        """Update player data"""
        try:
            # Update database
            success = update_player(player_id, updates)
            if success:
                # Update cache
                if player_id in self.active_players:
                    self.active_players[player_id].update(updates)
                else:
                    # Reload from database
                    self.active_players[player_id] = self.get_player(player_id)
            return success
        except Exception as e:
            logger.error(f"Failed to update player {player_id}: {e}")
            return False
    
    def get_player_status(self, player_id: str) -> Optional[str]:
        """Get formatted player status"""
        player = self.get_player(player_id)
        if not player:
            return None
        
        char_class = self.get_character_class(player.get('class', ''))
        class_info = f" ({char_class.description})" if char_class else ""
        
        status = f"👤 {player['username']} - {player['class']}{class_info}\n"
        status += format_player_stats(player)
        
        return status
    
    def join_game(self, user_id: str, username: str, group_code: str) -> Dict[str, Any]:
        """Join a game with existing character or prompt for creation"""
        # Check if player exists
        player = get_player(user_id)
        if player:
            if player['group_code'] == group_code:
                return {
                    "success": True,
                    "player": player,
                    "message": f"Welcome back, {player['username']}!"
                }
            else:
                return {
                    "success": False,
                    "error": "You're already in a different game"
                }
        
        # Player doesn't exist, need to create character
        return {
            "success": False,
            "error": "Character not found. Use /create_character <name> <class> to create one.",
            "need_character": True
        }
    
    def get_players_in_group(self, group_code: str) -> List[Dict[str, Any]]:
        """Get all players in a group"""
        players = db.execute_query(
            "SELECT * FROM players WHERE group_code = ? AND status = 'alive'",
            (group_code,)
        )
        
        # Convert JSON fields
        for player in players:
            if isinstance(player.get('last_actions'), str):
                player['last_actions'] = json.loads(player['last_actions'])
        
        return players
    
    def get_players_in_location(self, location: str) -> List[Dict[str, Any]]:
        """Get all players in a specific location"""
        players = db.execute_query(
            "SELECT * FROM players WHERE location = ? AND status = 'alive'",
            (location,)
        )
        
        # Convert JSON fields
        for player in players:
            if isinstance(player.get('last_actions'), str):
                player['last_actions'] = json.loads(player['last_actions'])
        
        return players
    
    def move_player(self, player_id: str, new_location: str) -> bool:
        """Move player to new location"""
        return self.update_player(player_id, {
            "location": new_location,
            "last_active": get_current_timestamp()
        })
    
    def update_player_health(self, player_id: str, hp_change: int) -> bool:
        """Update player health"""
        player = self.get_player(player_id)
        if not player:
            return False
        
        new_hp = max(0, min(PLAYER_MAX_HP, player['hp'] + hp_change))
        return self.update_player(player_id, {"hp": new_hp})
    
    def update_player_stamina(self, player_id: str, stamina_change: int) -> bool:
        """Update player stamina"""
        player = self.get_player(player_id)
        if not player:
            return False
        
        new_stamina = max(0, min(PLAYER_MAX_STAMINA, player['stamina'] + stamina_change))
        return self.update_player(player_id, {"stamina": new_stamina})
    
    def update_player_hunger(self, player_id: str, hunger_change: int) -> bool:
        """Update player hunger"""
        player = self.get_player(player_id)
        if not player:
            return False
        
        new_hunger = max(0, min(100, player['hunger'] + hunger_change))
        return self.update_player(player_id, {"hunger": new_hunger})
    
    def update_player_infection(self, player_id: str, infection_change: int) -> bool:
        """Update player infection"""
        player = self.get_player(player_id)
        if not player:
            return False
        
        new_infection = max(0, min(100, player['infection'] + infection_change))
        return self.update_player(player_id, {"infection": new_infection})
    
    def update_player_intelligence(self, player_id: str, intelligence_change: int) -> bool:
        """Update player intelligence"""
        player = self.get_player(player_id)
        if not player:
            return False
        
        new_intelligence = max(0, min(100, player['intelligence'] + intelligence_change))
        return self.update_player(player_id, {"intelligence": new_intelligence})
    
    def set_player_status(self, player_id: str, status: str) -> bool:
        """Set player status (alive, zombie, etc.)"""
        valid_statuses = ["alive", "zombie", "dead"]
        if status not in valid_statuses:
            return False
        
        return self.update_player(player_id, {"status": status})
    
    def set_offline_mode(self, player_id: str, mode: str) -> bool:
        """Set player offline mode"""
        valid_modes = ["none", "ambush", "scavenge"]
        if mode not in valid_modes:
            return False
        
        return self.update_player(player_id, {"offline_mode": mode})
    
    def add_action_to_history(self, player_id: str, action: str, details: Dict = None) -> bool:
        """Add action to player's history"""
        player = self.get_player(player_id)
        if not player:
            return False
        
        from utils.helpers import add_action_to_history, truncate_action_history
        
        action_data = add_action_to_history(player_id, action, details)
        new_actions = player.get('last_actions', []) + [action_data]
        new_actions = truncate_action_history(new_actions)
        
        return self.update_player(player_id, {"last_actions": new_actions})
    
    def get_player_class_bonus(self, player_id: str, bonus_type: str) -> float:
        """Get player's class bonus for specific type"""
        player = self.get_player(player_id)
        if not player:
            return 1.0
        
        char_class = self.get_character_class(player.get('class', ''))
        if not char_class:
            return 1.0
        
        return char_class.bonuses.get(bonus_type, 1.0)
    
    def is_player_alive(self, player_id: str) -> bool:
        """Check if player is alive"""
        player = self.get_player(player_id)
        return player and player.get('status') == 'alive'
    
    def can_player_act(self, player_id: str, action: str) -> bool:
        """Check if player can perform an action (cooldowns, status, etc.)"""
        player = self.get_player(player_id)
        if not player or not self.is_player_alive(player_id):
            return False
        
        from utils.helpers import is_action_available
        return is_action_available(player_id, action, player.get('last_actions', []))

# Global player system instance
player_system = PlayerSystem()