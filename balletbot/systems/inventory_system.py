"""
Inventory system for BalletBot: Outbreak Dominion
Manages player inventories and items
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp

logger = logging.getLogger(__name__)

class InventorySystem:
    """Manages player inventories and items"""
    
    def __init__(self):
        self.item_definitions: Dict[str, Dict] = {}
        self._load_item_definitions()
    
    def _load_item_definitions(self):
        """Load item definitions from JSON file"""
        try:
            with open("data/items.json", "r", encoding="utf-8") as f:
                self.item_definitions = json.load(f)
            logger.info(f"Loaded {len(self.item_definitions)} item definitions")
        except Exception as e:
            logger.error(f"Error loading item definitions: {e}")
            self.item_definitions = {}
    
    def get_item_definition(self, item_id: str) -> Optional[Dict]:
        """Get item definition"""
        return self.item_definitions.get(item_id)
    
    def get_all_items(self) -> Dict[str, Dict]:
        """Get all item definitions"""
        return self.item_definitions.copy()
    
    def get_player_inventory(self, player_id: str) -> Dict[str, int]:
        """Get player inventory"""
        return file_manager.get_player_inventory(player_id)
    
    def add_item(self, player_id: str, item_id: str, quantity: int) -> bool:
        """Add item to player inventory"""
        try:
            if item_id not in self.item_definitions:
                logger.warning(f"Unknown item: {item_id}")
                return False
            
            file_manager.add_item_to_inventory(player_id, item_id, quantity)
            
            # Add to action history
            from utils.helpers import add_action_to_history
            add_action_to_history(player_id, "item_added", item_id=item_id, quantity=quantity)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding item {item_id} to player {player_id}: {e}")
            return False
    
    def remove_item(self, player_id: str, item_id: str, quantity: int) -> bool:
        """Remove item from player inventory"""
        try:
            if item_id not in self.item_definitions:
                logger.warning(f"Unknown item: {item_id}")
                return False
            
            success = file_manager.remove_item_from_inventory(player_id, item_id, quantity)
            
            if success:
                # Add to action history
                from utils.helpers import add_action_to_history
                add_action_to_history(player_id, "item_removed", item_id=item_id, quantity=quantity)
            
            return success
            
        except Exception as e:
            logger.error(f"Error removing item {item_id} from player {player_id}: {e}")
            return False
    
    def has_item(self, player_id: str, item_id: str, quantity: int = 1) -> bool:
        """Check if player has item"""
        return file_manager.has_item(player_id, item_id, quantity)
    
    def get_item_quantity(self, player_id: str, item_id: str) -> int:
        """Get quantity of specific item"""
        inventory = file_manager.get_player_inventory(player_id)
        return inventory.get(item_id, 0)
    
    def transfer_item(self, from_player: str, to_player: str, item_id: str, quantity: int) -> bool:
        """Transfer item between players"""
        try:
            if not self.has_item(from_player, item_id, quantity):
                return False
            
            if not self.remove_item(from_player, item_id, quantity):
                return False
            
            if not self.add_item(to_player, item_id, quantity):
                # Rollback
                self.add_item(from_player, item_id, quantity)
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error transferring item {item_id} from {from_player} to {to_player}: {e}")
            return False
    
    def get_items_by_type(self, player_id: str, item_type: str) -> Dict[str, int]:
        """Get items of specific type from player inventory"""
        inventory = file_manager.get_player_inventory(player_id)
        filtered_items = {}
        
        for item_id, quantity in inventory.items():
            item_def = self.get_item_definition(item_id)
            if item_def and item_def.get("type") == item_type:
                filtered_items[item_id] = quantity
        
        return filtered_items
    
    def get_weapons(self, player_id: str) -> Dict[str, int]:
        """Get weapons from player inventory"""
        return self.get_items_by_type(player_id, "weapon")
    
    def get_meds(self, player_id: str) -> Dict[str, int]:
        """Get medical items from player inventory"""
        return self.get_items_by_type(player_id, "med")
    
    def get_resources(self, player_id: str) -> Dict[str, int]:
        """Get resources from player inventory"""
        return self.get_items_by_type(player_id, "resource")
    
    def get_tools(self, player_id: str) -> Dict[str, int]:
        """Get tools from player inventory"""
        return self.get_items_by_type(player_id, "tool")
    
    def calculate_inventory_weight(self, player_id: str) -> int:
        """Calculate total inventory weight"""
        inventory = file_manager.get_player_inventory(player_id)
        total_weight = 0
        
        for item_id, quantity in inventory.items():
            item_def = self.get_item_definition(item_id)
            if item_def:
                weight = item_def.get("properties", {}).get("weight", 0)
                total_weight += weight * quantity
        
        return total_weight
    
    def calculate_inventory_value(self, player_id: str) -> int:
        """Calculate total inventory value"""
        inventory = file_manager.get_player_inventory(player_id)
        total_value = 0
        
        for item_id, quantity in inventory.items():
            item_def = self.get_item_definition(item_id)
            if item_def:
                value = item_def.get("properties", {}).get("value", 0)
                total_value += value * quantity
        
        return total_value
    
    def can_craft_item(self, player_id: str, recipe: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check if player can craft item"""
        missing_items = []
        
        # Check resources
        for resource, required_qty in recipe.get("resources", {}).items():
            if not self.has_item(player_id, resource, required_qty):
                missing_items.append(f"{resource} x{required_qty}")
        
        # Check intelligence
        required_intelligence = recipe.get("intelligence", 0)
        if required_intelligence > 0:
            from systems.player_system import player_system
            player_data = player_system.get_player(player_id)
            if not player_data or player_data.get("intelligence", 0) < required_intelligence:
                missing_items.append(f"intelligence {required_intelligence}")
        
        return len(missing_items) == 0, missing_items
    
    def consume_crafting_materials(self, player_id: str, recipe: Dict[str, Any]) -> bool:
        """Consume materials for crafting"""
        try:
            # Check if can craft
            can_craft, missing = self.can_craft_item(player_id, recipe)
            if not can_craft:
                return False
            
            # Consume resources
            for resource, required_qty in recipe.get("resources", {}).items():
                if not self.remove_item(player_id, resource, required_qty):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error consuming crafting materials for player {player_id}: {e}")
            return False
    
    def format_inventory(self, player_id: str) -> str:
        """Format inventory for display"""
        inventory = file_manager.get_player_inventory(player_id)
        
        if not inventory:
            return "📦 **Inventory is empty**"
        
        # Group items by type
        items_by_type = {}
        for item_id, quantity in inventory.items():
            item_def = self.get_item_definition(item_id)
            if item_def:
                item_type = item_def.get("type", "misc")
                if item_type not in items_by_type:
                    items_by_type[item_type] = []
                
                items_by_type[item_type].append({
                    "id": item_id,
                    "name": item_def.get("name", item_id),
                    "quantity": quantity,
                    "properties": item_def.get("properties", {})
                })
        
        # Format display
        display = "📦 **Inventory:**\n\n"
        
        for item_type, items in items_by_type.items():
            display += f"**{item_type.title()}:**\n"
            for item in items:
                display += f"• {item['name']} x{item['quantity']}\n"
            display += "\n"
        
        # Add weight and value
        weight = self.calculate_inventory_weight(player_id)
        value = self.calculate_inventory_value(player_id)
        display += f"⚖️ Weight: {weight}\n"
        display += f"💰 Value: {value}"
        
        return display
    
    def format_item_info(self, item_id: str) -> str:
        """Format item information"""
        item_def = self.get_item_definition(item_id)
        if not item_def:
            return f"❌ Unknown item: {item_id}"
        
        from utils.helpers import format_item_info
        return format_item_info(item_def)
    
    def search_items(self, query: str) -> List[Dict]:
        """Search items by name or type"""
        query = query.lower()
        results = []
        
        for item_id, item_def in self.item_definitions.items():
            name = item_def.get("name", "").lower()
            item_type = item_def.get("type", "").lower()
            
            if query in name or query in item_type or query in item_id.lower():
                results.append({
                    "id": item_id,
                    "name": item_def.get("name", item_id),
                    "type": item_def.get("type", "misc"),
                    "properties": item_def.get("properties", {})
                })
        
        return results
    
    def get_loot_drop(self, loot_table: str, difficulty: int = 1) -> List[Tuple[str, int]]:
        """Get random loot drop from loot table"""
        from utils.helpers import get_random_loot_item
        
        loot_items = []
        
        # Base loot
        base_item = get_random_loot_item(loot_table)
        if base_item:
            item_id, base_quantity = base_item
            # Scale quantity by difficulty
            quantity = max(1, int(base_quantity * (1 + difficulty * 0.1)))
            loot_items.append((item_id, quantity))
        
        # Chance for additional loot
        if difficulty > 1:
            additional_chance = min(0.5, difficulty * 0.1)
            if self._roll_chance(additional_chance):
                additional_item = get_random_loot_item(loot_table)
                if additional_item:
                    item_id, quantity = additional_item
                    loot_items.append((item_id, quantity))
        
        return loot_items
    
    def _roll_chance(self, chance: float) -> bool:
        """Roll chance (0.0 to 1.0)"""
        import random
        return random.random() < chance
    
    def get_inventory_summary(self, player_id: str) -> Dict[str, Any]:
        """Get inventory summary statistics"""
        inventory = file_manager.get_player_inventory(player_id)
        
        summary = {
            "total_items": len(inventory),
            "total_quantity": sum(inventory.values()),
            "weight": self.calculate_inventory_weight(player_id),
            "value": self.calculate_inventory_value(player_id),
            "by_type": {}
        }
        
        # Count by type
        for item_id, quantity in inventory.items():
            item_def = self.get_item_definition(item_id)
            if item_def:
                item_type = item_def.get("type", "misc")
                if item_type not in summary["by_type"]:
                    summary["by_type"][item_type] = 0
                summary["by_type"][item_type] += quantity
        
        return summary

# Global inventory system instance
inventory_system = InventorySystem()