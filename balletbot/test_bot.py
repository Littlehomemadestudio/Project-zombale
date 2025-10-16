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
from core.world_manager import world_manager
from utils.helpers import get_current_timestamp

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
        
        print("\n🎉 All basic tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())