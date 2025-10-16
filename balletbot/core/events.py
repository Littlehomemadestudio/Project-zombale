"""
Event system for BalletBot: Outbreak Dominion
Handles game events and notifications
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime

from utils.helpers import get_current_timestamp

logger = logging.getLogger(__name__)

@dataclass
class GameEvent:
    """Represents a game event"""
    id: str
    type: str
    timestamp: int
    data: Dict[str, Any]
    priority: int = 1  # 1 = low, 2 = medium, 3 = high

class EventSystem:
    """Manages game events and notifications"""
    
    def __init__(self):
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.event_queue: List[GameEvent] = []
        self.event_history: List[GameEvent] = []
        self.max_history = 1000
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for event type: {event_type}")
    
    def unregister_handler(self, event_type: str, handler: Callable):
        """Unregister an event handler"""
        if event_type in self.event_handlers:
            if handler in self.event_handlers[event_type]:
                self.event_handlers[event_type].remove(handler)
                logger.info(f"Unregistered handler for event type: {event_type}")
    
    def emit_event(self, event_type: str, data: Dict[str, Any], priority: int = 1):
        """Emit a game event"""
        event = GameEvent(
            id=f"event_{get_current_timestamp()}_{len(self.event_queue)}",
            type=event_type,
            timestamp=get_current_timestamp(),
            data=data,
            priority=priority
        )
        
        self.event_queue.append(event)
        self.event_history.append(event)
        
        # Trim history if too long
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        logger.debug(f"Emitted event: {event_type}")
    
    async def process_events(self):
        """Process all queued events"""
        while self.event_queue:
            event = self.event_queue.pop(0)
            await self._handle_event(event)
    
    async def _handle_event(self, event: GameEvent):
        """Handle a single event"""
        event_type = event.type
        
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")
        else:
            logger.debug(f"No handlers for event type: {event_type}")
    
    def get_events_by_type(self, event_type: str, limit: int = 100) -> List[GameEvent]:
        """Get recent events of a specific type"""
        events = [e for e in self.event_history if e.type == event_type]
        return events[-limit:] if events else []
    
    def get_events_by_priority(self, priority: int, limit: int = 100) -> List[GameEvent]:
        """Get recent events of a specific priority"""
        events = [e for e in self.event_history if e.priority == priority]
        return events[-limit:] if events else []
    
    def get_recent_events(self, limit: int = 100) -> List[GameEvent]:
        """Get recent events"""
        return self.event_history[-limit:] if self.event_history else []
    
    def clear_event_queue(self):
        """Clear the event queue"""
        self.event_queue.clear()
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get event system statistics"""
        event_counts = {}
        for event in self.event_history:
            event_counts[event.type] = event_counts.get(event.type, 0) + 1
        
        return {
            "total_events": len(self.event_history),
            "queued_events": len(self.event_queue),
            "event_types": len(event_counts),
            "event_counts": event_counts
        }

# Global event system instance
event_system = EventSystem()

# Common event types
EVENT_TYPES = {
    "player_created": "Player character created",
    "player_died": "Player died",
    "player_moved": "Player moved to new location",
    "combat_started": "Combat initiated",
    "combat_ended": "Combat finished",
    "zombie_spawned": "Zombie spawned",
    "zombie_killed": "Zombie killed",
    "item_crafted": "Item crafted",
    "building_entered": "Player entered building",
    "floor_cleared": "Building floor cleared",
    "vehicle_created": "Vehicle created",
    "vehicle_moved": "Vehicle moved",
    "radio_message": "Radio message sent",
    "spotter_used": "Spotter device used",
    "construction_started": "Construction started",
    "construction_completed": "Construction completed",
    "offline_mode_set": "Player set offline mode",
    "ambush_triggered": "Ambush triggered",
    "scavenge_success": "Scavenge successful",
    "map_purchased": "Map purchased",
    "intel_gathered": "Intelligence gathered"
}

# Event priorities
PRIORITY_LOW = 1
PRIORITY_MEDIUM = 2
PRIORITY_HIGH = 3
PRIORITY_CRITICAL = 4