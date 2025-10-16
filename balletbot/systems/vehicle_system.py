"""
Vehicle system for BalletBot: Outbreak Dominion
Handles vehicles, condition, repair, and movement
"""

import logging
from typing import Dict, List, Optional, Any

from utils.helpers import get_current_timestamp
from utils.db import db, log_event
from config import VEHICLE_CONDITION_THRESHOLD, VEHICLE_REPAIR_RATE

logger = logging.getLogger(__name__)

class VehicleSystem:
    """Manages vehicles and their operations"""
    
    def __init__(self):
        self.vehicle_types = {
            "bike": {
                "name": "Bicycle",
                "max_condition": 100,
                "fuel_capacity": 0,
                "storage_capacity": 10,
                "speed": 1,
                "fuel_consumption": 0
            },
            "jeep": {
                "name": "Jeep",
                "max_condition": 100,
                "fuel_capacity": 100,
                "storage_capacity": 50,
                "speed": 3,
                "fuel_consumption": 10
            },
            "truck": {
                "name": "Truck",
                "max_condition": 100,
                "fuel_capacity": 150,
                "storage_capacity": 100,
                "speed": 2,
                "fuel_consumption": 15
            },
            "tank": {
                "name": "Tank",
                "max_condition": 100,
                "fuel_capacity": 200,
                "storage_capacity": 30,
                "speed": 1,
                "fuel_consumption": 25
            },
            "helicopter": {
                "name": "Helicopter",
                "max_condition": 100,
                "fuel_capacity": 300,
                "storage_capacity": 20,
                "speed": 5,
                "fuel_consumption": 30
            },
            "warship": {
                "name": "Warship",
                "max_condition": 100,
                "fuel_capacity": 500,
                "storage_capacity": 200,
                "speed": 2,
                "fuel_consumption": 40
            }
        }
    
    def create_vehicle(self, vehicle_data: Dict[str, Any]) -> bool:
        """Create a new vehicle"""
        try:
            db.execute_update("""
                INSERT INTO vehicles 
                (vehicle_id, owner_id, type, condition, fuel, storage, location, properties)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vehicle_data["vehicle_id"],
                vehicle_data.get("owner_id"),
                vehicle_data["type"],
                vehicle_data.get("condition", 100),
                vehicle_data.get("fuel", 100),
                vehicle_data.get("storage", 0),
                vehicle_data["location"],
                str(vehicle_data.get("properties", {}))
            ))
            
            log_event("vehicle_created", {
                "vehicle_id": vehicle_data["vehicle_id"],
                "owner_id": vehicle_data.get("owner_id"),
                "type": vehicle_data["type"],
                "location": vehicle_data["location"]
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create vehicle: {e}")
            return False
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        """Get vehicle by ID"""
        vehicle = db.execute_one("SELECT * FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
        
        if vehicle and isinstance(vehicle.get('properties'), str):
            import json
            vehicle['properties'] = json.loads(vehicle['properties'])
        
        return vehicle
    
    def get_player_vehicles(self, player_id: str) -> List[Dict[str, Any]]:
        """Get all vehicles owned by a player"""
        vehicles = db.execute_query(
            "SELECT * FROM vehicles WHERE owner_id = ? ORDER BY type",
            (player_id,)
        )
        
        # Parse properties JSON
        for vehicle in vehicles:
            if isinstance(vehicle.get('properties'), str):
                import json
                vehicle['properties'] = json.loads(vehicle['properties'])
        
        return vehicles
    
    def get_vehicles_at_location(self, location: str) -> List[Dict[str, Any]]:
        """Get all vehicles at a specific location"""
        vehicles = db.execute_query(
            "SELECT * FROM vehicles WHERE location = ? ORDER BY type",
            (location,)
        )
        
        # Parse properties JSON
        for vehicle in vehicles:
            if isinstance(vehicle.get('properties'), str):
                import json
                vehicle['properties'] = json.loads(vehicle['properties'])
        
        return vehicles
    
    def can_drive_vehicle(self, vehicle: Dict[str, Any]) -> bool:
        """Check if vehicle can be driven"""
        condition = vehicle.get("condition", 0)
        return condition >= VEHICLE_CONDITION_THRESHOLD
    
    def repair_vehicle(self, vehicle_id: str, player_id: str) -> Dict[str, Any]:
        """Repair a vehicle"""
        from systems.inventory_system import inventory_system
        
        vehicle = self.get_vehicle(vehicle_id)
        if not vehicle:
            return {"success": False, "error": "Vehicle not found"}
        
        if vehicle.get("owner_id") != player_id:
            return {"success": False, "error": "You don't own this vehicle"}
        
        # Check if vehicle needs repair
        current_condition = vehicle.get("condition", 100)
        if current_condition >= 100:
            return {"success": False, "error": "Vehicle is already in perfect condition"}
        
        # Check for repair kit
        if not inventory_system.has_item(player_id, "repair_kit", 1):
            return {"success": False, "error": "You need a repair kit to repair the vehicle"}
        
        # Check for metal
        if not inventory_system.has_item(player_id, "metal", 2):
            return {"success": False, "error": "You need 2 metal to repair the vehicle"}
        
        # Consume materials
        if not inventory_system.remove_item(player_id, "repair_kit", 1):
            return {"success": False, "error": "Failed to consume repair kit"}
        
        if not inventory_system.remove_item(player_id, "metal", 2):
            return {"success": False, "error": "Failed to consume metal"}
        
        # Repair vehicle
        new_condition = min(100, current_condition + VEHICLE_REPAIR_RATE)
        
        try:
            db.execute_update(
                "UPDATE vehicles SET condition = ? WHERE vehicle_id = ?",
                (new_condition, vehicle_id)
            )
            
            log_event("vehicle_repaired", {
                "vehicle_id": vehicle_id,
                "player_id": player_id,
                "old_condition": current_condition,
                "new_condition": new_condition
            })
            
            return {
                "success": True,
                "old_condition": current_condition,
                "new_condition": new_condition,
                "repair_amount": new_condition - current_condition
            }
            
        except Exception as e:
            logger.error(f"Failed to repair vehicle {vehicle_id}: {e}")
            return {"success": False, "error": "Failed to repair vehicle"}
    
    def move_vehicle(self, vehicle_id: str, new_location: str, 
                    distance: int = 1) -> Dict[str, Any]:
        """Move vehicle to new location"""
        vehicle = self.get_vehicle(vehicle_id)
        if not vehicle:
            return {"success": False, "error": "Vehicle not found"}
        
        if not self.can_drive_vehicle(vehicle):
            return {"success": False, "error": "Vehicle condition too low to drive"}
        
        # Check fuel
        vehicle_type = vehicle.get("type", "bike")
        type_info = self.vehicle_types.get(vehicle_type, {})
        fuel_consumption = type_info.get("fuel_consumption", 0)
        
        if fuel_consumption > 0:
            current_fuel = vehicle.get("fuel", 0)
            required_fuel = fuel_consumption * distance
            
            if current_fuel < required_fuel:
                return {
                    "success": False, 
                    "error": f"Insufficient fuel. Need {required_fuel}, have {current_fuel}"
                }
            
            # Consume fuel
            new_fuel = current_fuel - required_fuel
            db.execute_update(
                "UPDATE vehicles SET fuel = ? WHERE vehicle_id = ?",
                (new_fuel, vehicle_id)
            )
        
        # Update location
        try:
            db.execute_update(
                "UPDATE vehicles SET location = ? WHERE vehicle_id = ?",
                (new_location, vehicle_id)
            )
            
            log_event("vehicle_moved", {
                "vehicle_id": vehicle_id,
                "old_location": vehicle.get("location"),
                "new_location": new_location,
                "distance": distance
            })
            
            return {
                "success": True,
                "new_location": new_location,
                "fuel_consumed": fuel_consumption * distance if fuel_consumption > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to move vehicle {vehicle_id}: {e}")
            return {"success": False, "error": "Failed to move vehicle"}
    
    def refuel_vehicle(self, vehicle_id: str, player_id: str, fuel_amount: int) -> Dict[str, Any]:
        """Refuel a vehicle"""
        from systems.inventory_system import inventory_system
        
        vehicle = self.get_vehicle(vehicle_id)
        if not vehicle:
            return {"success": False, "error": "Vehicle not found"}
        
        if vehicle.get("owner_id") != player_id:
            return {"success": False, "error": "You don't own this vehicle"}
        
        # Check for fuel
        if not inventory_system.has_item(player_id, "fuel", fuel_amount):
            return {"success": False, "error": f"You need {fuel_amount} fuel"}
        
        # Get vehicle type info
        vehicle_type = vehicle.get("type", "bike")
        type_info = self.vehicle_types.get(vehicle_type, {})
        max_fuel = type_info.get("fuel_capacity", 0)
        
        if max_fuel == 0:
            return {"success": False, "error": "This vehicle doesn't use fuel"}
        
        current_fuel = vehicle.get("fuel", 0)
        new_fuel = min(max_fuel, current_fuel + fuel_amount)
        actual_fuel_added = new_fuel - current_fuel
        
        if actual_fuel_added <= 0:
            return {"success": False, "error": "Vehicle is already full of fuel"}
        
        # Consume fuel from inventory
        if not inventory_system.remove_item(player_id, "fuel", actual_fuel_added):
            return {"success": False, "error": "Failed to consume fuel"}
        
        # Update vehicle fuel
        try:
            db.execute_update(
                "UPDATE vehicles SET fuel = ? WHERE vehicle_id = ?",
                (new_fuel, vehicle_id)
            )
            
            log_event("vehicle_refueled", {
                "vehicle_id": vehicle_id,
                "player_id": player_id,
                "fuel_added": actual_fuel_added,
                "new_fuel": new_fuel
            })
            
            return {
                "success": True,
                "fuel_added": actual_fuel_added,
                "new_fuel": new_fuel,
                "max_fuel": max_fuel
            }
            
        except Exception as e:
            logger.error(f"Failed to refuel vehicle {vehicle_id}: {e}")
            return {"success": False, "error": "Failed to refuel vehicle"}
    
    def get_vehicle_display(self, vehicle: Dict[str, Any]) -> str:
        """Get formatted vehicle display"""
        vehicle_type = vehicle.get("type", "unknown")
        type_info = self.vehicle_types.get(vehicle_type, {})
        name = type_info.get("name", vehicle_type.title())
        
        condition = vehicle.get("condition", 0)
        fuel = vehicle.get("fuel", 0)
        max_fuel = type_info.get("fuel_capacity", 0)
        storage = vehicle.get("storage", 0)
        max_storage = type_info.get("storage_capacity", 0)
        
        # Condition bar
        condition_percent = (condition / 100) * 100
        condition_bar = "█" * int(condition_percent // 10) + "░" * (10 - int(condition_percent // 10))
        
        # Fuel bar (if applicable)
        fuel_display = ""
        if max_fuel > 0:
            fuel_percent = (fuel / max_fuel) * 100
            fuel_bar = "█" * int(fuel_percent // 10) + "░" * (10 - int(fuel_percent // 10))
            fuel_display = f"⛽ Fuel: {fuel}/{max_fuel} [{fuel_bar}]\n"
        
        # Storage display
        storage_display = f"📦 Storage: {storage}/{max_storage}\n"
        
        # Driveable status
        can_drive = self.can_drive_vehicle(vehicle)
        drive_status = "✅ Driveable" if can_drive else "❌ Needs Repair"
        
        display = f"""
🚗 **{name}**
🔧 Condition: {condition}/100 [{condition_bar}] {drive_status}
{fuel_display}{storage_display}
📍 Location: {vehicle.get('location', 'Unknown')}
        """.strip()
        
        return display
    
    def get_vehicle_types(self) -> Dict[str, Dict[str, Any]]:
        """Get all available vehicle types"""
        return self.vehicle_types
    
    def get_vehicle_type_info(self, vehicle_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific vehicle type"""
        return self.vehicle_types.get(vehicle_type)

# Global vehicle system instance
vehicle_system = VehicleSystem()