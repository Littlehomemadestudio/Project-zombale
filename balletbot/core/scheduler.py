"""
Scheduler for BalletBot: Outbreak Dominion
Manages game timing and periodic events
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp, is_night_time, get_day_phase
from config import WORLD_TICK_SECONDS, DAY_LENGTH_SECONDS

logger = logging.getLogger(__name__)

class Scheduler:
    """Manages game timing and periodic events"""
    
    def __init__(self, world_manager):
        self.world_manager = world_manager
        self.running = False
        self.tasks: List[asyncio.Task] = []
        self.last_world_tick = 0
        self.last_day_night_tick = 0
    
    async def start(self):
        """Start the scheduler"""
        try:
            self.running = True
            current_time = get_current_timestamp()
            self.last_world_tick = current_time
            self.last_day_night_tick = current_time
            
            # Start background tasks
            self.tasks = [
                asyncio.create_task(self._world_tick_loop()),
                asyncio.create_task(self._day_night_loop()),
                asyncio.create_task(self._cleanup_loop())
            ]
            
            logger.info("Scheduler started")
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler"""
        try:
            self.running = False
            
            # Cancel all tasks
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self.tasks, return_exceptions=True)
            
            logger.info("Scheduler stopped")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    async def _world_tick_loop(self):
        """Main world tick loop"""
        while self.running:
            try:
                current_time = get_current_timestamp()
                
                # Process world tick
                if current_time - self.last_world_tick >= WORLD_TICK_SECONDS:
                    await self._process_world_tick()
                    self.last_world_tick = current_time
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in world tick loop: {e}")
                await asyncio.sleep(30)
    
    async def _day_night_loop(self):
        """Day/night cycle processing"""
        while self.running:
            try:
                current_time = get_current_timestamp()
                
                # Process day/night changes
                if current_time - self.last_day_night_tick >= DAY_LENGTH_SECONDS // 4:  # Check 4 times per day
                    await self._process_day_night_change()
                    self.last_day_night_tick = current_time
                
                await asyncio.sleep(DAY_LENGTH_SECONDS // 4)
                
            except Exception as e:
                logger.error(f"Error in day/night loop: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_loop(self):
        """Cleanup expired pending actions and other maintenance"""
        while self.running:
            try:
                current_time = get_current_timestamp()
                
                # Clean up expired pending actions
                file_manager.clear_expired_actions(current_time)
                
                # Clean up offline modes
                from systems.offline_system import offline_system
                offline_system.cleanup_offline_modes()
                
                # Clean up building encounters
                from systems.building_system import building_system
                building_system.cleanup_expired_encounters()
                
                # Wait 5 minutes before next cleanup
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)
    
    async def _process_world_tick(self):
        """Process world tick events"""
        try:
            current_time = get_current_timestamp()
            is_night = is_night_time()
            
            # Process zombie spawning
            await self._process_zombie_spawning(is_night)
            
            # Process offline player actions
            await self._process_offline_actions()
            
            # Process construction progress
            await self._process_construction()
            
            # Process pending actions
            await self._process_pending_actions()
            
            # Log world tick
            file_manager.add_log("INFO", "World tick processed", timestamp=current_time, is_night=is_night)
            
        except Exception as e:
            logger.error(f"Error processing world tick: {e}")
    
    async def _process_zombie_spawning(self, is_night: bool):
        """Process zombie spawning for all regions"""
        try:
            from systems.zombie_system import zombie_system
            
            for region_name, region in self.world_manager.regions.items():
                # Calculate spawn probability
                spawn_prob = zombie_system.calculate_spawn_probability(
                    region.get('danger', 0),
                    0,  # noise level - could be calculated from player activity
                    is_night
                )
                
                # Roll for spawning
                import random
                if random.random() < spawn_prob:
                    # Spawn 1-3 zombies
                    spawn_count = random.randint(1, 3)
                    if is_night:
                        spawn_count = int(spawn_count * 1.5)  # More zombies at night
                    
                    zombie_system.spawn_zombies(region_name, spawn_count)
                    
                    logger.debug(f"Spawned {spawn_count} zombies in {region_name}")
            
        except Exception as e:
            logger.error(f"Error processing zombie spawning: {e}")
    
    async def _process_offline_actions(self):
        """Process offline player actions"""
        try:
            from systems.offline_system import offline_system
            from systems.player_system import player_system
            
            # Get all players in scavenge mode
            all_players = file_manager.get_all_players()
            for player_id, player_data in all_players.items():
                if player_data.get("offline_mode") == "scavenge":
                    # Process scavenge
                    result = offline_system.process_scavenge(player_id)
                    if result.get("success"):
                        logger.debug(f"Player {player_id} scavenged successfully")
            
        except Exception as e:
            logger.error(f"Error processing offline actions: {e}")
    
    async def _process_construction(self):
        """Process construction progress"""
        try:
            current_time = get_current_timestamp()
            construction_projects = file_manager.get_construction()
            
            for project in construction_projects:
                if project.get("status") != "in_progress":
                    continue
                
                start_time = project.get("start_time", 0)
                duration = project.get("duration", 0)
                
                if current_time >= start_time + duration:
                    # Construction completed
                    await self._complete_construction(project)
            
        except Exception as e:
            logger.error(f"Error processing construction: {e}")
    
    async def _complete_construction(self, project: Dict):
        """Complete a construction project"""
        try:
            from systems.construction_system import construction_system
            
            project_id = project.get("id")
            owner_id = project.get("owner_id")
            structure_type = project.get("structure_type")
            
            # Complete construction
            result = construction_system.complete_construction(project_id)
            
            if result.get("success"):
                logger.info(f"Construction {project_id} completed for player {owner_id}")
                
                # TODO: Notify player of completion
                
        except Exception as e:
            logger.error(f"Error completing construction: {e}")
    
    async def _process_pending_actions(self):
        """Process pending actions"""
        try:
            current_time = get_current_timestamp()
            pending_actions = file_manager.get_pending_actions()
            
            for action in pending_actions:
                if current_time >= action.get("expire_at", 0):
                    await self._process_expired_action(action)
            
        except Exception as e:
            logger.error(f"Error processing pending actions: {e}")
    
    async def _process_expired_action(self, action: Dict):
        """Process an expired pending action"""
        try:
            action_type = action.get("action_type")
            payload = action.get("payload", {})
            
            if action_type == "encounter_timeout":
                # Handle building encounter timeout
                from systems.building_system import building_system
                encounter_id = payload.get("encounter_id")
                default_action = payload.get("default_action", "sneak")
                
                if encounter_id:
                    building_system.process_encounter_action(
                        action.get("player_id"), 
                        default_action, 
                        encounter_id
                    )
            
            # Remove expired action
            file_manager.remove_pending_action(action.get("id"))
            
        except Exception as e:
            logger.error(f"Error processing expired action: {e}")
    
    async def _process_day_night_change(self):
        """Process day/night cycle changes"""
        try:
            current_time = get_current_timestamp()
            is_night = is_night_time()
            day_phase = get_day_phase()
            
            # Log day/night change
            file_manager.add_log("INFO", f"Day/night cycle: {day_phase}", timestamp=current_time, is_night=is_night)
            
            # Apply day/night modifiers
            if is_night:
                # Night bonuses/penalties
                logger.debug("Night time - applying night modifiers")
            else:
                # Day bonuses/penalties
                logger.debug("Day time - applying day modifiers")
            
        except Exception as e:
            logger.error(f"Error processing day/night change: {e}")
    
    def add_pending_action(self, player_id: str, action_type: str, payload: Dict, expire_time: int):
        """Add a pending action"""
        try:
            action_data = {
                "id": f"pending_{get_current_timestamp()}_{player_id}",
                "player_id": player_id,
                "action_type": action_type,
                "payload": payload,
                "expire_at": expire_time,
                "created_at": get_current_timestamp()
            }
            
            file_manager.add_pending_action(action_data)
            
        except Exception as e:
            logger.error(f"Error adding pending action: {e}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "running": self.running,
            "active_tasks": len(self.tasks),
            "last_world_tick": self.last_world_tick,
            "last_day_night_tick": self.last_day_night_tick
        }

# Global scheduler instance
scheduler = None  # Will be initialized in main.py