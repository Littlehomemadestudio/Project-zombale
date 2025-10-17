"""
World manager for BalletBot: Outbreak Dominion
Manages world state, regions, and buildings
"""

import logging
from typing import Dict, List, Optional, Any
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp
from config import WORLD_REGIONS, BUILDING_FLOORS

logger = logging.getLogger(__name__)

class WorldManager:
    """Manages world state and regions"""
    
    def __init__(self):
        self.regions: Dict[str, Dict] = {}
        self.buildings: Dict[str, Dict] = {}
        self.active_games: Dict[str, Dict] = {}
    
    async def initialize(self):
        """Initialize world manager"""
        try:
            # Load regions
            self.regions = file_manager.get_all_regions()
            
            # If no regions exist, create default ones
            if not self.regions:
                await self._create_default_regions()
            
            # Load buildings
            self.buildings = file_manager.get_all_buildings()
            
            logger.info(f"World manager initialized with {len(self.regions)} regions and {len(self.buildings)} buildings")
            
        except Exception as e:
            logger.error(f"Error initializing world manager: {e}")
            raise
    
    async def _create_default_regions(self):
        """Create default world regions"""
        try:
            for region_name, region_data in WORLD_REGIONS.items():
                # Add timestamp
                region_data["last_updated"] = get_current_timestamp()
                
                # Save to file
                file_manager.save_region(region_name, region_data)
                self.regions[region_name] = region_data
            
            logger.info(f"Created {len(WORLD_REGIONS)} default regions")
            
        except Exception as e:
            logger.error(f"Error creating default regions: {e}")
            raise
    
    def get_region(self, region_name: str) -> Optional[Dict]:
        """Get region data"""
        return self.regions.get(region_name)
    
    def get_all_regions(self) -> Dict[str, Dict]:
        """Get all regions"""
        return self.regions.copy()
    
    def get_connected_regions(self, region_name: str) -> List[str]:
        """Get connected regions"""
        region = self.get_region(region_name)
        if not region:
            return []
        
        return region.get("connected", [])
    
    def update_region_zombies(self, region_name: str, change: int):
        """Update zombie count in region"""
        try:
            region = self.get_region(region_name)
            if not region:
                return
            
            current_zombies = region.get("zombies", 0)
            new_count = max(0, current_zombies + change)
            region["zombies"] = new_count
            region["last_updated"] = get_current_timestamp()
            
            # Save to file
            file_manager.save_region(region_name, region)
            
            logger.debug(f"Updated {region_name} zombies: {current_zombies} -> {new_count}")
            
        except Exception as e:
            logger.error(f"Error updating region zombies: {e}")
    
    def get_region_zombie_count(self, region_name: str) -> int:
        """Get zombie count in region"""
        region = self.get_region(region_name)
        if not region:
            return 0
        
        return region.get("zombies", 0)
    
    def get_building(self, building_id: str) -> Optional[Dict]:
        """Get building data"""
        return self.buildings.get(building_id)
    
    def create_building(self, building_id: str, building_data: Dict):
        """Create a new building"""
        try:
            building_data["created_at"] = get_current_timestamp()
            building_data["last_updated"] = get_current_timestamp()
            
            file_manager.save_building(building_id, building_data)
            self.buildings[building_id] = building_data
            
            logger.info(f"Created building {building_id}")
            
        except Exception as e:
            logger.error(f"Error creating building {building_id}: {e}")
    
    def update_building(self, building_id: str, updates: Dict):
        """Update building data"""
        try:
            building = self.buildings.get(building_id)
            if not building:
                return
            
            building.update(updates)
            building["last_updated"] = get_current_timestamp()
            
            file_manager.save_building(building_id, building)
            
        except Exception as e:
            logger.error(f"Error updating building {building_id}: {e}")
    
    def get_buildings_in_region(self, region_name: str) -> List[Dict]:
        """Get all buildings in a region"""
        buildings = []
        
        for building_id, building_data in self.buildings.items():
            if building_data.get("region") == region_name:
                buildings.append(building_data)
        
        return buildings
    
    def get_world_status(self) -> Dict[str, Any]:
        """Get world status summary"""
        try:
            total_zombies = sum(region.get("zombies", 0) for region in self.regions.values())
            total_buildings = len(self.buildings)
            active_games = len(self.active_games)
            
            return {
                "total_regions": len(self.regions),
                "total_zombies": total_zombies,
                "total_buildings": total_buildings,
                "active_games": active_games,
                "regions": {
                    name: {
                        "zombies": region.get("zombies", 0),
                        "danger": region.get("danger", 0),
                        "type": region.get("type", "unknown")
                    }
                    for name, region in self.regions.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting world status: {e}")
            return {
                "total_regions": 0,
                "total_zombies": 0,
                "total_buildings": 0,
                "active_games": 0,
                "regions": {}
            }
    
    def create_game(self, game_code: str) -> bool:
        """Create a new game"""
        try:
            if game_code in self.active_games:
                return False
            
            self.active_games[game_code] = {
                "code": game_code,
                "created_at": get_current_timestamp(),
                "players": [],
                "status": "active"
            }
            
            logger.info(f"Created game {game_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating game {game_code}: {e}")
            return False
    
    def join_game(self, game_code: str, player_id: str) -> bool:
        """Join a game"""
        try:
            if game_code not in self.active_games:
                return False
            
            if player_id not in self.active_games[game_code]["players"]:
                self.active_games[game_code]["players"].append(player_id)
                logger.info(f"Player {player_id} joined game {game_code}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error joining game {game_code}: {e}")
            return False
    
    def get_game(self, game_code: str) -> Optional[Dict]:
        """Get game data"""
        return self.active_games.get(game_code)
    
    def get_all_games(self) -> Dict[str, Dict]:
        """Get all active games"""
        return self.active_games.copy()
    
    def format_world_status(self) -> str:
        """Format world status for display"""
        try:
            status = self.get_world_status()
            
            display = "🌍 **World Status**\n\n"
            display += f"Regions: {status['total_regions']}\n"
            display += f"Zombies: {status['total_zombies']}\n"
            display += f"Buildings: {status['total_buildings']}\n"
            display += f"Active Games: {status['active_games']}\n\n"
            
            display += "**Regions:**\n"
            for name, region in status['regions'].items():
                display += f"• {name}: {region['zombies']} zombies, {region['danger']}% danger\n"
            
            return display
            
        except Exception as e:
            logger.error(f"Error formatting world status: {e}")
            return "❌ Error getting world status"
    
    def get_region_info(self, region_name: str) -> str:
        """Get formatted region information"""
        try:
            region = self.get_region(region_name)
            if not region:
                return f"❌ Region {region_name} not found"
            
            display = f"🏞️ **{region_name}**\n\n"
            display += f"Type: {region.get('type', 'Unknown')}\n"
            display += f"Danger: {region.get('danger', 0)}%\n"
            display += f"Zombies: {region.get('zombies', 0)}\n"
            display += f"Connected: {', '.join(region.get('connected', []))}\n"
            
            # Get buildings in region
            buildings = self.get_buildings_in_region(region_name)
            if buildings:
                display += f"\nBuildings: {', '.join([b['name'] for b in buildings])}\n"
            
            return display
            
        except Exception as e:
            logger.error(f"Error getting region info: {e}")
            return f"❌ Error getting region info for {region_name}"

# Global world manager instance
world_manager = WorldManager()