"""
Inventory system for BalletBot: Outbreak Dominion
Handles item management, trading, and inventory operations
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple

from utils.db import db, get_player_inventory, add_item_to_inventory, remove_item_from_inventory
from utils.helpers import format_inventory_item, sanitize_input

logger = logging.getLogger(__name__)

class InventorySystem:
    """Manages player inventories and item operations"""
    
    def __init__(self):
        self.item_cache: Dict[str, Dict] = {}
        self._load_items()
    
    def _load_items(self):
        """Load items from database into cache"""
        items = db.execute_query("SELECT * FROM items")
        for item in items:
            # Parse properties JSON
            if isinstance(item.get('properties'), str):
                item['properties'] = json.loads(item['properties'])
            self.item_cache[item['item_id']] = item
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item definition by ID"""
        return self.item_cache.get(item_id)
    
    def get_player_inventory(self, player_id: str) -> List[Dict[str, Any]]:
        """Get player's inventory with item details"""
        return get_player_inventory(player_id)
    
    def get_inventory_display(self, player_id: str) -> str:
        """Get formatted inventory display"""
        inventory = self.get_player_inventory(player_id)
        if not inventory:
            return "📦 Inventory is empty"
        
        display = "📦 **Inventory:**\n"
        for item in inventory:
            display += format_inventory_item(item) + "\n"
        
        return display.strip()
    
    def has_item(self, player_id: str, item_id: str, quantity: int = 1) -> bool:
        """Check if player has enough of an item"""
        inventory = self.get_player_inventory(player_id)
        for item in inventory:
            if item['item_id'] == item_id and item['qty'] >= quantity:
                return True
        return False
    
    def add_item(self, player_id: str, item_id: str, quantity: int) -> bool:
        """Add item to player inventory"""
        if quantity <= 0:
            return False
        
        # Validate item exists
        if not self.get_item(item_id):
            logger.warning(f"Attempted to add non-existent item: {item_id}")
            return False
        
        success = add_item_to_inventory(player_id, item_id, quantity)
        if success:
            logger.info(f"Added {quantity}x {item_id} to player {player_id}")
        return success
    
    def remove_item(self, player_id: str, item_id: str, quantity: int) -> bool:
        """Remove item from player inventory"""
        if quantity <= 0:
            return False
        
        success = remove_item_from_inventory(player_id, item_id, quantity)
        if success:
            logger.info(f"Removed {quantity}x {item_id} from player {player_id}")
        return success
    
    def transfer_item(self, from_player: str, to_player: str, item_id: str, quantity: int) -> bool:
        """Transfer item between players"""
        if not self.has_item(from_player, item_id, quantity):
            return False
        
        if not self.remove_item(from_player, item_id, quantity):
            return False
        
        if not self.add_item(to_player, item_id, quantity):
            # Rollback
            self.add_item(from_player, item_id, quantity)
            return False
        
        return True
    
    def get_item_quantity(self, player_id: str, item_id: str) -> int:
        """Get quantity of specific item in player inventory"""
        inventory = self.get_player_inventory(player_id)
        for item in inventory:
            if item['item_id'] == item_id:
                return item['qty']
        return 0
    
    def get_items_by_type(self, player_id: str, item_type: str) -> List[Dict[str, Any]]:
        """Get all items of specific type in player inventory"""
        inventory = self.get_player_inventory(player_id)
        return [item for item in inventory if item.get('type') == item_type]
    
    def get_weapons(self, player_id: str) -> List[Dict[str, Any]]:
        """Get all weapons in player inventory"""
        return self.get_items_by_type(player_id, 'weapon')
    
    def get_meds(self, player_id: str) -> List[Dict[str, Any]]:
        """Get all medical items in player inventory"""
        return self.get_items_by_type(player_id, 'med')
    
    def get_resources(self, player_id: str) -> List[Dict[str, Any]]:
        """Get all resource items in player inventory"""
        return self.get_items_by_type(player_id, 'resource')
    
    def get_components(self, player_id: str) -> List[Dict[str, Any]]:
        """Get all component items in player inventory"""
        return self.get_items_by_type(player_id, 'component')
    
    def get_tools(self, player_id: str) -> List[Dict[str, Any]]:
        """Get all tool items in player inventory"""
        return self.get_items_by_type(player_id, 'tool')
    
    def can_craft_item(self, player_id: str, recipe: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check if player can craft an item based on recipe requirements"""
        missing_items = []
        
        # Check resource requirements
        for resource, required_qty in recipe.get('resources', {}).items():
            if not self.has_item(player_id, resource, required_qty):
                missing_items.append(f"{resource} x{required_qty}")
        
        # Check intelligence requirement
        from systems.player_system import player_system
        player = player_system.get_player(player_id)
        if not player:
            return False, ["Player not found"]
        
        required_intel = recipe.get('intelligence', 0)
        if player.get('intelligence', 0) < required_intel:
            missing_items.append(f"Intelligence {required_intel}")
        
        return len(missing_items) == 0, missing_items
    
    def consume_crafting_materials(self, player_id: str, recipe: Dict[str, Any]) -> bool:
        """Consume materials for crafting"""
        for resource, required_qty in recipe.get('resources', {}).items():
            if not self.remove_item(player_id, resource, required_qty):
                return False
        return True
    
    def get_inventory_weight(self, player_id: str) -> int:
        """Calculate total weight of inventory"""
        inventory = self.get_player_inventory(player_id)
        total_weight = 0
        
        for item in inventory:
            weight = item.get('properties', {}).get('weight', 1)
            total_weight += weight * item['qty']
        
        return total_weight
    
    def get_inventory_value(self, player_id: str) -> int:
        """Calculate total value of inventory"""
        inventory = self.get_player_inventory(player_id)
        total_value = 0
        
        for item in inventory:
            value = item.get('properties', {}).get('value', 0)
            total_value += value * item['qty']
        
        return total_value
    
    def search_inventory(self, player_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search inventory by item name"""
        inventory = self.get_player_inventory(player_id)
        search_term = search_term.lower()
        
        results = []
        for item in inventory:
            if search_term in item.get('name', '').lower():
                results.append(item)
        
        return results
    
    def get_inventory_summary(self, player_id: str) -> Dict[str, Any]:
        """Get inventory summary statistics"""
        inventory = self.get_player_inventory(player_id)
        
        summary = {
            'total_items': len(inventory),
            'total_quantity': sum(item['qty'] for item in inventory),
            'weight': self.get_inventory_weight(player_id),
            'value': self.get_inventory_value(player_id),
            'by_type': {}
        }
        
        # Count by type
        for item in inventory:
            item_type = item.get('type', 'unknown')
            if item_type not in summary['by_type']:
                summary['by_type'][item_type] = 0
            summary['by_type'][item_type] += item['qty']
        
        return summary
    
    def create_item(self, item_id: str, name: str, item_type: str, properties: Dict = None) -> bool:
        """Create a new item definition"""
        try:
            db.execute_update("""
                INSERT OR REPLACE INTO items (item_id, name, type, properties)
                VALUES (?, ?, ?, ?)
            """, (item_id, name, item_type, json.dumps(properties or {})))
            
            # Update cache
            self.item_cache[item_id] = {
                'item_id': item_id,
                'name': name,
                'type': item_type,
                'properties': properties or {}
            }
            
            return True
        except Exception as e:
            logger.error(f"Failed to create item {item_id}: {e}")
            return False
    
    def update_item_properties(self, item_id: str, properties: Dict) -> bool:
        """Update item properties"""
        try:
            db.execute_update(
                "UPDATE items SET properties = ? WHERE item_id = ?",
                (json.dumps(properties), item_id)
            )
            
            # Update cache
            if item_id in self.item_cache:
                self.item_cache[item_id]['properties'].update(properties)
            
            return True
        except Exception as e:
            logger.error(f"Failed to update item {item_id}: {e}")
            return False

# Global inventory system instance
inventory_system = InventorySystem()