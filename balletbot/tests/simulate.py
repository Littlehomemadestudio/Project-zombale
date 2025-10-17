#!/usr/bin/env python3
"""
Simulation script for BalletBot: Outbreak Dominion
Creates test players and simulates game activity
"""

import asyncio
import random
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from systems.player_system import player_system
from systems.inventory_system import inventory_system
from systems.combat_system import combat_system
from systems.zombie_system import zombie_system
from core.world_manager import world_manager
from core.scheduler import scheduler
from utils.helpers import get_current_timestamp

class GameSimulator:
    """Simulates game activity for testing"""
    
    def __init__(self):
        self.test_players = []
        self.simulation_running = False
    
    async def create_test_players(self, count: int = 10):
        """Create test players"""
        print(f"Creating {count} test players...")
        
        classes = ["Scavenger", "Mechanic", "Soldier"]
        
        for i in range(count):
            player_id = f"test_player_{i}"
            username = f"TestPlayer{i}"
            char_class = random.choice(classes)
            
            result = player_system.create_character(
                player_id, username, char_class, "TEST_GAME"
            )
            
            if result["success"]:
                self.test_players.append(player_id)
                print(f"Created {username} ({char_class})")
            else:
                print(f"Failed to create player {i}: {result['error']}")
    
    async def simulate_player_activity(self, player_id: str):
        """Simulate activity for a single player"""
        player = player_system.get_player(player_id)
        if not player:
            return
        
        # Random actions
        actions = [
            self._simulate_movement,
            self._simulate_looting,
            self._simulate_crafting,
            self._simulate_combat
        ]
        
        action = random.choice(actions)
        await action(player_id)
    
    async def _simulate_movement(self, player_id: str):
        """Simulate player movement"""
        from core.world_manager import world_manager
        
        player = player_system.get_player(player_id)
        if not player:
            return
        
        current_location = player.get("location", "Forest:Camp:Area1")
        region = current_location.split(":")[0]
        
        # Get connected regions
        connected = world_manager.get_connected_regions(region)
        if connected:
            new_region = random.choice(connected)
            new_location = f"{new_region}:Camp:Area1"
            
            if player_system.move_player(player_id, new_location):
                print(f"Player {player_id} moved to {new_location}")
    
    async def _simulate_looting(self, player_id: str):
        """Simulate looting activity"""
        # Random chance to find items
        if random.random() < 0.3:  # 30% chance
            loot_items = [
                ("wood", random.randint(1, 3)),
                ("metal", random.randint(1, 2)),
                ("cloth", random.randint(1, 2)),
                ("ammo", random.randint(1, 5))
            ]
            
            for item_id, quantity in loot_items:
                if random.random() < 0.5:  # 50% chance for each item
                    inventory_system.add_item(player_id, item_id, quantity)
            
            print(f"Player {player_id} found some loot")
    
    async def _simulate_crafting(self, player_id: str):
        """Simulate crafting activity"""
        from systems.crafting_system import crafting_system
        
        # Get craftable items
        craftable = crafting_system.get_craftable_items(player_id)
        
        # Try to craft a random item
        for item in craftable:
            if not item["missing_items"]:  # Can craft
                if random.random() < 0.2:  # 20% chance
                    result = crafting_system.craft_item(player_id, item["item_id"])
                    if result["success"]:
                        print(f"Player {player_id} crafted {item['name']}")
                    break
    
    async def _simulate_combat(self, player_id: str):
        """Simulate combat with zombies"""
        player = player_system.get_player(player_id)
        if not player:
            return
        
        location = player.get("location", "")
        region = location.split(":")[0]
        
        # Check if there are zombies in the region
        region_info = world_manager.get_region(region)
        if region_info and region_info.get("zombies", 0) > 0:
            # Generate zombie encounter
            zombie = zombie_system.generate_zombie(region.lower())
            
            # Start combat
            combat = combat_system.initiate_combat(player_id, zombie["id"], "pvz")
            
            # Process attack
            attack_data = {
                "weapon_damage": 25,
                "zombie": zombie
            }
            
            result = combat_system.process_combat_turn(combat["id"], "attack", attack_data)
            
            if result.get("combat_ended") and result.get("winner") == player_id:
                print(f"Player {player_id} defeated a zombie")
            else:
                print(f"Player {player_id} is in combat")
    
    async def run_simulation(self, duration_minutes: int = 5):
        """Run simulation for specified duration"""
        print(f"Starting simulation for {duration_minutes} minutes...")
        self.simulation_running = True
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        tick_count = 0
        
        while time.time() < end_time and self.simulation_running:
            tick_count += 1
            print(f"\n--- Simulation Tick {tick_count} ---")
            
            # Simulate activity for each player
            for player_id in self.test_players:
                if random.random() < 0.7:  # 70% chance of activity
                    await self.simulate_player_activity(player_id)
            
            # Wait before next tick
            await asyncio.sleep(10)  # 10 second ticks
        
        print(f"\nSimulation completed after {tick_count} ticks")
        await self.print_simulation_summary()
    
    async def print_simulation_summary(self):
        """Print simulation summary"""
        print("\n=== SIMULATION SUMMARY ===")
        
        # Player stats
        print(f"Total test players: {len(self.test_players)}")
        
        for player_id in self.test_players:
            player = player_system.get_player(player_id)
            if player:
                inventory = inventory_system.get_player_inventory(player_id)
                print(f"\n{player['username']} ({player['class']}):")
                print(f"  Location: {player['location']}")
                print(f"  HP: {player['hp']}/100")
                print(f"  Intelligence: {player['intelligence']}")
                print(f"  Inventory items: {len(inventory)}")
        
        # World stats
        world_status = world_manager.get_world_status()
        print(f"\nWorld Status:")
        print(f"  Total regions: {world_status['total_regions']}")
        print(f"  Total zombies: {world_status['total_zombies']}")
        print(f"  Active games: {world_status['active_games']}")

async def main():
    """Main simulation function"""
    print("BalletBot: Outbreak Dominion - Simulation")
    print("=" * 50)
    
    # Initialize systems
    await world_manager.initialize()
    await scheduler.start()
    
    # Create simulator
    simulator = GameSimulator()
    
    try:
        # Create test players
        await simulator.create_test_players(5)
        
        # Run simulation
        await simulator.run_simulation(2)  # 2 minutes
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    except Exception as e:
        print(f"Simulation error: {e}")
    finally:
        # Cleanup
        await scheduler.stop()
        print("Simulation ended")

if __name__ == "__main__":
    asyncio.run(main())