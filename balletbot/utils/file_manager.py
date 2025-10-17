"""
File-based data management for BalletBot: Outbreak Dominion
Replaces database with text file storage
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class FileManager:
    """Manages data persistence using text files"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize data structures
        self.players: Dict[str, Dict] = {}
        self.inventories: Dict[str, Dict[str, int]] = {}
        self.world_regions: Dict[str, Dict] = {}
        self.buildings: Dict[str, Dict] = {}
        self.vehicles: Dict[str, Dict] = {}
        self.pending_actions: List[Dict] = []
        self.construction: List[Dict] = []
        self.events: List[Dict] = []
        self.logs: List[Dict] = {}
        
        # Load all data
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all data from files"""
        self._load_players()
        self._load_inventories()
        self._load_world_regions()
        self._load_buildings()
        self._load_vehicles()
        self._load_pending_actions()
        self._load_construction()
        self._load_events()
        self._load_logs()
    
    def _load_players(self):
        """Load players from file"""
        file_path = self.data_dir / "players.txt"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.players = json.load(f)
            except Exception as e:
                logger.error(f"Error loading players: {e}")
                self.players = {}
        else:
            self.players = {}
    
    def _save_players(self):
        """Save players to file"""
        file_path = self.data_dir / "players.txt"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.players, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving players: {e}")
    
    def _load_inventories(self):
        """Load inventories from file"""
        file_path = self.data_dir / "inventories.txt"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.inventories = json.load(f)
            except Exception as e:
                logger.error(f"Error loading inventories: {e}")
                self.inventories = {}
        else:
            self.inventories = {}
    
    def _save_inventories(self):
        """Save inventories to file"""
        file_path = self.data_dir / "inventories.txt"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.inventories, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving inventories: {e}")
    
    def _load_world_regions(self):
        """Load world regions from file"""
        file_path = self.data_dir / "world.txt"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.world_regions = json.load(f)
            except Exception as e:
                logger.error(f"Error loading world regions: {e}")
                self.world_regions = {}
        else:
            self.world_regions = {}
    
    def _save_world_regions(self):
        """Save world regions to file"""
        file_path = self.data_dir / "world.txt"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.world_regions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving world regions: {e}")
    
    def _load_buildings(self):
        """Load buildings from file"""
        file_path = self.data_dir / "buildings.txt"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.buildings = json.load(f)
            except Exception as e:
                logger.error(f"Error loading buildings: {e}")
                self.buildings = {}
        else:
            self.buildings = {}
    
    def _save_buildings(self):
        """Save buildings to file"""
        file_path = self.data_dir / "buildings.txt"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.buildings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving buildings: {e}")
    
    def _load_vehicles(self):
        """Load vehicles from file"""
        file_path = self.data_dir / "vehicles.txt"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.vehicles = json.load(f)
            except Exception as e:
                logger.error(f"Error loading vehicles: {e}")
                self.vehicles = {}
        else:
            self.vehicles = {}
    
    def _save_vehicles(self):
        """Save vehicles to file"""
        file_path = self.data_dir / "vehicles.txt"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.vehicles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving vehicles: {e}")
    
    def _load_pending_actions(self):
        """Load pending actions from file"""
        file_path = self.data_dir / "pending_actions.txt"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.pending_actions = json.load(f)
            except Exception as e:
                logger.error(f"Error loading pending actions: {e}")
                self.pending_actions = []
        else:
            self.pending_actions = []
    
    def _save_pending_actions(self):
        """Save pending actions to file"""
        file_path = self.data_dir / "pending_actions.txt"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.pending_actions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving pending actions: {e}")
    
    def _load_construction(self):
        """Load construction from file"""
        file_path = self.data_dir / "construction.txt"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.construction = json.load(f)
            except Exception as e:
                logger.error(f"Error loading construction: {e}")
                self.construction = []
        else:
            self.construction = []
    
    def _save_construction(self):
        """Save construction to file"""
        file_path = self.data_dir / "construction.txt"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.construction, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving construction: {e}")
    
    def _load_events(self):
        """Load events from file"""
        file_path = self.data_dir / "events.txt"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.events = json.load(f)
            except Exception as e:
                logger.error(f"Error loading events: {e}")
                self.events = []
        else:
            self.events = []
    
    def _save_events(self):
        """Save events to file"""
        file_path = self.data_dir / "events.txt"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving events: {e}")
    
    def _load_logs(self):
        """Load logs from file"""
        file_path = self.data_dir / "logs.txt"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.logs = json.load(f)
            except Exception as e:
                logger.error(f"Error loading logs: {e}")
                self.logs = {}
        else:
            self.logs = {}
    
    def _save_logs(self):
        """Save logs to file"""
        file_path = self.data_dir / "logs.txt"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving logs: {e}")
    
    # Player operations
    def get_player(self, player_id: str) -> Optional[Dict]:
        """Get player data"""
        return self.players.get(player_id)
    
    def save_player(self, player_id: str, player_data: Dict):
        """Save player data"""
        self.players[player_id] = player_data
        self._save_players()
    
    def delete_player(self, player_id: str):
        """Delete player"""
        if player_id in self.players:
            del self.players[player_id]
            self._save_players()
    
    def get_all_players(self) -> Dict[str, Dict]:
        """Get all players"""
        return self.players.copy()
    
    # Inventory operations
    def get_player_inventory(self, player_id: str) -> Dict[str, int]:
        """Get player inventory"""
        return self.inventories.get(player_id, {})
    
    def save_player_inventory(self, player_id: str, inventory: Dict[str, int]):
        """Save player inventory"""
        self.inventories[player_id] = inventory
        self._save_inventories()
    
    def add_item_to_inventory(self, player_id: str, item_id: str, quantity: int):
        """Add item to inventory"""
        if player_id not in self.inventories:
            self.inventories[player_id] = {}
        
        current_qty = self.inventories[player_id].get(item_id, 0)
        self.inventories[player_id][item_id] = current_qty + quantity
        self._save_inventories()
    
    def remove_item_from_inventory(self, player_id: str, item_id: str, quantity: int) -> bool:
        """Remove item from inventory"""
        if player_id not in self.inventories:
            return False
        
        current_qty = self.inventories[player_id].get(item_id, 0)
        if current_qty < quantity:
            return False
        
        self.inventories[player_id][item_id] = current_qty - quantity
        if self.inventories[player_id][item_id] <= 0:
            del self.inventories[player_id][item_id]
        
        self._save_inventories()
        return True
    
    def has_item(self, player_id: str, item_id: str, quantity: int = 1) -> bool:
        """Check if player has item"""
        if player_id not in self.inventories:
            return False
        
        return self.inventories[player_id].get(item_id, 0) >= quantity
    
    # World operations
    def get_region(self, region_name: str) -> Optional[Dict]:
        """Get region data"""
        return self.world_regions.get(region_name)
    
    def save_region(self, region_name: str, region_data: Dict):
        """Save region data"""
        self.world_regions[region_name] = region_data
        self._save_world_regions()
    
    def get_all_regions(self) -> Dict[str, Dict]:
        """Get all regions"""
        return self.world_regions.copy()
    
    # Building operations
    def get_building(self, building_id: str) -> Optional[Dict]:
        """Get building data"""
        return self.buildings.get(building_id)
    
    def save_building(self, building_id: str, building_data: Dict):
        """Save building data"""
        self.buildings[building_id] = building_data
        self._save_buildings()
    
    def get_all_buildings(self) -> Dict[str, Dict]:
        """Get all buildings"""
        return self.buildings.copy()
    
    # Vehicle operations
    def get_vehicle(self, vehicle_id: str) -> Optional[Dict]:
        """Get vehicle data"""
        return self.vehicles.get(vehicle_id)
    
    def save_vehicle(self, vehicle_id: str, vehicle_data: Dict):
        """Save vehicle data"""
        self.vehicles[vehicle_id] = vehicle_data
        self._save_vehicles()
    
    def delete_vehicle(self, vehicle_id: str):
        """Delete vehicle"""
        if vehicle_id in self.vehicles:
            del self.vehicles[vehicle_id]
            self._save_vehicles()
    
    def get_all_vehicles(self) -> Dict[str, Dict]:
        """Get all vehicles"""
        return self.vehicles.copy()
    
    # Pending actions operations
    def add_pending_action(self, action_data: Dict):
        """Add pending action"""
        self.pending_actions.append(action_data)
        self._save_pending_actions()
    
    def get_pending_actions(self, player_id: str = None) -> List[Dict]:
        """Get pending actions"""
        if player_id:
            return [action for action in self.pending_actions if action.get('player_id') == player_id]
        return self.pending_actions.copy()
    
    def remove_pending_action(self, action_id: str):
        """Remove pending action"""
        self.pending_actions = [action for action in self.pending_actions if action.get('id') != action_id]
        self._save_pending_actions()
    
    def clear_expired_actions(self, current_time: int):
        """Clear expired pending actions"""
        self.pending_actions = [action for action in self.pending_actions if action.get('expire_at', 0) > current_time]
        self._save_pending_actions()
    
    # Construction operations
    def add_construction(self, construction_data: Dict):
        """Add construction project"""
        self.construction.append(construction_data)
        self._save_construction()
    
    def get_construction(self, construction_id: str = None) -> List[Dict]:
        """Get construction projects"""
        if construction_id:
            return [c for c in self.construction if c.get('id') == construction_id]
        return self.construction.copy()
    
    def update_construction(self, construction_id: str, updates: Dict):
        """Update construction project"""
        for i, construction in enumerate(self.construction):
            if construction.get('id') == construction_id:
                self.construction[i].update(updates)
                self._save_construction()
                break
    
    def remove_construction(self, construction_id: str):
        """Remove construction project"""
        self.construction = [c for c in self.construction if c.get('id') != construction_id]
        self._save_construction()
    
    # Event operations
    def add_event(self, event_data: Dict):
        """Add event"""
        self.events.append(event_data)
        self._save_events()
    
    def get_events(self, event_type: str = None, limit: int = 100) -> List[Dict]:
        """Get events"""
        events = self.events.copy()
        if event_type:
            events = [e for e in events if e.get('type') == event_type]
        return events[-limit:] if events else []
    
    # Log operations
    def add_log(self, level: str, message: str, **kwargs):
        """Add log entry"""
        log_entry = {
            "timestamp": kwargs.get('timestamp', 0),
            "level": level,
            "message": message,
            **kwargs
        }
        
        if level not in self.logs:
            self.logs[level] = []
        
        self.logs[level].append(log_entry)
        self._save_logs()
    
    def get_logs(self, level: str = None, limit: int = 100) -> List[Dict]:
        """Get logs"""
        if level:
            return self.logs.get(level, [])[-limit:]
        
        all_logs = []
        for level_logs in self.logs.values():
            all_logs.extend(level_logs)
        
        return sorted(all_logs, key=lambda x: x.get('timestamp', 0))[-limit:]
    
    def save_all(self):
        """Save all data"""
        self._save_players()
        self._save_inventories()
        self._save_world_regions()
        self._save_buildings()
        self._save_vehicles()
        self._save_pending_actions()
        self._save_construction()
        self._save_events()
        self._save_logs()

# Global file manager instance
file_manager = FileManager()