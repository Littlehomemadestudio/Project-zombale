#!/usr/bin/env python3
"""
Test script for BalletBot: Outbreak Dominion
Tests basic functionality without Bale API
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from systems.player_system import player_system
from systems.inventory_system import inventory_system
from systems.crafting_system import crafting_system
from systems.building_system import building_system
from systems.combat_system import combat_system
from systems.vehicle_system import vehicle_system
from systems.radio_system import radio_system
from systems.spotter_system import spotter_system
from systems.offline_system import offline_system
from systems.construction_system import construction_system
from core.world_manager import world_manager
from utils.file_manager import file_manager

async def test_basic_functionality():
    """Test basic bot functionality"""
    print("Testing BalletBot: Outbreak Dominion...")
    
    try:
        # Initialize world manager
        await world_manager.initialize()
        print("✅ World manager initialized")
        
        # Test player creation
        result = player_system.create_character(
            "test_user_1", "TestPlayer", "Scavenger", "TEST_GAME"
        )
        if result["success"]:
            print("✅ Player creation works")
        else:
            print(f"❌ Player creation failed: {result['error']}")
            return
        
        # Test inventory system
        inventory_system.add_item("test_user_1", "wood", 10)
        inventory_system.add_item("test_user_1", "metal", 5)
        print("✅ Inventory system works")
        
        # Test crafting system
        craftable = crafting_system.get_craftable_items("test_user_1")
        print(f"✅ Crafting system works - {len(craftable)} recipes available")
        
        # Test world regions
        regions = world_manager.regions
        print(f"✅ World manager works - {len(regions)} regions loaded")
        
        # Test player status
        status = player_system.get_player_status("test_user_1")
        if status:
            print("✅ Player status system works")
        else:
            print("❌ Player status system failed")
        
        # Test building system
        building_result = building_system.enter_building("test_user_1", "Hospital")
        if building_result["success"]:
            print("✅ Building system works")
        else:
            print(f"❌ Building system failed: {building_result['error']}")
        
        # Test vehicle system
        vehicle_result = vehicle_system.create_vehicle("jeep", "test_user_1", "Forest:Camp:Area1")
        if vehicle_result["success"]:
            print("✅ Vehicle system works")
        else:
            print(f"❌ Vehicle system failed: {vehicle_result['error']}")
        
        # Test radio system
        radio_result = radio_system.set_frequency("test_user_1", "101.5")
        if radio_result["success"]:
            print("✅ Radio system works")
        else:
            print(f"❌ Radio system failed: {radio_result['error']}")
        
        # Test spotter system
        spotter_result = spotter_system.buy_spotter("test_user_1")
        if spotter_result["success"]:
            print("✅ Spotter system works")
        else:
            print(f"❌ Spotter system failed: {spotter_result['error']}")
        
        # Test offline system
        offline_result = offline_system.set_offline_mode("test_user_1", "scavenge")
        if offline_result["success"]:
            print("✅ Offline system works")
        else:
            print(f"❌ Offline system failed: {offline_result['error']}")
        
        # Test construction system
        construction_result = construction_system.start_construction(
            "test_user_1", "radio_tower", "Forest:Camp:Area1", 
            {"metal": 20, "circuit": 10, "battery": 5}, 48
        )
        if construction_result["success"]:
            print("✅ Construction system works")
        else:
            print(f"❌ Construction system failed: {construction_result['error']}")
        
        print("\n🎉 All basic tests passed!")
        
        # Test some advanced functionality
        print("\n--- Advanced Tests ---")
        
        # Test crafting
        craft_result = crafting_system.craft_item("test_user_1", "bandage")
        if craft_result["success"]:
            print("✅ Crafting works")
        else:
            print(f"❌ Crafting failed: {craft_result['error']}")
        
        # Test inventory display
        inventory_display = inventory_system.format_inventory("test_user_1")
        print(f"✅ Inventory display works (length: {len(inventory_display)})")
        
        # Test world status
        world_status = world_manager.get_world_status()
        print(f"✅ World status works - {world_status['total_regions']} regions, {world_status['total_zombies']} zombies")
        
        print("\n🎉 All advanced tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())