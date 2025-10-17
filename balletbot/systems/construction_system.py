"""
Construction system for BalletBot: Outbreak Dominion
Manages multi-day construction projects
"""

import logging
from typing import Dict, List, Optional, Any
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp, add_action_to_history

logger = logging.getLogger(__name__)

class ConstructionSystem:
    """Manages construction projects"""
    
    def __init__(self):
        self.construction_counter = 0
    
    def start_construction(self, player_id: str, structure_type: str, location: str, 
                         resources: Dict[str, int], duration_hours: int = 24) -> Dict[str, Any]:
        """Start a construction project"""
        try:
            # Validate structure type
            valid_structures = ["tank", "helicopter", "warship", "radio_tower", "fortress"]
            if structure_type not in valid_structures:
                return {"success": False, "error": f"Invalid structure type. Choose: {', '.join(valid_structures)}"}
            
            # Check if player has required resources
            from systems.inventory_system import inventory_system
            
            can_afford, missing = inventory_system.can_craft_item(player_id, {
                "resources": resources
            })
            
            if not can_afford:
                return {
                    "success": False,
                    "error": f"Insufficient resources. Missing: {', '.join(missing)}"
                }
            
            # Consume resources
            if not inventory_system.consume_crafting_materials(player_id, {
                "resources": resources
            }):
                return {"success": False, "error": "Failed to consume resources"}
            
            # Create construction project
            self.construction_counter += 1
            construction_id = f"construction_{self.construction_counter}_{get_current_timestamp()}"
            
            current_time = get_current_timestamp()
            duration_seconds = duration_hours * 3600
            
            construction_data = {
                "id": construction_id,
                "owner_id": player_id,
                "structure_type": structure_type,
                "start_time": current_time,
                "duration": duration_seconds,
                "resources": resources,
                "status": "in_progress",
                "location": location,
                "created_at": current_time
            }
            
            file_manager.add_construction(construction_data)
            
            # Add to action history
            add_action_to_history(player_id, "construction_started", 
                                structure_type=structure_type, construction_id=construction_id)
            
            logger.info(f"Player {player_id} started construction of {structure_type}")
            
            return {
                "success": True,
                "construction_id": construction_id,
                "duration_hours": duration_hours,
                "message": f"✅ Construction of {structure_type} started! Duration: {duration_hours} hours"
            }
            
        except Exception as e:
            logger.error(f"Error starting construction: {e}")
            return {"success": False, "error": "Failed to start construction"}
    
    def complete_construction(self, construction_id: str) -> Dict[str, Any]:
        """Complete a construction project"""
        try:
            construction_projects = file_manager.get_construction(construction_id)
            if not construction_projects:
                return {"success": False, "error": "Construction project not found"}
            
            project = construction_projects[0]
            owner_id = project.get("owner_id")
            structure_type = project.get("structure_type")
            location = project.get("location")
            
            # Create the structure
            if structure_type in ["tank", "helicopter", "warship"]:
                # Create vehicle
                from systems.vehicle_system import vehicle_system
                result = vehicle_system.create_vehicle(structure_type, owner_id, location)
                
                if not result["success"]:
                    return {"success": False, "error": "Failed to create vehicle"}
                
            elif structure_type == "radio_tower":
                # Create radio tower
                from systems.radio_system import radio_system
                radio_system.create_radio_tower(location, owner_id)
                
            elif structure_type == "fortress":
                # Create fortress (building)
                building_id = f"{location}:Fortress"
                building_data = {
                    "id": building_id,
                    "region": location.split(":")[0],
                    "name": "Fortress",
                    "floors": [
                        {"floor": 1, "difficulty": 80, "zombies": 0, "loot_table": "fortress_floor_1"},
                        {"floor": 2, "difficulty": 90, "zombies": 0, "loot_table": "fortress_floor_2"},
                        {"floor": 3, "difficulty": 100, "zombies": 0, "loot_table": "fortress_floor_3"}
                    ],
                    "cleared_by": {},
                    "last_checked": get_current_timestamp()
                }
                
                file_manager.save_building(building_id, building_data)
            
            # Update construction status
            file_manager.update_construction(construction_id, {
                "status": "completed",
                "completed_at": get_current_timestamp()
            })
            
            # Add to action history
            add_action_to_history(owner_id, "construction_completed", 
                                structure_type=structure_type, construction_id=construction_id)
            
            logger.info(f"Construction {construction_id} completed for player {owner_id}")
            
            return {
                "success": True,
                "structure_type": structure_type,
                "message": f"✅ Construction of {structure_type} completed!"
            }
            
        except Exception as e:
            logger.error(f"Error completing construction: {e}")
            return {"success": False, "error": "Failed to complete construction"}
    
    def cancel_construction(self, player_id: str, construction_id: str) -> Dict[str, Any]:
        """Cancel a construction project with partial refund"""
        try:
            construction_projects = file_manager.get_construction(construction_id)
            if not construction_projects:
                return {"success": False, "error": "Construction project not found"}
            
            project = construction_projects[0]
            
            if project.get("owner_id") != player_id:
                return {"success": False, "error": "You don't own this construction project"}
            
            if project.get("status") != "in_progress":
                return {"success": False, "error": "Construction project is not in progress"}
            
            # Calculate partial refund (50%)
            resources = project.get("resources", {})
            refund_resources = {}
            for resource, qty in resources.items():
                refund_resources[resource] = qty // 2
            
            # Give refund
            from systems.inventory_system import inventory_system
            for resource, qty in refund_resources.items():
                inventory_system.add_item(player_id, resource, qty)
            
            # Update construction status
            file_manager.update_construction(construction_id, {
                "status": "cancelled",
                "cancelled_at": get_current_timestamp()
            })
            
            # Add to action history
            add_action_to_history(player_id, "construction_cancelled", 
                                construction_id=construction_id, refund=refund_resources)
            
            logger.info(f"Player {player_id} cancelled construction {construction_id}")
            
            return {
                "success": True,
                "refund": refund_resources,
                "message": f"✅ Construction cancelled. Refunded: {', '.join([f'{k} x{v}' for k, v in refund_resources.items()])}"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling construction: {e}")
            return {"success": False, "error": "Failed to cancel construction"}
    
    def get_player_constructions(self, player_id: str) -> List[Dict]:
        """Get all construction projects for a player"""
        try:
            all_constructions = file_manager.get_construction()
            player_constructions = []
            
            for construction in all_constructions:
                if construction.get("owner_id") == player_id:
                    player_constructions.append(construction)
            
            return player_constructions
            
        except Exception as e:
            logger.error(f"Error getting player constructions: {e}")
            return []
    
    def get_construction_progress(self, construction_id: str) -> Dict[str, Any]:
        """Get construction progress"""
        try:
            construction_projects = file_manager.get_construction(construction_id)
            if not construction_projects:
                return {"success": False, "error": "Construction project not found"}
            
            project = construction_projects[0]
            current_time = get_current_timestamp()
            start_time = project.get("start_time", 0)
            duration = project.get("duration", 0)
            
            elapsed = current_time - start_time
            progress_percent = min(100, (elapsed / duration) * 100) if duration > 0 else 0
            
            time_remaining = max(0, duration - elapsed)
            
            return {
                "success": True,
                "construction_id": construction_id,
                "structure_type": project.get("structure_type"),
                "status": project.get("status"),
                "progress_percent": progress_percent,
                "time_remaining": time_remaining,
                "is_complete": elapsed >= duration
            }
            
        except Exception as e:
            logger.error(f"Error getting construction progress: {e}")
            return {"success": False, "error": "Failed to get construction progress"}
    
    def format_construction_list(self, player_id: str) -> str:
        """Format construction list for player"""
        try:
            constructions = self.get_player_constructions(player_id)
            
            if not constructions:
                return "🏗️ **No construction projects**"
            
            display = "🏗️ **Your Construction Projects:**\n\n"
            
            for construction in constructions:
                construction_id = construction.get("id", "Unknown")
                structure_type = construction.get("structure_type", "Unknown")
                status = construction.get("status", "Unknown")
                
                display += f"**{structure_type}** ({construction_id})\n"
                display += f"  Status: {status}\n"
                
                if status == "in_progress":
                    progress = self.get_construction_progress(construction_id)
                    if progress.get("success"):
                        display += f"  Progress: {progress['progress_percent']:.1f}%\n"
                        display += f"  Time remaining: {progress['time_remaining'] // 3600}h\n"
                
                display += "\n"
            
            return display
            
        except Exception as e:
            logger.error(f"Error formatting construction list: {e}")
            return "❌ Error getting construction list"
    
    def get_available_structures(self) -> List[Dict]:
        """Get available structures for construction"""
        return [
            {
                "type": "tank",
                "name": "Tank",
                "description": "Heavy armored vehicle",
                "base_duration": 168,  # 7 days
                "base_resources": {"steel": 50, "engine_parts": 10, "circuit": 20}
            },
            {
                "type": "helicopter",
                "name": "Helicopter",
                "description": "Aerial vehicle",
                "base_duration": 120,  # 5 days
                "base_resources": {"steel": 30, "engine_parts": 8, "circuit": 15}
            },
            {
                "type": "warship",
                "name": "Warship",
                "description": "Naval vessel",
                "base_duration": 240,  # 10 days
                "base_resources": {"steel": 100, "engine_parts": 20, "circuit": 30}
            },
            {
                "type": "radio_tower",
                "name": "Radio Tower",
                "description": "Long-range communication",
                "base_duration": 48,  # 2 days
                "base_resources": {"metal": 20, "circuit": 10, "battery": 5}
            },
            {
                "type": "fortress",
                "name": "Fortress",
                "description": "Defensive structure",
                "base_duration": 72,  # 3 days
                "base_resources": {"stone": 50, "metal": 30, "circuit": 5}
            }
        ]
    
    def format_available_structures(self) -> str:
        """Format available structures for display"""
        try:
            structures = self.get_available_structures()
            
            display = "🏗️ **Available Structures:**\n\n"
            
            for structure in structures:
                display += f"**{structure['name']}**\n"
                display += f"  Type: {structure['type']}\n"
                display += f"  Description: {structure['description']}\n"
                display += f"  Duration: {structure['base_duration']} hours\n"
                display += f"  Resources: {', '.join([f'{k} x{v}' for k, v in structure['base_resources'].items()])}\n\n"
            
            return display
            
        except Exception as e:
            logger.error(f"Error formatting available structures: {e}")
            return "❌ Error getting available structures"

# Global construction system instance
construction_system = ConstructionSystem()