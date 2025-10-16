"""
Game loop for BalletBot: Outbreak Dominion
Handles message processing and command routing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

from bale_api import bale_api
from utils.helpers import sanitize_input, get_current_timestamp
from utils.db import log_event

logger = logging.getLogger(__name__)

class GameLoop:
    """Main game loop that handles messages and commands"""
    
    def __init__(self, bale_api, world_manager, scheduler):
        self.bale_api = bale_api
        self.world_manager = world_manager
        self.scheduler = scheduler
        self.running = False
        
        # Register command handlers
        self._register_commands()
    
    def _register_commands(self):
        """Register all command handlers"""
        # Admin commands
        self.bale_api.command("start_season")(self._handle_start_season)
        self.bale_api.command("announce")(self._handle_announce)
        self.bale_api.command("pause_world")(self._handle_pause_world)
        self.bale_api.command("resume_world")(self._handle_resume_world)
        self.bale_api.command("reset_world")(self._handle_reset_world)
        
        # Player commands
        self.bale_api.command("join")(self._handle_join)
        self.bale_api.command("create_character")(self._handle_create_character)
        self.bale_api.command("status")(self._handle_status)
        self.bale_api.command("map")(self._handle_map)
        self.bale_api.command("move")(self._handle_move)
        self.bale_api.command("loot")(self._handle_loot)
        self.bale_api.command("enter")(self._handle_enter)
        self.bale_api.command("floor")(self._handle_floor)
        self.bale_api.command("sneak")(self._handle_sneak)
        self.bale_api.command("attack")(self._handle_attack)
        self.bale_api.command("reload")(self._handle_reload)
        self.bale_api.command("craft")(self._handle_craft)
        self.bale_api.command("build")(self._handle_build)
        self.bale_api.command("setmode")(self._handle_setmode)
        self.bale_api.command("seek")(self._handle_seek)
        self.bale_api.command("radio")(self._handle_radio)
        self.bale_api.command("setfreq")(self._handle_setfreq)
        self.bale_api.command("intel")(self._handle_intel)
        self.bale_api.command("mine")(self._handle_mine)
        self.bale_api.command("chop")(self._handle_chop)
        self.bale_api.command("vehicle")(self._handle_vehicle)
        self.bale_api.command("store")(self._handle_store)
        self.bale_api.command("retrieve")(self._handle_retrieve)
        self.bale_api.command("ally")(self._handle_ally)
        
        # Admin-only commands
        self.bale_api.command("admin")(self._handle_admin)
    
    async def start(self):
        """Start the game loop"""
        logger.info("Starting game loop...")
        self.running = True
        
        # Start Bale API polling
        await self.bale_api.start_polling()
        
        logger.info("Game loop started successfully")
    
    async def stop(self):
        """Stop the game loop"""
        logger.info("Stopping game loop...")
        self.running = False
        await self.bale_api.stop_polling()
        logger.info("Game loop stopped")
    
    # Admin command handlers
    async def _handle_start_season(self, message):
        """Start a new game season"""
        if not await self._is_admin(message):
            await self._send_error(message, "Admin access required")
            return
        
        from utils.helpers import generate_game_code
        from systems.player_system import player_system
        
        game_code = generate_game_code()
        admin_id = message.user.id
        
        # Create game
        game_data = self.world_manager.create_game(game_code, admin_id)
        
        await self._send_message(message, f"🎮 **New Season Started!**\n\nGame Code: `{game_code}`\nPlayers can join with: `/join {game_code}`")
        
        log_event("season_started", {
            "game_code": game_code,
            "admin_id": admin_id,
            "chat_id": message.chat_id
        })
    
    async def _handle_announce(self, message):
        """Make an announcement"""
        if not await self._is_admin(message):
            await self._send_error(message, "Admin access required")
            return
        
        text = message.text.split(' ', 1)[1] if ' ' in message.text else ""
        if not text:
            await self._send_error(message, "Usage: /announce <message>")
            return
        
        await self._send_message(message, f"📢 **ANNOUNCEMENT:**\n{text}")
    
    async def _handle_pause_world(self, message):
        """Pause the world"""
        if not await self._is_admin(message):
            await self._send_error(message, "Admin access required")
            return
        
        # TODO: Implement world pausing
        await self._send_message(message, "⏸️ World paused")
    
    async def _handle_resume_world(self, message):
        """Resume the world"""
        if not await self._is_admin(message):
            await self._send_error(message, "Admin access required")
            return
        
        # TODO: Implement world resuming
        await self._send_message(message, "▶️ World resumed")
    
    async def _handle_reset_world(self, message):
        """Reset the world"""
        if not await self._is_admin(message):
            await self._send_error(message, "Admin access required")
            return
        
        # TODO: Implement world reset with confirmation
        await self._send_message(message, "🔄 World reset (not implemented yet)")
    
    # Player command handlers
    async def _handle_join(self, message):
        """Join a game"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        parts = message.text.split()
        if len(parts) < 2:
            await self._send_error(message, "Usage: /join <game_code>")
            return
        
        game_code = parts[1].upper()
        username = message.user.username or message.user.first_name
        
        from systems.player_system import player_system
        
        result = player_system.join_game(message.user.id, username, game_code)
        
        if result["success"]:
            await self._send_message(message, f"✅ {result['message']}")
        elif result.get("need_character"):
            await self._send_message(message, f"❌ {result['error']}\n\nAvailable classes: Scavenger, Mechanic, Soldier")
        else:
            await self._send_error(message, result["error"])
    
    async def _handle_create_character(self, message):
        """Create a character"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        parts = message.text.split()
        if len(parts) < 3:
            await self._send_error(message, "Usage: /create_character <name> <class>")
            return
        
        name = sanitize_input(parts[1])
        class_name = parts[2].title()
        
        # Get game code from group (this is a simplified approach)
        # In a real implementation, you'd need to determine which game the player wants to join
        game_code = "DEFAULT"  # TODO: Get from context
        
        from systems.player_system import player_system
        
        result = player_system.create_character(message.user.id, name, class_name, game_code)
        
        if result["success"]:
            await self._send_message(message, f"✅ {result['message']}")
        else:
            await self._send_error(message, result["error"])
    
    async def _handle_status(self, message):
        """Show player status"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        from systems.player_system import player_system
        
        status = player_system.get_player_status(message.user.id)
        if status:
            await self._send_message(message, status)
        else:
            await self._send_error(message, "Character not found. Use /join to join a game first.")
    
    async def _handle_map(self, message):
        """Show map"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement map system
        await self._send_message(message, "🗺️ Map system not implemented yet")
    
    async def _handle_move(self, message):
        """Move to a location"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement movement system
        await self._send_message(message, "🚶 Movement system not implemented yet")
    
    async def _handle_loot(self, message):
        """Loot current area"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement looting system
        await self._send_message(message, "📦 Looting system not implemented yet")
    
    async def _handle_enter(self, message):
        """Enter a building"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement building system
        await self._send_message(message, "🏢 Building system not implemented yet")
    
    async def _handle_floor(self, message):
        """Enter a floor in a building"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement floor system
        await self._send_message(message, "🏢 Floor system not implemented yet")
    
    async def _handle_sneak(self, message):
        """Attempt to sneak"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement sneak system
        await self._send_message(message, "🥷 Sneak system not implemented yet")
    
    async def _handle_attack(self, message):
        """Attack a target"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement combat system
        await self._send_message(message, "⚔️ Combat system not implemented yet")
    
    async def _handle_reload(self, message):
        """Reload weapon"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement reload system
        await self._send_message(message, "🔫 Reload system not implemented yet")
    
    async def _handle_craft(self, message):
        """Craft an item"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement crafting system
        await self._send_message(message, "🔨 Crafting system not implemented yet")
    
    async def _handle_build(self, message):
        """Build a structure"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement building system
        await self._send_message(message, "🏗️ Building system not implemented yet")
    
    async def _handle_setmode(self, message):
        """Set offline mode"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement offline mode system
        await self._send_message(message, "😴 Offline mode system not implemented yet")
    
    async def _handle_seek(self, message):
        """Seek for players/zombies"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement seeker system
        await self._send_message(message, "🔍 Seeker system not implemented yet")
    
    async def _handle_radio(self, message):
        """Use radio"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement radio system
        await self._send_message(message, "📻 Radio system not implemented yet")
    
    async def _handle_setfreq(self, message):
        """Set radio frequency"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement radio frequency system
        await self._send_message(message, "📻 Radio frequency system not implemented yet")
    
    async def _handle_intel(self, message):
        """Use intelligence system"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement intel system
        await self._send_message(message, "🕵️ Intel system not implemented yet")
    
    async def _handle_mine(self, message):
        """Mine resources"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement mining system
        await self._send_message(message, "⛏️ Mining system not implemented yet")
    
    async def _handle_chop(self, message):
        """Chop wood"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement wood chopping system
        await self._send_message(message, "🪓 Wood chopping system not implemented yet")
    
    async def _handle_vehicle(self, message):
        """Vehicle commands"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement vehicle system
        await self._send_message(message, "🚗 Vehicle system not implemented yet")
    
    async def _handle_store(self, message):
        """Store items"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement storage system
        await self._send_message(message, "📦 Storage system not implemented yet")
    
    async def _handle_retrieve(self, message):
        """Retrieve items"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement retrieval system
        await self._send_message(message, "📦 Retrieval system not implemented yet")
    
    async def _handle_ally(self, message):
        """Ally commands"""
        if not message.is_private:
            await self._send_error(message, "This command must be used in private messages")
            return
        
        # TODO: Implement ally system
        await self._send_message(message, "🤝 Ally system not implemented yet")
    
    async def _handle_admin(self, message):
        """Admin commands"""
        if not await self._is_admin(message):
            await self._send_error(message, "Admin access required")
            return
        
        # TODO: Implement admin commands
        await self._send_message(message, "👑 Admin commands not implemented yet")
    
    # Helper methods
    async def _is_admin(self, message) -> bool:
        """Check if user is admin"""
        return await self.bale_api.is_admin(message.chat_id, message.user.id)
    
    async def _send_message(self, message, text: str):
        """Send a message"""
        await self.bale_api.send_message(message.chat_id, text, reply_to=message.id)
    
    async def _send_error(self, message, error: str):
        """Send an error message"""
        await self._send_message(message, f"❌ {error}")
    
    async def _send_success(self, message, text: str):
        """Send a success message"""
        await self._send_message(message, f"✅ {text}")