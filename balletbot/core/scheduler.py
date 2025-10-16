"""
Scheduler for BalletBot: Outbreak Dominion
Handles game timing, day/night cycles, and periodic events
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from utils.helpers import get_current_timestamp, is_night_time, get_day_phase
from utils.db import db, log_event
from config import DAY_LENGTH_SECONDS, WORLD_TICK_SECONDS, TIME_MULTIPLIER

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
        logger.info("Starting game scheduler...")
        self.running = True
        
        # Start world tick task
        world_tick_task = asyncio.create_task(self._world_tick_loop())
        self.tasks.append(world_tick_task)
        
        # Start day/night cycle task
        day_night_task = asyncio.create_task(self._day_night_loop())
        self.tasks.append(day_night_task)
        
        # Start pending actions cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.tasks.append(cleanup_task)
        
        logger.info("Scheduler started successfully")
    
    async def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler...")
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
        
        logger.info("Scheduler stopped")
    
    async def _world_tick_loop(self):
        """Main world processing loop"""
        while self.running:
            try:
                current_time = get_current_timestamp()
                
                # Only process if enough time has passed
                if current_time - self.last_world_tick >= WORLD_TICK_SECONDS:
                    await self._process_world_tick()
                    self.last_world_tick = current_time
                
                # Sleep for a short time to prevent busy waiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in world tick loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
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
                await self._cleanup_expired_actions()
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)
    
    async def _process_world_tick(self):
        """Process a single world tick"""
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
        
        log_event("world_tick", {
            "timestamp": current_time,
            "is_night": is_night,
            "day_phase": get_day_phase()
        })
    
    async def _process_zombie_spawning(self, is_night: bool):
        """Process zombie spawning for all regions"""
        from systems.zombie_system import zombie_system
        
        for region_name, region in self.world_manager.regions.items():
            # Calculate spawn probability
            spawn_prob = zombie_system.calculate_spawn_probability(
                region.get('danger', 0),
                0,  # noise level - could be calculated from player activity
                is_night
            )
            
            # Spawn zombies based on probability
            if spawn_prob > 0:
                zombies_to_spawn = zombie_system.calculate_zombie_spawn_count(spawn_prob)
                if zombies_to_spawn > 0:
                    self.world_manager.update_region_zombies(region_name, zombies_to_spawn)
                    logger.info(f"Spawned {zombies_to_spawn} zombies in {region_name}")
    
    async def _process_offline_actions(self):
        """Process offline player actions (ambush, scavenge)"""
        from systems.offline_system import offline_system
        
        # Get all players in offline mode
        offline_players = db.execute_query("""
            SELECT * FROM players 
            WHERE offline_mode != 'none' AND status = 'alive'
        """)
        
        for player in offline_players:
            await offline_system.process_offline_player(player)
    
    async def _process_construction(self):
        """Process ongoing construction projects"""
        current_time = get_current_timestamp()
        
        # Get all in-progress construction
        constructions = db.execute_query("""
            SELECT * FROM construction 
            WHERE status = 'in_progress'
        """)
        
        for construction in constructions:
            if current_time >= construction['start_time'] + construction['duration']:
                # Construction completed
                await self._complete_construction(construction)
    
    async def _complete_construction(self, construction: Dict[str, Any]):
        """Complete a construction project"""
        from systems.construction_system import construction_system
        
        success = await construction_system.complete_construction(construction['id'])
        if success:
            logger.info(f"Completed construction: {construction['structure_type']} for player {construction['owner_id']}")
        else:
            logger.error(f"Failed to complete construction: {construction['id']}")
    
    async def _process_pending_actions(self):
        """Process pending actions that are ready to execute"""
        current_time = get_current_timestamp()
        
        # Get expired pending actions
        expired_actions = db.execute_query("""
            SELECT * FROM pending_actions 
            WHERE expire_at <= ?
        """, (current_time,))
        
        for action in expired_actions:
            await self._execute_pending_action(action)
    
    async def _execute_pending_action(self, action: Dict[str, Any]):
        """Execute a pending action"""
        from systems.combat_system import combat_system
        
        action_type = action['action_type']
        payload = action.get('payload', {})
        player_id = action['player_id']
        
        try:
            if action_type == 'combat_timeout':
                # Default to sneak attempt (which will fail)
                await combat_system.handle_combat_timeout(player_id, payload)
            elif action_type == 'ambush_trigger':
                await combat_system.handle_ambush_trigger(player_id, payload)
            
            # Remove the action
            db.execute_update("DELETE FROM pending_actions WHERE id = ?", (action['id'],))
            
        except Exception as e:
            logger.error(f"Error executing pending action {action['id']}: {e}")
    
    async def _process_day_night_change(self):
        """Process day/night cycle changes"""
        current_phase = get_day_phase()
        
        # Log phase change
        log_event("day_night_change", {
            "phase": current_phase,
            "timestamp": get_current_timestamp()
        })
        
        # Apply day/night effects to players
        await self._apply_day_night_effects(current_phase)
    
    async def _apply_day_night_effects(self, phase: str):
        """Apply day/night effects to players"""
        # Night effects: reduced stamina regeneration, increased infection risk
        if phase == "night":
            # Could implement night-specific effects here
            pass
        else:
            # Day effects: normal stamina regeneration
            pass
    
    async def _cleanup_expired_actions(self):
        """Clean up expired pending actions"""
        current_time = get_current_timestamp()
        
        # Delete actions that expired more than 1 hour ago
        deleted = db.execute_update("""
            DELETE FROM pending_actions 
            WHERE expire_at < ? - 3600
        """, (current_time,))
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} expired pending actions")
    
    def create_pending_action(self, player_id: str, action_type: str, 
                            payload: Dict[str, Any], expire_seconds: int) -> int:
        """Create a pending action"""
        current_time = get_current_timestamp()
        expire_at = current_time + expire_seconds
        
        try:
            cursor = db.execute_update("""
                INSERT INTO pending_actions (player_id, action_type, payload, expire_at, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (player_id, action_type, json.dumps(payload), expire_at, current_time))
            
            # Get the inserted ID
            result = db.execute_one("SELECT last_insert_rowid() as id")
            return result['id'] if result else 0
            
        except Exception as e:
            logger.error(f"Failed to create pending action: {e}")
            return 0
    
    def get_pending_actions(self, player_id: str) -> List[Dict[str, Any]]:
        """Get pending actions for a player"""
        return db.execute_query("""
            SELECT * FROM pending_actions 
            WHERE player_id = ? AND expire_at > ?
            ORDER BY expire_at ASC
        """, (player_id, get_current_timestamp()))
    
    def cancel_pending_action(self, action_id: int) -> bool:
        """Cancel a pending action"""
        try:
            deleted = db.execute_update("DELETE FROM pending_actions WHERE id = ?", (action_id,))
            return deleted > 0
        except Exception as e:
            logger.error(f"Failed to cancel pending action {action_id}: {e}")
            return False
    
    def get_game_time_info(self) -> Dict[str, Any]:
        """Get current game time information"""
        current_time = get_current_timestamp()
        is_night = is_night_time()
        phase = get_day_phase()
        
        # Calculate day progress (0.0 to 1.0)
        day_progress = (current_time % DAY_LENGTH_SECONDS) / DAY_LENGTH_SECONDS
        
        return {
            "current_time": current_time,
            "is_night": is_night,
            "phase": phase,
            "day_progress": day_progress,
            "time_multiplier": TIME_MULTIPLIER
        }