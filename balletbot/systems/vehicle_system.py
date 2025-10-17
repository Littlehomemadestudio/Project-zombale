"""
Vehicle system for BalletBot: Outbreak Dominion
Manages vehicles, condition, fuel, and movement
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp, add_action_to_history
from config import VEHICLE_TYPES, VEHICLE_CONDITION_THRESHOLD, VEHICLE_REPAIR_RATE

logger = logging.getLogger(__name__)

class VehicleSystem:
    """Manages vehicles and transportation"""
    
    def __init__(self):
        self.vehicle_counter = 0
    
    def create_vehicle(self, vehicle_type: str, owner_id: str, location: str) -> Dict[str, Any]:
        """Create a new vehicle"""
        try:
            if vehicle_type not in VEHICLE_TYPES:
                return {"success": False, "error": f"Unknown vehicle type: {vehicle_type}"}
            
            self.vehicle_counter += 1
            vehicle_id = f"vehicle_{self.vehicle_counter}_{get_current_timestamp()}"
            
            type_data = VEHICLE_TYPES[vehicle_type]
            
            # Create vehicle with random condition
            condition = random.randint(20, 80)  # Vehicles found in looting often have low condition
            
            vehicle_data = {
                "id": vehicle_id,
                "owner_id": owner_id,
                "type": vehicle_type,
                "name": type_data["name"],
                "condition": condition,
                "max_condition": type_data["condition_max"],
                "fuel": type_data["fuel_capacity"],
                "max_fuel": type_data["fuel_capacity"],
                "storage": type_data["storage"],
                "speed": type_data["speed"],
                "location": location,
                "created_at": get_current_timestamp(),
                "status": "idle"
            }
            
            file_manager.save_vehicle(vehicle_id, vehicle_data)
            
            # Add to action history
            add_action_to_history(owner_id, "vehicle_created", vehicle_id=vehicle_id, vehicle_type=vehicle_type)
            
            logger.info(f"Created vehicle {vehicle_type} for player {owner_id}")
            
            return {
                "success": True,
                "vehicle_id": vehicle_id,
                "vehicle_data": vehicle_data,
                "message": f"✅ Created {type_data['name']} (Condition: {condition}%)"
            }
            
        except Exception as e:
            logger.error(f"Error creating vehicle: {e}")
            return {"success": False, "error": "Failed to create vehicle"}
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Dict]:
        """Get vehicle data"""
        return file_manager.get_vehicle(vehicle_id)
    
    def get_player_vehicles(self, player_id: str) -> List[Dict]:
        """Get all vehicles owned by player"""
        try:
            all_vehicles = file_manager.get_all_vehicles()
            player_vehicles = []
            
            for vehicle in all_vehicles.values():
                if vehicle.get("owner_id") == player_id:
                    player_vehicles.append(vehicle)
            
            return player_vehicles
            
        except Exception as e:
            logger.error(f"Error getting player vehicles for {player_id}: {e}")
            return []
    
    def can_drive(self, vehicle_id: str) -> bool:
        """Check if vehicle can be driven"""
        try:
            vehicle = file_manager.get_vehicle(vehicle_id)
            if not vehicle:
                return False
            
            condition = vehicle.get("condition", 0)
            fuel = vehicle.get("fuel", 0)
            
            return condition >= VEHICLE_CONDITION_THRESHOLD and fuel > 0
            
        except Exception as e:
            logger.error(f"Error checking if vehicle can drive: {e}")
            return False
    
    def repair_vehicle(self, player_id: str, vehicle_id: str) -> Dict[str, Any]:
        """Repair a vehicle"""
        try:
            vehicle = file_manager.get_vehicle(vehicle_id)
            if not vehicle:
                return {"success": False, "error": "Vehicle not found"}
            
            if vehicle.get("owner_id") != player_id:
                return {"success": False, "error": "You don't own this vehicle"}
            
            # Check if vehicle needs repair
            condition = vehicle.get("condition", 0)
            max_condition = vehicle.get("max_condition", 100)
            
            if condition >= max_condition:
                return {"success": False, "error": "Vehicle is already in perfect condition"}
            
            # Check repair materials
            from systems.inventory_system import inventory_system
            
            vehicle_type = vehicle.get("type", "")
            type_data = VEHICLE_TYPES.get(vehicle_type, {})
            repair_cost = type_data.get("repair_cost", {"metal": 5})
            
            # Check if player has repair materials
            can_repair = True
            missing_materials = []
            
            for material, required_qty in repair_cost.items():
                if not inventory_system.has_item(player_id, material, required_qty):
                    can_repair = False
                    missing_materials.append(f"{material} x{required_qty}")
            
            if not can_repair:
                return {
                    "success": False,
                    "error": f"Missing repair materials: {', '.join(missing_materials)}"
                }
            
            # Consume materials
            for material, required_qty in repair_cost.items():
                inventory_system.remove_item(player_id, material, required_qty)
            
            # Repair vehicle
            repair_amount = VEHICLE_REPAIR_RATE
            new_condition = min(max_condition, condition + repair_amount)
            vehicle["condition"] = new_condition
            
            file_manager.save_vehicle(vehicle_id, vehicle)
            
            # Add to action history
            add_action_to_history(player_id, "vehicle_repaired", vehicle_id=vehicle_id, repair_amount=repair_amount)
            
            logger.info(f"Player {player_id} repaired vehicle {vehicle_id}")
            
            return {
                "success": True,
                "repair_amount": repair_amount,
                "new_condition": new_condition,
                "message": f"✅ Repaired vehicle! Condition: {new_condition}%"
            }
            
        except Exception as e:
            logger.error(f"Error repairing vehicle: {e}")
            return {"success": False, "error": "Failed to repair vehicle"}
    
    def refuel_vehicle(self, player_id: str, vehicle_id: str, fuel_amount: int = None) -> Dict[str, Any]:
        """Refuel a vehicle"""
        try:
            vehicle = file_manager.get_vehicle(vehicle_id)
            if not vehicle:
                return {"success": False, "error": "Vehicle not found"}
            
            if vehicle.get("owner_id") != player_id:
                return {"success": False, "error": "You don't own this vehicle"}
            
            current_fuel = vehicle.get("fuel", 0)
            max_fuel = vehicle.get("max_fuel", 0)
            
            if current_fuel >= max_fuel:
                return {"success": False, "error": "Vehicle is already fully fueled"}
            
            # Check if player has fuel
            from systems.inventory_system import inventory_system
            
            if not inventory_system.has_item(player_id, "fuel", 1):
                return {"success": False, "error": "You need fuel to refuel the vehicle"}
            
            # Calculate fuel amount
            if fuel_amount is None:
                fuel_amount = min(10, max_fuel - current_fuel)  # Default refuel amount
            
            fuel_needed = min(fuel_amount, max_fuel - current_fuel)
            
            # Check if player has enough fuel
            if not inventory_system.has_item(player_id, "fuel", fuel_needed):
                return {"success": False, "error": f"You need {fuel_needed} fuel"}
            
            # Consume fuel
            inventory_system.remove_item(player_id, "fuel", fuel_needed)
            
            # Refuel vehicle
            vehicle["fuel"] = current_fuel + fuel_needed
            file_manager.save_vehicle(vehicle_id, vehicle)
            
            # Add to action history
            add_action_to_history(player_id, "vehicle_refueled", vehicle_id=vehicle_id, fuel_amount=fuel_needed)
            
            logger.info(f"Player {player_id} refueled vehicle {vehicle_id}")
            
            return {
                "success": True,
                "fuel_added": fuel_needed,
                "new_fuel": vehicle["fuel"],
                "message": f"✅ Refueled vehicle! Fuel: {vehicle['fuel']}/{max_fuel}"
            }
            
        except Exception as e:
            logger.error(f"Error refueling vehicle: {e}")
            return {"success": False, "error": "Failed to refuel vehicle"}
    
    def move_vehicle(self, player_id: str, vehicle_id: str, destination: str) -> Dict[str, Any]:
        """Move vehicle to destination"""
        try:
            vehicle = file_manager.get_vehicle(vehicle_id)
            if not vehicle:
                return {"success": False, "error": "Vehicle not found"}
            
            if vehicle.get("owner_id") != player_id:
                return {"success": False, "error": "You don't own this vehicle"}
            
            # Check if vehicle can drive
            if not self.can_drive(vehicle_id):
                return {"success": False, "error": "Vehicle cannot be driven (low condition or no fuel)"}
            
            # Calculate fuel cost
            current_location = vehicle.get("location", "")
            fuel_cost = self._calculate_fuel_cost(current_location, destination, vehicle.get("type", ""))
            
            if vehicle.get("fuel", 0) < fuel_cost:
                return {"success": False, "error": f"Not enough fuel. Need {fuel_cost} fuel"}
            
            # Consume fuel
            vehicle["fuel"] = vehicle.get("fuel", 0) - fuel_cost
            vehicle["location"] = destination
            vehicle["status"] = "traveling"
            
            file_manager.save_vehicle(vehicle_id, vehicle)
            
            # Add to action history
            add_action_to_history(player_id, "vehicle_moved", vehicle_id=vehicle_id, destination=destination, fuel_cost=fuel_cost)
            
            logger.info(f"Player {player_id} moved vehicle {vehicle_id} to {destination}")
            
            return {
                "success": True,
                "destination": destination,
                "fuel_cost": fuel_cost,
                "remaining_fuel": vehicle["fuel"],
                "message": f"✅ Vehicle moved to {destination} (Fuel cost: {fuel_cost})"
            }
            
        except Exception as e:
            logger.error(f"Error moving vehicle: {e}")
            return {"success": False, "error": "Failed to move vehicle"}
    
    def _calculate_fuel_cost(self, from_location: str, to_location: str, vehicle_type: str) -> int:
        """Calculate fuel cost for movement"""
        try:
            # Simple distance calculation
            from utils.helpers import calculate_distance
            distance = calculate_distance(from_location, to_location)
            
            # Get vehicle type data
            type_data = VEHICLE_TYPES.get(vehicle_type, {})
            speed = type_data.get("speed", 1)
            
            # Calculate fuel cost based on distance and speed
            base_cost = distance * 2
            speed_modifier = max(0.5, 2 - speed)  # Faster vehicles use less fuel per distance
            
            fuel_cost = int(base_cost * speed_modifier)
            return max(1, fuel_cost)
            
        except Exception as e:
            logger.error(f"Error calculating fuel cost: {e}")
            return 5  # Default fuel cost
    
    def get_vehicle_status(self, vehicle_id: str) -> str:
        """Get formatted vehicle status"""
        try:
            vehicle = file_manager.get_vehicle(vehicle_id)
            if not vehicle:
                return "❌ Vehicle not found"
            
            condition = vehicle.get("condition", 0)
            fuel = vehicle.get("fuel", 0)
            max_fuel = vehicle.get("max_fuel", 0)
            location = vehicle.get("location", "Unknown")
            
            status = f"🚗 **{vehicle.get('name', 'Vehicle')}**\n"
            status += f"🔧 Condition: {condition}%\n"
            status += f"⛽ Fuel: {fuel}/{max_fuel}\n"
            status += f"📍 Location: {location}\n"
            status += f"📦 Storage: {vehicle.get('storage', 0)} slots\n"
            status += f"🏃 Speed: {vehicle.get('speed', 1)}\n"
            
            # Status indicators
            if condition < VEHICLE_CONDITION_THRESHOLD:
                status += "⚠️ Needs repair\n"
            if fuel == 0:
                status += "⚠️ Out of fuel\n"
            if condition >= VEHICLE_CONDITION_THRESHOLD and fuel > 0:
                status += "✅ Ready to drive\n"
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting vehicle status: {e}")
            return "❌ Error getting vehicle status"
    
    def format_vehicle_list(self, player_id: str) -> str:
        """Format vehicle list for player"""
        try:
            vehicles = self.get_player_vehicles(player_id)
            
            if not vehicles:
                return "🚗 **No vehicles owned**"
            
            display = "🚗 **Your Vehicles:**\n\n"
            
            for vehicle in vehicles:
                vehicle_id = vehicle.get("id", "Unknown")
                name = vehicle.get("name", "Vehicle")
                condition = vehicle.get("condition", 0)
                fuel = vehicle.get("fuel", 0)
                max_fuel = vehicle.get("max_fuel", 0)
                location = vehicle.get("location", "Unknown")
                
                display += f"**{name}** ({vehicle_id})\n"
                display += f"  Condition: {condition}%\n"
                display += f"  Fuel: {fuel}/{max_fuel}\n"
                display += f"  Location: {location}\n"
                
                if condition < VEHICLE_CONDITION_THRESHOLD:
                    display += "  ⚠️ Needs repair\n"
                elif fuel == 0:
                    display += "  ⚠️ Out of fuel\n"
                else:
                    display += "  ✅ Ready\n"
                
                display += "\n"
            
            return display
            
        except Exception as e:
            logger.error(f"Error formatting vehicle list: {e}")
            return "❌ Error getting vehicle list"
    
    def get_available_vehicles(self) -> List[Dict]:
        """Get all available vehicle types"""
        vehicles = []
        
        for vehicle_type, type_data in VEHICLE_TYPES.items():
            vehicles.append({
                "type": vehicle_type,
                "name": type_data["name"],
                "condition_max": type_data["condition_max"],
                "fuel_capacity": type_data["fuel_capacity"],
                "storage": type_data["storage"],
                "speed": type_data["speed"],
                "repair_cost": type_data.get("repair_cost", {})
            })
        
        return vehicles
    
    def deploy_vehicle(self, player_id: str, vehicle_id: str) -> Dict[str, Any]:
        """Deploy vehicle (for large vehicles like tanks)"""
        try:
            vehicle = file_manager.get_vehicle(vehicle_id)
            if not vehicle:
                return {"success": False, "error": "Vehicle not found"}
            
            if vehicle.get("owner_id") != player_id:
                return {"success": False, "error": "You don't own this vehicle"}
            
            vehicle_type = vehicle.get("type", "")
            
            # Check if vehicle can be deployed
            if vehicle_type not in ["tank", "heli", "warship"]:
                return {"success": False, "error": "This vehicle cannot be deployed"}
            
            # Check if vehicle is ready
            if not self.can_drive(vehicle_id):
                return {"success": False, "error": "Vehicle is not ready for deployment"}
            
            # Deploy vehicle
            vehicle["status"] = "deployed"
            file_manager.save_vehicle(vehicle_id, vehicle)
            
            # Add to action history
            add_action_to_history(player_id, "vehicle_deployed", vehicle_id=vehicle_id, vehicle_type=vehicle_type)
            
            # TODO: Send global announcement for large vehicle deployment
            
            logger.info(f"Player {player_id} deployed vehicle {vehicle_id}")
            
            return {
                "success": True,
                "vehicle_id": vehicle_id,
                "message": f"✅ {vehicle.get('name', 'Vehicle')} deployed successfully!"
            }
            
        except Exception as e:
            logger.error(f"Error deploying vehicle: {e}")
            return {"success": False, "error": "Failed to deploy vehicle"}
    
    def get_vehicle_repair_cost(self, vehicle_id: str) -> Dict[str, Any]:
        """Get vehicle repair cost"""
        try:
            vehicle = file_manager.get_vehicle(vehicle_id)
            if not vehicle:
                return {"success": False, "error": "Vehicle not found"}
            
            vehicle_type = vehicle.get("type", "")
            type_data = VEHICLE_TYPES.get(vehicle_type, {})
            repair_cost = type_data.get("repair_cost", {"metal": 5})
            
            return {
                "success": True,
                "repair_cost": repair_cost,
                "current_condition": vehicle.get("condition", 0),
                "max_condition": vehicle.get("max_condition", 100)
            }
            
        except Exception as e:
            logger.error(f"Error getting vehicle repair cost: {e}")
            return {"success": False, "error": "Failed to get repair cost"}

# Global vehicle system instance
vehicle_system = VehicleSystem()