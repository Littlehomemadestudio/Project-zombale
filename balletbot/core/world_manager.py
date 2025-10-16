"""
World manager for BalletBot: Outbreak Dominion
Handles world state, regions, buildings, and global game state
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from utils.db import db, log_event
from utils.helpers import get_current_timestamp, parse_location, format_location
from config import REGION_TYPES, MAP_OVERVIEW_PATH, MAP_DETAILED_PATH

logger = logging.getLogger(__name__)

class WorldManager:
    """Manages world state, regions, and buildings"""
    
    def __init__(self):
        self.regions: Dict[str, Dict] = {}
        self.buildings: Dict[str, Dict] = {}
        self.active_games: Dict[str, Dict] = {}
        self._initialize_world()
    
    def _initialize_world(self):
        """Initialize world regions and buildings"""
        self._create_default_regions()
        self._create_default_buildings()
        self._load_world_data()
    
    def _create_default_regions(self):
        """Create default world regions"""
        default_regions = [
            {
                "name": "Forest",
                "type": "forest",
                "danger": 20,
                "zombies": 0,
                "connected": ["Urban", "Coast"],
                "buildings": ["Camp", "Cabin"],
                "properties": {"resources": ["wood", "herbs"], "weather": "normal"}
            },
            {
                "name": "Urban",
                "type": "urban", 
                "danger": 60,
                "zombies": 0,
                "connected": ["Forest", "Military", "Downtown"],
                "buildings": ["Hospital", "Police Station", "Store"],
                "properties": {"resources": ["metal", "circuit", "cloth"], "weather": "normal"}
            },
            {
                "name": "Downtown",
                "type": "urban",
                "danger": 70,
                "zombies": 0,
                "connected": ["Urban", "Military"],
                "buildings": ["Office Building", "Shopping Mall", "Apartment Complex"],
                "properties": {"resources": ["metal", "circuit", "cloth", "fuel"], "weather": "normal"}
            },
            {
                "name": "Military",
                "type": "military",
                "danger": 80,
                "zombies": 0,
                "connected": ["Urban", "Downtown", "Coast"],
                "buildings": ["Bunker", "Armory", "Command Center"],
                "properties": {"resources": ["ammo", "weapon_parts", "fuel"], "weather": "normal"}
            },
            {
                "name": "Coast",
                "type": "coast",
                "danger": 40,
                "zombies": 0,
                "connected": ["Forest", "Military"],
                "buildings": ["Lighthouse", "Harbor", "Research Station"],
                "properties": {"resources": ["fish", "salt", "fuel"], "weather": "normal"}
            }
        ]
        
        for region_data in default_regions:
            self._create_region(region_data)
    
    def _create_region(self, region_data: Dict[str, Any]):
        """Create a region in the database"""
        try:
            db.execute_update("""
                INSERT OR REPLACE INTO world_regions 
                (name, type, danger, zombies, connected, buildings, properties)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                region_data["name"],
                region_data["type"],
                region_data["danger"],
                region_data["zombies"],
                json.dumps(region_data["connected"]),
                json.dumps(region_data["buildings"]),
                json.dumps(region_data["properties"])
            ))
            
            self.regions[region_data["name"]] = region_data
            logger.info(f"Created region: {region_data['name']}")
            
        except Exception as e:
            logger.error(f"Failed to create region {region_data['name']}: {e}")
    
    def _create_default_buildings(self):
        """Create default buildings"""
        default_buildings = [
            {
                "id": "Forest:Camp",
                "region": "Forest",
                "name": "Camp",
                "floors": [
                    {"floor": 1, "difficulty": 10, "zombies": 0, "loot_table": "camp_floor_1"},
                    {"floor": 2, "difficulty": 15, "zombies": 1, "loot_table": "camp_floor_2"}
                ],
                "cleared_by": {},
                "last_checked": 0
            },
            {
                "id": "Urban:Hospital",
                "region": "Urban", 
                "name": "Hospital",
                "floors": [
                    {"floor": 1, "difficulty": 30, "zombies": 2, "loot_table": "hospital_floor_1"},
                    {"floor": 2, "difficulty": 40, "zombies": 3, "loot_table": "hospital_floor_2"},
                    {"floor": 3, "difficulty": 50, "zombies": 4, "loot_table": "hospital_floor_3"},
                    {"floor": 4, "difficulty": 60, "zombies": 5, "loot_table": "hospital_floor_4"}
                ],
                "cleared_by": {},
                "last_checked": 0
            },
            {
                "id": "Military:Bunker",
                "region": "Military",
                "name": "Bunker", 
                "floors": [
                    {"floor": 1, "difficulty": 70, "zombies": 6, "loot_table": "bunker_floor_1"},
                    {"floor": 2, "difficulty": 80, "zombies": 8, "loot_table": "bunker_floor_2"},
                    {"floor": 3, "difficulty": 90, "zombies": 10, "loot_table": "bunker_floor_3"}
                ],
                "cleared_by": {},
                "last_checked": 0
            }
        ]
        
        for building_data in default_buildings:
            self._create_building(building_data)
    
    def _create_building(self, building_data: Dict[str, Any]):
        """Create a building in the database"""
        try:
            db.execute_update("""
                INSERT OR REPLACE INTO buildings 
                (id, region, name, floors, cleared_by, last_checked)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                building_data["id"],
                building_data["region"],
                building_data["name"],
                json.dumps(building_data["floors"]),
                json.dumps(building_data["cleared_by"]),
                building_data["last_checked"]
            ))
            
            self.buildings[building_data["id"]] = building_data
            logger.info(f"Created building: {building_data['name']} in {building_data['region']}")
            
        except Exception as e:
            logger.error(f"Failed to create building {building_data['id']}: {e}")
    
    def _load_world_data(self):
        """Load world data from database"""
        # Load regions
        regions = db.execute_query("SELECT * FROM world_regions")
        for region in regions:
            region['connected'] = json.loads(region['connected'])
            region['buildings'] = json.loads(region['buildings'])
            region['properties'] = json.loads(region['properties'])
            self.regions[region['name']] = region
        
        # Load buildings
        buildings = db.execute_query("SELECT * FROM buildings")
        for building in buildings:
            building['floors'] = json.loads(building['floors'])
            building['cleared_by'] = json.loads(building['cleared_by'])
            self.buildings[building['id']] = building
    
    async def initialize(self):
        """Initialize world manager"""
        logger.info("Initializing world manager...")
        self._load_world_data()
        logger.info(f"Loaded {len(self.regions)} regions and {len(self.buildings)} buildings")
    
    def get_region(self, region_name: str) -> Optional[Dict[str, Any]]:
        """Get region by name"""
        return self.regions.get(region_name)
    
    def get_building(self, building_id: str) -> Optional[Dict[str, Any]]:
        """Get building by ID"""
        return self.buildings.get(building_id)
    
    def get_connected_regions(self, region_name: str) -> List[str]:
        """Get list of connected regions"""
        region = self.get_region(region_name)
        if not region:
            return []
        return region.get('connected', [])
    
    def can_move_to_region(self, from_region: str, to_region: str) -> bool:
        """Check if player can move from one region to another"""
        connected = self.get_connected_regions(from_region)
        return to_region in connected
    
    def get_region_buildings(self, region_name: str) -> List[Dict[str, Any]]:
        """Get all buildings in a region"""
        region = self.get_region(region_name)
        if not region:
            return []
        
        building_names = region.get('buildings', [])
        buildings = []
        
        for building_name in building_names:
            building_id = f"{region_name}:{building_name}"
            building = self.get_building(building_id)
            if building:
                buildings.append(building)
        
        return buildings
    
    def get_building_floors(self, building_id: str) -> List[Dict[str, Any]]:
        """Get all floors in a building"""
        building = self.get_building(building_id)
        if not building:
            return []
        
        return building.get('floors', [])
    
    def get_floor_info(self, building_id: str, floor_number: int) -> Optional[Dict[str, Any]]:
        """Get specific floor information"""
        floors = self.get_building_floors(building_id)
        for floor in floors:
            if floor.get('floor') == floor_number:
                return floor
        return None
    
    def is_floor_cleared(self, building_id: str, floor_number: int, player_id: str) -> bool:
        """Check if floor is cleared by player"""
        building = self.get_building(building_id)
        if not building:
            return False
        
        cleared_by = building.get('cleared_by', {})
        return str(floor_number) in cleared_by and player_id in cleared_by[str(floor_number)]
    
    def mark_floor_cleared(self, building_id: str, floor_number: int, player_id: str):
        """Mark floor as cleared by player"""
        building = self.get_building(building_id)
        if not building:
            return
        
        cleared_by = building.get('cleared_by', {})
        floor_key = str(floor_number)
        
        if floor_key not in cleared_by:
            cleared_by[floor_key] = []
        
        if player_id not in cleared_by[floor_key]:
            cleared_by[floor_key].append(player_id)
        
        # Update database
        db.execute_update(
            "UPDATE buildings SET cleared_by = ? WHERE id = ?",
            (json.dumps(cleared_by), building_id)
        )
        
        # Update cache
        building['cleared_by'] = cleared_by
        
        log_event("floor_cleared", {
            "building_id": building_id,
            "floor": floor_number,
            "player_id": player_id
        })
    
    def get_region_danger_level(self, region_name: str) -> int:
        """Get region danger level"""
        region = self.get_region(region_name)
        if not region:
            return 0
        return region.get('danger', 0)
    
    def get_region_zombie_count(self, region_name: str) -> int:
        """Get current zombie count in region"""
        region = self.get_region(region_name)
        if not region:
            return 0
        return region.get('zombies', 0)
    
    def update_region_zombies(self, region_name: str, zombie_change: int):
        """Update zombie count in region"""
        region = self.get_region(region_name)
        if not region:
            return
        
        new_count = max(0, region.get('zombies', 0) + zombie_change)
        
        # Update database
        db.execute_update(
            "UPDATE world_regions SET zombies = ? WHERE name = ?",
            (new_count, region_name)
        )
        
        # Update cache
        region['zombies'] = new_count
        
        log_event("zombie_count_changed", {
            "region": region_name,
            "old_count": region.get('zombies', 0),
            "new_count": new_count,
            "change": zombie_change
        })
    
    def get_map_overview_path(self) -> str:
        """Get path to map overview image"""
        return MAP_OVERVIEW_PATH
    
    def get_map_detailed_path(self) -> str:
        """Get path to detailed map image"""
        return MAP_DETAILED_PATH
    
    def create_game(self, group_code: str, admin_id: str) -> Dict[str, Any]:
        """Create a new game session"""
        game_data = {
            "group_code": group_code,
            "admin_id": admin_id,
            "created_at": get_current_timestamp(),
            "status": "active",
            "settings": {
                "time_multiplier": 1.0,
                "day_length": 1800,
                "world_tick": 30
            }
        }
        
        self.active_games[group_code] = game_data
        
        log_event("game_created", game_data)
        
        return game_data
    
    def get_game(self, group_code: str) -> Optional[Dict[str, Any]]:
        """Get game by group code"""
        return self.active_games.get(group_code)
    
    def get_all_games(self) -> List[Dict[str, Any]]:
        """Get all active games"""
        return list(self.active_games.values())
    
    def end_game(self, group_code: str):
        """End a game session"""
        if group_code in self.active_games:
            del self.active_games[group_code]
            log_event("game_ended", {"group_code": group_code})
    
    def get_world_status(self) -> Dict[str, Any]:
        """Get overall world status"""
        total_zombies = sum(region.get('zombies', 0) for region in self.regions.values())
        active_games = len(self.active_games)
        
        return {
            "total_regions": len(self.regions),
            "total_buildings": len(self.buildings),
            "total_zombies": total_zombies,
            "active_games": active_games,
            "regions": list(self.regions.keys())
        }

# Global world manager instance
world_manager = WorldManager()