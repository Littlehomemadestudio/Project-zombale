"""
Construction system for BalletBot: Outbreak Dominion
Handles heavy builds like tanks, helicopters, and warships
"""

import logging
from typing import Dict, List, Optional, Any

from utils.helpers import get_current_timestamp
from utils.db import db, log_event
from config import TANK_BUILD_DEFAULT_DAYS, get_scaled_days

logger = logging.getLogger(__name__)

class ConstructionSystem:
    """Manages construction of heavy structures and vehicles"""
    
    def __init__(self):
        self.construction_types = {
            "tank": {
                "name": "Tank",
                "duration_days": TANK_BUILD_DEFAULT_DAYS,
                "resources": {"steel": 50, "engine_parts": 10, "circuit": 5},
                "intelligence_required": 90,
                "location_required": "military_base"
            },
            "helicopter": {
                "name": "Helicopter",
                "duration_days": 10,
                "resources": {"steel": 30, "engine_parts": 8, "circuit": 3, "fuel": 20},
                "intelligence_required": 85,
                "location_required": "military_base"
            },
            "warship": {
                "name": "Warship",
                "duration_days": 21,
                "resources": {"steel": 100, "engine_parts": 20, "circuit": 10, "fuel": 50},
                "intelligence_required": 95,
                "location_required": "coast_base"
            },
            "radio_tower": {
                "name": "Radio Tower",
                "duration_days": 3,
                "resources": {"metal": 20, "circuit": 5, "wood": 10},
                "intelligence_required": 40,
                "location_required": "any"
            },
            "advanced_workshop": {
                "name": "Advanced Workshop",
                "duration_days": 5,
                "resources": {"metal": 30, "circuit": 8, "wood": 15},
                "intelligence_required": 60,
                "location_required": "any"
            }
        }
    
    def start_construction(self, player_id: str, structure_type: str, 
                         location: str) -> Dict[str, Any]:
        """Start construction of a structure"""
        from systems.player_system import player_system
        from systems.inventory_system import inventory_system
        
        # Validate structure type
        if structure_type not in self.construction_types:
            return {"success": False, "error": f"Unknown structure type: {structure_type}"}
        
        structure_info = self.construction_types[structure_type]
        
        # Check player exists
        player = player_system.get_player(player_id)
        if not player:
            return {"success": False, "error": "Player not found"}
        
        # Check intelligence requirement
        if player.get("intelligence", 0) < structure_info["intelligence_required"]:
            return {
                "success": False, 
                "error": f"Insufficient intelligence. Required: {structure_info['intelligence_required']}"
            }
        
        # Check location requirement
        if not self._check_location_requirement(location, structure_info["location_required"]):
            return {
                "success": False,
                "error": f"Invalid location. Required: {structure_info['location_required']}"
            }
        
        # Check resources
        can_afford, missing = inventory_system.can_craft_item(player_id, structure_info)
        if not can_afford:
            return {
                "success": False,
                "error": f"Insufficient resources. Missing: {', '.join(missing)}"
            }
        
        # Consume resources
        if not inventory_system.consume_crafting_materials(player_id, structure_info):
            return {"success": False, "error": "Failed to consume resources"}
        
        # Calculate duration
        duration_seconds = get_scaled_days(structure_info["duration_days"])
        start_time = get_current_timestamp()
        
        # Create construction record
        try:
            cursor = db.execute_update("""
                INSERT INTO construction 
                (owner_id, structure_type, start_time, duration, resources, status, location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                player_id,
                structure_type,
                start_time,
                duration_seconds,
                str(structure_info["resources"]),
                "in_progress",
                location
            ))
            
            # Get construction ID
            result = db.execute_one("SELECT last_insert_rowid() as id")
            construction_id = result['id'] if result else 0
            
            log_event("construction_started", {
                "construction_id": construction_id,
                "player_id": player_id,
                "structure_type": structure_type,
                "location": location,
                "duration_days": structure_info["duration_days"]
            })
            
            return {
                "success": True,
                "construction_id": construction_id,
                "structure_type": structure_type,
                "duration_days": structure_info["duration_days"],
                "completion_time": start_time + duration_seconds
            }
            
        except Exception as e:
            logger.error(f"Failed to start construction: {e}")
            return {"success": False, "error": "Failed to start construction"}
    
    def _check_location_requirement(self, location: str, required: str) -> bool:
        """Check if location meets construction requirements"""
        if required == "any":
            return True
        
        # Parse location to get region
        region = location.split(":")[0] if ":" in location else location
        
        if required == "military_base":
            return region.lower() in ["military", "bunker"]
        elif required == "coast_base":
            return region.lower() in ["coast", "harbor"]
        
        return False
    
    async def complete_construction(self, construction_id: int) -> bool:
        """Complete a construction project"""
        try:
            # Get construction data
            construction = db.execute_one(
                "SELECT * FROM construction WHERE id = ?", (construction_id,)
            )
            
            if not construction:
                return False
            
            structure_type = construction["structure_type"]
            owner_id = construction["owner_id"]
            location = construction["location"]
            
            # Mark as completed
            db.execute_update(
                "UPDATE construction SET status = 'completed' WHERE id = ?",
                (construction_id,)
            )
            
            # Create the structure/vehicle
            if structure_type in ["tank", "helicopter", "warship"]:
                await self._create_vehicle(owner_id, structure_type, location)
            else:
                await self._create_structure(owner_id, structure_type, location)
            
            log_event("construction_completed", {
                "construction_id": construction_id,
                "player_id": owner_id,
                "structure_type": structure_type,
                "location": location
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete construction {construction_id}: {e}")
            return False
    
    async def _create_vehicle(self, owner_id: str, vehicle_type: str, location: str):
        """Create a vehicle from construction"""
        from systems.vehicle_system import vehicle_system
        
        vehicle_id = f"{vehicle_type}_{get_current_timestamp()}_{owner_id}"
        
        vehicle_data = {
            "vehicle_id": vehicle_id,
            "owner_id": owner_id,
            "type": vehicle_type,
            "condition": 100,
            "fuel": 100,
            "storage": 50,
            "location": location,
            "properties": {}
        }
        
        vehicle_system.create_vehicle(vehicle_data)
    
    async def _create_structure(self, owner_id: str, structure_type: str, location: str):
        """Create a structure from construction"""
        # TODO: Implement structure creation
        # This would add the structure to the world and give benefits to the player
        pass
    
    def get_construction_status(self, construction_id: int) -> Optional[Dict[str, Any]]:
        """Get construction status"""
        construction = db.execute_one(
            "SELECT * FROM construction WHERE id = ?", (construction_id,)
        )
        
        if not construction:
            return None
        
        # Calculate progress
        current_time = get_current_timestamp()
        elapsed = current_time - construction["start_time"]
        progress = min(100, (elapsed / construction["duration"]) * 100)
        
        construction["progress"] = progress
        construction["time_remaining"] = max(0, construction["duration"] - elapsed)
        
        return construction
    
    def get_player_constructions(self, player_id: str) -> List[Dict[str, Any]]:
        """Get all constructions for a player"""
        constructions = db.execute_query("""
            SELECT * FROM construction 
            WHERE owner_id = ? 
            ORDER BY start_time DESC
        """, (player_id,))
        
        # Add progress to each construction
        for construction in constructions:
            current_time = get_current_timestamp()
            elapsed = current_time - construction["start_time"]
            progress = min(100, (elapsed / construction["duration"]) * 100)
            
            construction["progress"] = progress
            construction["time_remaining"] = max(0, construction["duration"] - elapsed)
        
        return constructions
    
    def cancel_construction(self, construction_id: int, player_id: str) -> bool:
        """Cancel a construction project"""
        try:
            # Get construction
            construction = db.execute_one(
                "SELECT * FROM construction WHERE id = ? AND owner_id = ?",
                (construction_id, player_id)
            )
            
            if not construction:
                return False
            
            # Check if it's still in progress
            if construction["status"] != "in_progress":
                return False
            
            # Calculate refund (50% of resources)
            # TODO: Implement resource refund
            
            # Mark as cancelled
            db.execute_update(
                "UPDATE construction SET status = 'cancelled' WHERE id = ?",
                (construction_id,)
            )
            
            log_event("construction_cancelled", {
                "construction_id": construction_id,
                "player_id": player_id,
                "structure_type": construction["structure_type"]
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel construction {construction_id}: {e}")
            return False
    
    def get_available_structures(self, player_id: str) -> List[Dict[str, Any]]:
        """Get structures available for construction by player"""
        from systems.player_system import player_system
        
        player = player_system.get_player(player_id)
        if not player:
            return []
        
        player_intelligence = player.get("intelligence", 0)
        available = []
        
        for structure_type, info in self.construction_types.items():
            if player_intelligence >= info["intelligence_required"]:
                available.append({
                    "type": structure_type,
                    "name": info["name"],
                    "duration_days": info["duration_days"],
                    "resources": info["resources"],
                    "intelligence_required": info["intelligence_required"],
                    "location_required": info["location_required"]
                })
        
        return available
    
    def get_construction_display(self, construction: Dict[str, Any]) -> str:
        """Get formatted construction display"""
        structure_type = construction["structure_type"]
        progress = construction.get("progress", 0)
        time_remaining = construction.get("time_remaining", 0)
        
        # Get structure info
        structure_info = self.construction_types.get(structure_type, {})
        structure_name = structure_info.get("name", structure_type)
        
        # Progress bar
        progress_bar = "█" * int(progress // 10) + "░" * (10 - int(progress // 10))
        
        # Time remaining
        hours = time_remaining // 3600
        minutes = (time_remaining % 3600) // 60
        
        display = f"""
🏗️ **{structure_name} Construction**
Progress: {progress:.1f}% [{progress_bar}]
Time Remaining: {hours}h {minutes}m
Status: {construction['status'].title()}
        """.strip()
        
        return display

# Global construction system instance
construction_system = ConstructionSystem()