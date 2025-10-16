"""
Player system for BalletBot: Outbreak Dominion
Manages player data and character classes
"""

import logging
from typing import Dict, List, Optional, Any
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp, generate_game_code, is_valid_username, is_valid_class
from config import CLASS_BONUSES, DEFAULT_HP, DEFAULT_STAMINA, DEFAULT_HUNGER, DEFAULT_INFECTION, DEFAULT_INTELLIGENCE, DEFAULT_LOCATION

logger = logging.getLogger(__name__)

class PlayerSystem:
    """Manages player data and character classes"""
    
    def __init__(self):
        self.active_games: Dict[str, Dict] = {}  # game_code -> game_data
        self.player_cooldowns: Dict[str, Dict[str, int]] = {}  # player_id -> {action: timestamp}
    
    def create_character(self, user_id: str, username: str, char_class: str, game_code: str) -> Dict[str, Any]:
        """Create a new character"""
        try:
            # Validate inputs
            if not is_valid_username(username):
                return {"success": False, "error": "Invalid username. Use 2-20 characters, letters, numbers, and -_ only."}
            
            if not is_valid_class(char_class):
                return {"success": False, "error": "Invalid class. Choose: Scavenger, Mechanic, or Soldier."}
            
            # Check if player already exists
            if file_manager.get_player(user_id):
                return {"success": False, "error": "Character already exists. Use /status to view your character."}
            
            # Create player data
            player_data = {
                "id": user_id,
                "username": username,
                "group_code": game_code,
                "class": char_class,
                "hp": DEFAULT_HP,
                "stamina": DEFAULT_STAMINA,
                "hunger": DEFAULT_HUNGER,
                "infection": DEFAULT_INFECTION,
                "intelligence": DEFAULT_INTELLIGENCE,
                "location": DEFAULT_LOCATION,
                "shelter_id": None,
                "status": "alive",
                "offline_mode": "none",
                "last_active": get_current_timestamp(),
                "last_actions": [],
                "created_at": get_current_timestamp()
            }
            
            # Save player
            file_manager.save_player(user_id, player_data)
            
            # Give starter items
            self._give_starter_items(user_id)
            
            # Add to active game
            if game_code not in self.active_games:
                self.active_games[game_code] = {
                    "code": game_code,
                    "created_at": get_current_timestamp(),
                    "players": []
                }
            
            self.active_games[game_code]["players"].append(user_id)
            
            logger.info(f"Created character {username} ({char_class}) for user {user_id}")
            
            return {
                "success": True,
                "message": f"Character created! Welcome {username} the {char_class}.",
                "player_data": player_data
            }
            
        except Exception as e:
            logger.error(f"Error creating character: {e}")
            return {"success": False, "error": "Failed to create character. Please try again."}
    
    def _give_starter_items(self, user_id: str):
        """Give starter items to new player"""
        starter_items = {
            "knife": 1,
            "small_backpack": 1,
            "basic_rations": 3,
            "water": 2
        }
        
        for item_id, quantity in starter_items.items():
            file_manager.add_item_to_inventory(user_id, item_id, quantity)
    
    def get_player(self, user_id: str) -> Optional[Dict]:
        """Get player data"""
        return file_manager.get_player(user_id)
    
    def update_player(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update player data"""
        try:
            player_data = file_manager.get_player(user_id)
            if not player_data:
                return False
            
            player_data.update(updates)
            player_data["last_active"] = get_current_timestamp()
            
            file_manager.save_player(user_id, player_data)
            return True
            
        except Exception as e:
            logger.error(f"Error updating player {user_id}: {e}")
            return False
    
    def move_player(self, user_id: str, new_location: str) -> bool:
        """Move player to new location"""
        try:
            player_data = file_manager.get_player(user_id)
            if not player_data:
                return False
            
            old_location = player_data.get("location", "")
            player_data["location"] = new_location
            player_data["last_active"] = get_current_timestamp()
            
            file_manager.save_player(user_id, player_data)
            
            # Add to action history
            from utils.helpers import add_action_to_history
            add_action_to_history(user_id, "move", from_location=old_location, to_location=new_location)
            
            return True
            
        except Exception as e:
            logger.error(f"Error moving player {user_id}: {e}")
            return False
    
    def update_hp(self, user_id: str, hp_change: int) -> bool:
        """Update player HP"""
        try:
            player_data = file_manager.get_player(user_id)
            if not player_data:
                return False
            
            current_hp = player_data.get("hp", DEFAULT_HP)
            new_hp = max(0, min(100, current_hp + hp_change))
            
            player_data["hp"] = new_hp
            player_data["last_active"] = get_current_timestamp()
            
            # Check for death
            if new_hp <= 0:
                player_data["status"] = "dead"
                logger.info(f"Player {user_id} died")
            
            file_manager.save_player(user_id, player_data)
            return True
            
        except Exception as e:
            logger.error(f"Error updating HP for player {user_id}: {e}")
            return False
    
    def update_stamina(self, user_id: str, stamina_change: int) -> bool:
        """Update player stamina"""
        try:
            player_data = file_manager.get_player(user_id)
            if not player_data:
                return False
            
            current_stamina = player_data.get("stamina", DEFAULT_STAMINA)
            new_stamina = max(0, min(100, current_stamina + stamina_change))
            
            player_data["stamina"] = new_stamina
            player_data["last_active"] = get_current_timestamp()
            
            file_manager.save_player(user_id, player_data)
            return True
            
        except Exception as e:
            logger.error(f"Error updating stamina for player {user_id}: {e}")
            return False
    
    def update_hunger(self, user_id: str, hunger_change: int) -> bool:
        """Update player hunger"""
        try:
            player_data = file_manager.get_player(user_id)
            if not player_data:
                return False
            
            current_hunger = player_data.get("hunger", DEFAULT_HUNGER)
            new_hunger = max(0, min(100, current_hunger + hunger_change))
            
            player_data["hunger"] = new_hunger
            player_data["last_active"] = get_current_timestamp()
            
            file_manager.save_player(user_id, player_data)
            return True
            
        except Exception as e:
            logger.error(f"Error updating hunger for player {user_id}: {e}")
            return False
    
    def update_infection(self, user_id: str, infection_change: int) -> bool:
        """Update player infection"""
        try:
            player_data = file_manager.get_player(user_id)
            if not player_data:
                return False
            
            current_infection = player_data.get("infection", DEFAULT_INFECTION)
            new_infection = max(0, min(100, current_infection + infection_change))
            
            player_data["infection"] = new_infection
            player_data["last_active"] = get_current_timestamp()
            
            # Check for zombie conversion
            if new_infection >= 100:
                player_data["status"] = "zombie"
                logger.info(f"Player {user_id} became a zombie")
            
            file_manager.save_player(user_id, player_data)
            return True
            
        except Exception as e:
            logger.error(f"Error updating infection for player {user_id}: {e}")
            return False
    
    def update_intelligence(self, user_id: str, intelligence_change: int) -> bool:
        """Update player intelligence"""
        try:
            player_data = file_manager.get_player(user_id)
            if not player_data:
                return False
            
            current_intelligence = player_data.get("intelligence", DEFAULT_INTELLIGENCE)
            new_intelligence = max(0, current_intelligence + intelligence_change)
            
            player_data["intelligence"] = new_intelligence
            player_data["last_active"] = get_current_timestamp()
            
            file_manager.save_player(user_id, player_data)
            return True
            
        except Exception as e:
            logger.error(f"Error updating intelligence for player {user_id}: {e}")
            return False
    
    def set_offline_mode(self, user_id: str, mode: str) -> bool:
        """Set player offline mode"""
        try:
            valid_modes = ["none", "ambush", "scavenge"]
            if mode not in valid_modes:
                return False
            
            player_data = file_manager.get_player(user_id)
            if not player_data:
                return False
            
            player_data["offline_mode"] = mode
            player_data["last_active"] = get_current_timestamp()
            
            file_manager.save_player(user_id, player_data)
            return True
            
        except Exception as e:
            logger.error(f"Error setting offline mode for player {user_id}: {e}")
            return False
    
    def get_player_status(self, user_id: str) -> Optional[str]:
        """Get formatted player status"""
        try:
            player_data = file_manager.get_player(user_id)
            if not player_data:
                return None
            
            from utils.helpers import format_player_status
            return format_player_status(player_data)
            
        except Exception as e:
            logger.error(f"Error getting player status for {user_id}: {e}")
            return None
    
    def get_class_bonuses(self, char_class: str) -> Dict[str, Any]:
        """Get character class bonuses"""
        return CLASS_BONUSES.get(char_class, {})
    
    def check_cooldown(self, user_id: str, action: str) -> bool:
        """Check if player can perform action (cooldown)"""
        try:
            from config import ACTION_COOLDOWNS
            
            if user_id not in self.player_cooldowns:
                self.player_cooldowns[user_id] = {}
            
            cooldown_duration = ACTION_COOLDOWNS.get(action, 0)
            if cooldown_duration == 0:
                return True
            
            last_used = self.player_cooldowns[user_id].get(action, 0)
            current_time = get_current_timestamp()
            
            return (current_time - last_used) >= cooldown_duration
            
        except Exception as e:
            logger.error(f"Error checking cooldown for player {user_id}: {e}")
            return False
    
    def set_cooldown(self, user_id: str, action: str):
        """Set cooldown for player action"""
        try:
            if user_id not in self.player_cooldowns:
                self.player_cooldowns[user_id] = {}
            
            self.player_cooldowns[user_id][action] = get_current_timestamp()
            
        except Exception as e:
            logger.error(f"Error setting cooldown for player {user_id}: {e}")
    
    def get_players_in_region(self, region: str) -> List[Dict]:
        """Get all players in a specific region"""
        try:
            all_players = file_manager.get_all_players()
            players_in_region = []
            
            for player_data in all_players.values():
                location = player_data.get("location", "")
                if location.startswith(region + ":"):
                    players_in_region.append(player_data)
            
            return players_in_region
            
        except Exception as e:
            logger.error(f"Error getting players in region {region}: {e}")
            return []
    
    def get_players_by_game(self, game_code: str) -> List[Dict]:
        """Get all players in a specific game"""
        try:
            all_players = file_manager.get_all_players()
            game_players = []
            
            for player_data in all_players.values():
                if player_data.get("group_code") == game_code:
                    game_players.append(player_data)
            
            return game_players
            
        except Exception as e:
            logger.error(f"Error getting players for game {game_code}: {e}")
            return []
    
    def create_game(self, game_code: str = None) -> str:
        """Create a new game"""
        try:
            if not game_code:
                game_code = generate_game_code()
            
            self.active_games[game_code] = {
                "code": game_code,
                "created_at": get_current_timestamp(),
                "players": []
            }
            
            logger.info(f"Created new game: {game_code}")
            return game_code
            
        except Exception as e:
            logger.error(f"Error creating game: {e}")
            return None
    
    def join_game(self, user_id: str, game_code: str) -> bool:
        """Join a game"""
        try:
            if game_code not in self.active_games:
                return False
            
            self.active_games[game_code]["players"].append(user_id)
            return True
            
        except Exception as e:
            logger.error(f"Error joining game {game_code}: {e}")
            return False

# Global player system instance
player_system = PlayerSystem()