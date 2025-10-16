"""
Crafting system for BalletBot: Outbreak Dominion
Handles item crafting and recipes
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from utils.helpers import get_current_timestamp
from utils.db import log_event
from config import RECIPES_PATH

logger = logging.getLogger(__name__)

class CraftingSystem:
    """Manages item crafting and recipes"""
    
    def __init__(self):
        self.recipes: Dict[str, Dict] = {}
        self._load_recipes()
    
    def _load_recipes(self):
        """Load recipes from JSON file"""
        try:
            recipes_path = Path(RECIPES_PATH)
            if recipes_path.exists():
                with open(recipes_path, 'r') as f:
                    self.recipes = json.load(f)
                logger.info(f"Loaded {len(self.recipes)} recipes")
            else:
                logger.warning(f"Recipes file not found: {RECIPES_PATH}")
        except Exception as e:
            logger.error(f"Failed to load recipes: {e}")
    
    def get_recipe(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get recipe for an item"""
        return self.recipes.get(item_id)
    
    def get_all_recipes(self) -> Dict[str, Dict[str, Any]]:
        """Get all available recipes"""
        return self.recipes
    
    def get_craftable_items(self, player_id: str) -> List[Dict[str, Any]]:
        """Get items that player can craft"""
        from systems.inventory_system import inventory_system
        from systems.player_system import player_system
        
        player = player_system.get_player(player_id)
        if not player:
            return []
        
        craftable = []
        
        for item_id, recipe in self.recipes.items():
            can_craft, missing = inventory_system.can_craft_item(player_id, recipe)
            if can_craft:
                craftable.append({
                    "item_id": item_id,
                    "name": recipe.get("name", item_id),
                    "recipe": recipe,
                    "missing_items": []
                })
            else:
                craftable.append({
                    "item_id": item_id,
                    "name": recipe.get("name", item_id),
                    "recipe": recipe,
                    "missing_items": missing
                })
        
        return craftable
    
    def craft_item(self, player_id: str, item_id: str) -> Dict[str, Any]:
        """Craft an item for a player"""
        from systems.inventory_system import inventory_system
        from systems.player_system import player_system
        
        # Get recipe
        recipe = self.get_recipe(item_id)
        if not recipe:
            return {"success": False, "error": f"Recipe not found for {item_id}"}
        
        # Check if player can craft
        can_craft, missing_items = inventory_system.can_craft_item(player_id, recipe)
        if not can_craft:
            return {
                "success": False, 
                "error": f"Cannot craft {item_id}",
                "missing_items": missing_items
            }
        
        # Check if player has required tools
        tools_required = recipe.get("tools_required", [])
        if tools_required:
            # TODO: Check if player has required tools
            pass
        
        # Consume materials
        if not inventory_system.consume_crafting_materials(player_id, recipe):
            return {"success": False, "error": "Failed to consume materials"}
        
        # Add crafted item
        if not inventory_system.add_item(player_id, item_id, 1):
            return {"success": False, "error": "Failed to add crafted item"}
        
        # Add intelligence gain
        intelligence_gain = recipe.get("intelligence", 0) // 10  # Small intelligence gain
        if intelligence_gain > 0:
            player_system.update_player_intelligence(player_id, intelligence_gain)
        
        # Log crafting event
        log_event("item_crafted", {
            "player_id": player_id,
            "item_id": item_id,
            "recipe": recipe,
            "intelligence_gain": intelligence_gain
        })
        
        return {
            "success": True,
            "item_id": item_id,
            "name": recipe.get("name", item_id),
            "intelligence_gain": intelligence_gain
        }
    
    def get_crafting_display(self, player_id: str) -> str:
        """Get formatted crafting display for player"""
        craftable_items = self.get_craftable_items(player_id)
        
        if not craftable_items:
            return "🔨 **Crafting**\nNo items available to craft."
        
        display = "🔨 **Available Recipes:**\n\n"
        
        for item in craftable_items:
            recipe = item["recipe"]
            name = item["name"]
            missing = item["missing_items"]
            
            if missing:
                display += f"❌ **{name}** (Missing: {', '.join(missing)})\n"
            else:
                display += f"✅ **{name}** - `/craft {item['item_id']}`\n"
                
                # Show required materials
                resources = recipe.get("resources", {})
                if resources:
                    materials = [f"{item} x{qty}" for item, qty in resources.items()]
                    display += f"   Materials: {', '.join(materials)}\n"
                
                # Show intelligence requirement
                intel_req = recipe.get("intelligence", 0)
                if intel_req > 0:
                    display += f"   Intelligence: {intel_req}\n"
                
                display += "\n"
        
        return display.strip()
    
    def get_recipe_display(self, item_id: str) -> str:
        """Get formatted recipe display"""
        recipe = self.get_recipe(item_id)
        if not recipe:
            return f"Recipe not found for {item_id}"
        
        name = recipe.get("name", item_id)
        resources = recipe.get("resources", {})
        intelligence = recipe.get("intelligence", 0)
        time_required = recipe.get("time_required", 0)
        tools = recipe.get("tools_required", [])
        
        display = f"🔨 **{name} Recipe**\n\n"
        
        if resources:
            display += "**Materials:**\n"
            for item, qty in resources.items():
                display += f"• {item} x{qty}\n"
            display += "\n"
        
        if intelligence > 0:
            display += f"**Intelligence Required:** {intelligence}\n"
        
        if time_required > 0:
            minutes = time_required // 60
            seconds = time_required % 60
            display += f"**Time Required:** {minutes}m {seconds}s\n"
        
        if tools:
            display += f"**Tools Required:** {', '.join(tools)}\n"
        
        return display.strip()
    
    def search_recipes(self, search_term: str) -> List[Dict[str, Any]]:
        """Search recipes by name or item_id"""
        search_term = search_term.lower()
        results = []
        
        for item_id, recipe in self.recipes.items():
            name = recipe.get("name", item_id).lower()
            if search_term in name or search_term in item_id.lower():
                results.append({
                    "item_id": item_id,
                    "name": recipe.get("name", item_id),
                    "recipe": recipe
                })
        
        return results
    
    def get_crafting_stats(self, player_id: str) -> Dict[str, Any]:
        """Get crafting statistics for a player"""
        from systems.player_system import player_system
        
        player = player_system.get_player(player_id)
        if not player:
            return {}
        
        intelligence = player.get("intelligence", 0)
        craftable_count = len([item for item in self.get_craftable_items(player_id) 
                              if not item["missing_items"]])
        
        return {
            "intelligence": intelligence,
            "craftable_items": craftable_count,
            "total_recipes": len(self.recipes),
            "crafting_level": intelligence // 10  # Simple level calculation
        }
    
    def create_recipe(self, item_id: str, name: str, resources: Dict[str, int],
                     intelligence: int = 0, time_required: int = 0,
                     tools_required: List[str] = None) -> bool:
        """Create a new recipe"""
        try:
            recipe = {
                "item_id": item_id,
                "name": name,
                "resources": resources,
                "intelligence": intelligence,
                "time_required": time_required,
                "tools_required": tools_required or []
            }
            
            self.recipes[item_id] = recipe
            
            # Save to file
            self._save_recipes()
            
            log_event("recipe_created", {
                "item_id": item_id,
                "name": name,
                "creator": "system"
            })
            
            return True
        except Exception as e:
            logger.error(f"Failed to create recipe {item_id}: {e}")
            return False
    
    def _save_recipes(self):
        """Save recipes to file"""
        try:
            recipes_path = Path(RECIPES_PATH)
            recipes_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(recipes_path, 'w') as f:
                json.dump(self.recipes, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save recipes: {e}")

# Global crafting system instance
crafting_system = CraftingSystem()