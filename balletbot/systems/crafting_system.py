"""
Crafting system for BalletBot: Outbreak Dominion
Manages item crafting and recipes
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp, add_action_to_history

logger = logging.getLogger(__name__)

class CraftingSystem:
    """Manages item crafting and recipes"""
    
    def __init__(self):
        self.recipes: Dict[str, Dict] = {}
        self._load_recipes()
    
    def _load_recipes(self):
        """Load recipes from JSON file"""
        try:
            with open("data/recipes.json", "r", encoding="utf-8") as f:
                self.recipes = json.load(f)
            logger.info(f"Loaded {len(self.recipes)} recipes")
        except Exception as e:
            logger.error(f"Error loading recipes: {e}")
            self.recipes = {}
    
    def get_recipe(self, item_id: str) -> Optional[Dict]:
        """Get recipe for item"""
        return self.recipes.get(item_id)
    
    def get_all_recipes(self) -> Dict[str, Dict]:
        """Get all recipes"""
        return self.recipes.copy()
    
    def get_craftable_items(self, player_id: str) -> List[Dict]:
        """Get items player can craft"""
        try:
            from systems.inventory_system import inventory_system
            from systems.player_system import player_system
            
            player_data = player_system.get_player(player_id)
            if not player_data:
                return []
            
            craftable_items = []
            
            for item_id, recipe in self.recipes.items():
                can_craft, missing_items = inventory_system.can_craft_item(player_id, recipe)
                
                craftable_items.append({
                    "item_id": item_id,
                    "name": recipe.get("name", item_id),
                    "can_craft": can_craft,
                    "missing_items": missing_items,
                    "recipe": recipe
                })
            
            return craftable_items
            
        except Exception as e:
            logger.error(f"Error getting craftable items for player {player_id}: {e}")
            return []
    
    def craft_item(self, player_id: str, item_id: str) -> Dict[str, Any]:
        """Craft an item"""
        try:
            from systems.inventory_system import inventory_system
            from systems.player_system import player_system
            
            # Get recipe
            recipe = self.get_recipe(item_id)
            if not recipe:
                return {"success": False, "error": f"Recipe for {item_id} not found"}
            
            # Check if player can craft
            can_craft, missing_items = inventory_system.can_craft_item(player_id, recipe)
            if not can_craft:
                return {
                    "success": False, 
                    "error": f"Cannot craft {item_id}. Missing: {', '.join(missing_items)}"
                }
            
            # Check cooldown
            if not player_system.check_cooldown(player_id, "craft"):
                return {"success": False, "error": "Crafting is on cooldown"}
            
            # Consume materials
            if not inventory_system.consume_crafting_materials(player_id, recipe):
                return {"success": False, "error": "Failed to consume materials"}
            
            # Add crafted item
            quantity = recipe.get("quantity", 1)
            if not inventory_system.add_item(player_id, item_id, quantity):
                return {"success": False, "error": "Failed to add crafted item"}
            
            # Set cooldown
            player_system.set_cooldown(player_id, "craft")
            
            # Add to action history
            add_action_to_history(player_id, "item_crafted", item_id=item_id, quantity=quantity)
            
            # Update intelligence
            intelligence_gain = recipe.get("intelligence_gain", 1)
            if intelligence_gain > 0:
                player_system.update_intelligence(player_id, intelligence_gain)
            
            logger.info(f"Player {player_id} crafted {item_id} x{quantity}")
            
            return {
                "success": True,
                "item_id": item_id,
                "quantity": quantity,
                "message": f"✅ Successfully crafted {recipe.get('name', item_id)} x{quantity}"
            }
            
        except Exception as e:
            logger.error(f"Error crafting item {item_id} for player {player_id}: {e}")
            return {"success": False, "error": "Failed to craft item"}
    
    def get_recipe_info(self, item_id: str) -> str:
        """Get formatted recipe information"""
        recipe = self.get_recipe(item_id)
        if not recipe:
            return f"❌ Recipe for {item_id} not found"
        
        from utils.helpers import format_recipe_info
        return format_recipe_info(recipe)
    
    def format_craftable_items(self, player_id: str) -> str:
        """Format craftable items for display"""
        craftable_items = self.get_craftable_items(player_id)
        
        if not craftable_items:
            return "🔧 **No craftable items available**"
        
        display = "🔧 **Craftable Items:**\n\n"
        
        for item in craftable_items:
            if item["can_craft"]:
                display += f"✅ **{item['name']}**\n"
            else:
                display += f"❌ **{item['name']}**\n"
                display += f"   Missing: {', '.join(item['missing_items'])}\n"
            
            # Show recipe requirements
            recipe = item["recipe"]
            resources = recipe.get("resources", {})
            if resources:
                display += "   Resources: "
                resource_list = [f"{resource} x{qty}" for resource, qty in resources.items()]
                display += ", ".join(resource_list) + "\n"
            
            intelligence = recipe.get("intelligence", 0)
            if intelligence > 0:
                display += f"   Intelligence: {intelligence}\n"
            
            time_required = recipe.get("time_required", 0)
            if time_required > 0:
                display += f"   Time: {time_required}s\n"
            
            display += "\n"
        
        return display
    
    def search_recipes(self, query: str) -> List[Dict]:
        """Search recipes by name or item"""
        query = query.lower()
        results = []
        
        for item_id, recipe in self.recipes.items():
            name = recipe.get("name", "").lower()
            if query in name or query in item_id.lower():
                results.append({
                    "item_id": item_id,
                    "name": recipe.get("name", item_id),
                    "recipe": recipe
                })
        
        return results
    
    def create_recipe(self, item_id: str, recipe_data: Dict) -> bool:
        """Create a new recipe"""
        try:
            self.recipes[item_id] = recipe_data
            self._save_recipes()
            logger.info(f"Created recipe for {item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating recipe for {item_id}: {e}")
            return False
    
    def _save_recipes(self):
        """Save recipes to file"""
        try:
            with open("data/recipes.json", "w", encoding="utf-8") as f:
                json.dump(self.recipes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving recipes: {e}")
    
    def get_recipe_requirements(self, item_id: str) -> Dict[str, Any]:
        """Get recipe requirements"""
        recipe = self.get_recipe(item_id)
        if not recipe:
            return {}
        
        return {
            "resources": recipe.get("resources", {}),
            "intelligence": recipe.get("intelligence", 0),
            "time_required": recipe.get("time_required", 0),
            "tools_required": recipe.get("tools_required", []),
            "quantity": recipe.get("quantity", 1)
        }
    
    def can_craft_with_intelligence(self, player_id: str, item_id: str) -> bool:
        """Check if player can craft item based on intelligence"""
        try:
            from systems.player_system import player_system
            
            recipe = self.get_recipe(item_id)
            if not recipe:
                return False
            
            required_intelligence = recipe.get("intelligence", 0)
            if required_intelligence == 0:
                return True
            
            player_data = player_system.get_player(player_id)
            if not player_data:
                return False
            
            player_intelligence = player_data.get("intelligence", 0)
            return player_intelligence >= required_intelligence
            
        except Exception as e:
            logger.error(f"Error checking intelligence for crafting: {e}")
            return False
    
    def get_crafting_time(self, item_id: str) -> int:
        """Get crafting time for item"""
        recipe = self.get_recipe(item_id)
        if not recipe:
            return 0
        
        return recipe.get("time_required", 0)
    
    def get_crafting_xp(self, item_id: str) -> int:
        """Get XP gained from crafting item"""
        recipe = self.get_recipe(item_id)
        if not recipe:
            return 0
        
        return recipe.get("intelligence_gain", 1)
    
    def format_recipe_detailed(self, item_id: str) -> str:
        """Format detailed recipe information"""
        recipe = self.get_recipe(item_id)
        if not recipe:
            return f"❌ Recipe for {item_id} not found"
        
        display = f"🔧 **{recipe.get('name', item_id)} Recipe**\n\n"
        
        # Resources
        resources = recipe.get("resources", {})
        if resources:
            display += "📦 **Resources needed:**\n"
            for resource, qty in resources.items():
                display += f"• {resource} x{qty}\n"
            display += "\n"
        
        # Intelligence requirement
        intelligence = recipe.get("intelligence", 0)
        if intelligence > 0:
            display += f"🧠 **Intelligence required:** {intelligence}\n\n"
        
        # Time requirement
        time_required = recipe.get("time_required", 0)
        if time_required > 0:
            display += f"⏱️ **Crafting time:** {time_required} seconds\n\n"
        
        # Tools required
        tools = recipe.get("tools_required", [])
        if tools:
            display += "🔨 **Tools required:**\n"
            for tool in tools:
                display += f"• {tool}\n"
            display += "\n"
        
        # Quantity
        quantity = recipe.get("quantity", 1)
        display += f"📦 **Quantity produced:** {quantity}\n"
        
        # XP gain
        xp_gain = recipe.get("intelligence_gain", 1)
        if xp_gain > 0:
            display += f"🧠 **XP gained:** {xp_gain}\n"
        
        return display
    
    def get_available_recipes_by_type(self, player_id: str, item_type: str) -> List[Dict]:
        """Get available recipes by item type"""
        try:
            from systems.inventory_system import inventory_system
            
            available_recipes = []
            
            for item_id, recipe in self.recipes.items():
                # Check if recipe produces item of requested type
                if recipe.get("type") == item_type:
                    can_craft, missing_items = inventory_system.can_craft_item(player_id, recipe)
                    available_recipes.append({
                        "item_id": item_id,
                        "name": recipe.get("name", item_id),
                        "can_craft": can_craft,
                        "missing_items": missing_items,
                        "recipe": recipe
                    })
            
            return available_recipes
            
        except Exception as e:
            logger.error(f"Error getting recipes by type for player {player_id}: {e}")
            return []
    
    def get_crafting_progress(self, player_id: str) -> Dict[str, Any]:
        """Get player's crafting progress"""
        try:
            from systems.player_system import player_system
            
            player_data = player_system.get_player(player_id)
            if not player_data:
                return {}
            
            # Get action history for crafting
            from utils.helpers import get_action_history
            actions = get_action_history(player_id, 50)
            
            crafted_items = {}
            for action in actions:
                if action.get("action") == "item_crafted":
                    item_id = action.get("item_id")
                    if item_id:
                        crafted_items[item_id] = crafted_items.get(item_id, 0) + 1
            
            return {
                "total_crafted": sum(crafted_items.values()),
                "unique_items": len(crafted_items),
                "crafted_items": crafted_items,
                "intelligence": player_data.get("intelligence", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting crafting progress for player {player_id}: {e}")
            return {}

# Global crafting system instance
crafting_system = CraftingSystem()