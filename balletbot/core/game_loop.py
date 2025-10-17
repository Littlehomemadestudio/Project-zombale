"""
Game loop for BalletBot: Outbreak Dominion
Handles message processing and command routing
"""

import logging
from typing import Dict, List, Optional, Any
from utils.file_manager import file_manager
from utils.helpers import get_current_timestamp, add_action_to_history

logger = logging.getLogger(__name__)

class GameLoop:
    """Main game loop for processing messages and commands"""
    
    def __init__(self, bot, world_manager, scheduler):
        self.bot = bot
        self.world_manager = world_manager
        self.scheduler = scheduler
        self.running = False
    
    async def start(self):
        """Start the game loop"""
        try:
            self.running = True
            
            # Register command handlers
            self._register_commands()
            
            # Start bot polling
            await self.bot.start_polling()
            
            logger.info("Game loop started")
            
        except Exception as e:
            logger.error(f"Error starting game loop: {e}")
            raise
    
    async def stop(self):
        """Stop the game loop"""
        try:
            self.running = False
            await self.bot.stop_polling()
            logger.info("Game loop stopped")
            
        except Exception as e:
            logger.error(f"Error stopping game loop: {e}")
    
    def _register_commands(self):
        """Register all command handlers"""
        try:
            # Admin commands
            self.bot.command("/start_season")(self._handle_start_season)
            self.bot.command("/announce")(self._handle_announce)
            self.bot.command("/pause_world")(self._handle_pause_world)
            self.bot.command("/resume_world")(self._handle_resume_world)
            self.bot.command("/reset_world")(self._handle_reset_world)
            
            # Player commands
            self.bot.command("/join")(self._handle_join)
            self.bot.command("/create_character")(self._handle_create_character)
            self.bot.command("/status")(self._handle_status)
            self.bot.command("/map")(self._handle_map)
            self.bot.command("/move")(self._handle_move)
            self.bot.command("/loot")(self._handle_loot)
            self.bot.command("/enter")(self._handle_enter)
            self.bot.command("/floor")(self._handle_floor)
            self.bot.command("/sneak")(self._handle_sneak)
            self.bot.command("/attack")(self._handle_attack)
            self.bot.command("/craft")(self._handle_craft)
            self.bot.command("/build")(self._handle_build)
            self.bot.command("/setmode")(self._handle_setmode)
            self.bot.command("/seek")(self._handle_seek)
            self.bot.command("/radio")(self._handle_radio)
            self.bot.command("/setfreq")(self._handle_setfreq)
            self.bot.command("/intel")(self._handle_intel)
            self.bot.command("/mine")(self._handle_mine)
            self.bot.command("/chop")(self._handle_chop)
            self.bot.command("/vehicle")(self._handle_vehicle)
            
            logger.info("Command handlers registered")
            
        except Exception as e:
            logger.error(f"Error registering commands: {e}")
    
    # Admin command handlers
    async def _handle_start_season(self, message, args):
        """Handle /start_season command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            # Check if user is admin
            if not await self.bot.is_admin(chat_id, user_id):
                await self.bot.send_message(chat_id, "❌ You must be an admin to start a season.")
                return
            
            # Create new game
            from systems.player_system import player_system
            game_code = player_system.create_game()
            
            if game_code:
                await self.bot.send_message(chat_id, f"✅ Season started! Game code: **{game_code}**")
                logger.info(f"Admin {user_id} started season {game_code}")
            else:
                await self.bot.send_message(chat_id, "❌ Failed to start season.")
                
        except Exception as e:
            logger.error(f"Error handling start_season: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_announce(self, message, args):
        """Handle /announce command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            # Check if user is admin
            if not await self.bot.is_admin(chat_id, user_id):
                await self.bot.send_message(chat_id, "❌ You must be an admin to make announcements.")
                return
            
            if not args:
                await self.bot.send_message(chat_id, "❌ Please provide a message to announce.")
                return
            
            # Send announcement
            announcement = f"📢 **ANNOUNCEMENT**\n\n{args}"
            await self.bot.send_message(chat_id, announcement)
            
            logger.info(f"Admin {user_id} made announcement: {args[:100]}...")
            
        except Exception as e:
            logger.error(f"Error handling announce: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_pause_world(self, message, args):
        """Handle /pause_world command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            # Check if user is admin
            if not await self.bot.is_admin(chat_id, user_id):
                await self.bot.send_message(chat_id, "❌ You must be an admin to pause the world.")
                return
            
            # TODO: Implement world pausing
            await self.bot.send_message(chat_id, "⏸️ World paused.")
            
        except Exception as e:
            logger.error(f"Error handling pause_world: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_resume_world(self, message, args):
        """Handle /resume_world command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            # Check if user is admin
            if not await self.bot.is_admin(chat_id, user_id):
                await self.bot.send_message(chat_id, "❌ You must be an admin to resume the world.")
                return
            
            # TODO: Implement world resuming
            await self.bot.send_message(chat_id, "▶️ World resumed.")
            
        except Exception as e:
            logger.error(f"Error handling resume_world: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_reset_world(self, message, args):
        """Handle /reset_world command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            # Check if user is admin
            if not await self.bot.is_admin(chat_id, user_id):
                await self.bot.send_message(chat_id, "❌ You must be an admin to reset the world.")
                return
            
            # TODO: Implement world reset with confirmation
            await self.bot.send_message(chat_id, "🔄 World reset. (Confirmation required)")
            
        except Exception as e:
            logger.error(f"Error handling reset_world: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    # Player command handlers
    async def _handle_join(self, message, args):
        """Handle /join command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            if not args:
                await self.bot.send_message(chat_id, "❌ Please provide a game code. Usage: `/join <game_code>`")
                return
            
            game_code = args.strip()
            
            # Join game
            from systems.player_system import player_system
            if player_system.join_game(user_id, game_code):
                await self.bot.send_message(chat_id, f"✅ Joined game {game_code}! Use `/create_character <name> <class>` to create your character.")
            else:
                await self.bot.send_message(chat_id, "❌ Failed to join game. Invalid game code or game not found.")
            
        except Exception as e:
            logger.error(f"Error handling join: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_create_character(self, message, args):
        """Handle /create_character command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            if not args:
                await self.bot.send_message(chat_id, "❌ Please provide name and class. Usage: `/create_character <name> <class>`")
                return
            
            parts = args.split()
            if len(parts) < 2:
                await self.bot.send_message(chat_id, "❌ Please provide both name and class. Usage: `/create_character <name> <class>`")
                return
            
            name = parts[0]
            char_class = parts[1]
            
            # Create character
            from systems.player_system import player_system
            result = player_system.create_character(user_id, name, char_class, "DEFAULT_GAME")
            
            if result["success"]:
                await self.bot.send_message(chat_id, result["message"])
            else:
                await self.bot.send_message(chat_id, f"❌ {result['error']}")
            
        except Exception as e:
            logger.error(f"Error handling create_character: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_status(self, message, args):
        """Handle /status command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            from systems.player_system import player_system
            status = player_system.get_player_status(user_id)
            
            if status:
                await self.bot.send_message(chat_id, status)
            else:
                await self.bot.send_message(chat_id, "❌ Character not found. Use `/create_character <name> <class>` to create one.")
            
        except Exception as e:
            logger.error(f"Error handling status: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_map(self, message, args):
        """Handle /map command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            # TODO: Implement map functionality
            await self.bot.send_message(chat_id, "🗺️ Map functionality coming soon!")
            
        except Exception as e:
            logger.error(f"Error handling map: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_move(self, message, args):
        """Handle /move command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            if not args:
                await self.bot.send_message(chat_id, "❌ Please provide a location. Usage: `/move <location>`")
                return
            
            location = args.strip()
            
            from systems.player_system import player_system
            if player_system.move_player(user_id, location):
                await self.bot.send_message(chat_id, f"✅ Moved to {location}")
            else:
                await self.bot.send_message(chat_id, "❌ Failed to move to that location.")
            
        except Exception as e:
            logger.error(f"Error handling move: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_loot(self, message, args):
        """Handle /loot command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            # TODO: Implement looting functionality
            await self.bot.send_message(chat_id, "💎 Looting functionality coming soon!")
            
        except Exception as e:
            logger.error(f"Error handling loot: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_enter(self, message, args):
        """Handle /enter command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            if not args:
                await self.bot.send_message(chat_id, "❌ Please provide a building name. Usage: `/enter <building>`")
                return
            
            building_name = args.strip()
            
            from systems.building_system import building_system
            result = building_system.enter_building(user_id, building_name)
            
            if result["success"]:
                await self.bot.send_message(chat_id, result["message"])
            else:
                await self.bot.send_message(chat_id, f"❌ {result['error']}")
            
        except Exception as e:
            logger.error(f"Error handling enter: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_floor(self, message, args):
        """Handle /floor command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            if not args:
                await self.bot.send_message(chat_id, "❌ Please provide floor number and action. Usage: `/floor <number> <action>`")
                return
            
            parts = args.split()
            if len(parts) < 2:
                await self.bot.send_message(chat_id, "❌ Please provide both floor number and action. Usage: `/floor <number> <action>`")
                return
            
            try:
                floor_number = int(parts[0])
                action = parts[1]
            except ValueError:
                await self.bot.send_message(chat_id, "❌ Floor number must be a number.")
                return
            
            from systems.building_system import building_system
            result = building_system.enter_floor(user_id, floor_number, action)
            
            if result["success"]:
                await self.bot.send_message(chat_id, result["message"])
            else:
                await self.bot.send_message(chat_id, f"❌ {result['error']}")
            
        except Exception as e:
            logger.error(f"Error handling floor: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_sneak(self, message, args):
        """Handle /sneak command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            from systems.building_system import building_system
            result = building_system.process_encounter_action(user_id, "sneak")
            
            if result["success"]:
                await self.bot.send_message(chat_id, result["message"])
            else:
                await self.bot.send_message(chat_id, f"❌ {result['error']}")
            
        except Exception as e:
            logger.error(f"Error handling sneak: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_attack(self, message, args):
        """Handle /attack command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            from systems.building_system import building_system
            result = building_system.process_encounter_action(user_id, "attack")
            
            if result["success"]:
                await self.bot.send_message(chat_id, result["message"])
            else:
                await self.bot.send_message(chat_id, f"❌ {result['error']}")
            
        except Exception as e:
            logger.error(f"Error handling attack: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_craft(self, message, args):
        """Handle /craft command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            if not args:
                await self.bot.send_message(chat_id, "❌ Please provide an item to craft. Usage: `/craft <item>`")
                return
            
            item_id = args.strip()
            
            from systems.crafting_system import crafting_system
            result = crafting_system.craft_item(user_id, item_id)
            
            if result["success"]:
                await self.bot.send_message(chat_id, result["message"])
            else:
                await self.bot.send_message(chat_id, f"❌ {result['error']}")
            
        except Exception as e:
            logger.error(f"Error handling craft: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_build(self, message, args):
        """Handle /build command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            # TODO: Implement building functionality
            await self.bot.send_message(chat_id, "🏗️ Building functionality coming soon!")
            
        except Exception as e:
            logger.error(f"Error handling build: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_setmode(self, message, args):
        """Handle /setmode command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            if not args:
                await self.bot.send_message(chat_id, "❌ Please provide a mode. Usage: `/setmode <mode>`")
                return
            
            mode = args.strip()
            
            from systems.offline_system import offline_system
            result = offline_system.set_offline_mode(user_id, mode)
            
            if result["success"]:
                await self.bot.send_message(chat_id, result["message"])
            else:
                await self.bot.send_message(chat_id, f"❌ {result['error']}")
            
        except Exception as e:
            logger.error(f"Error handling setmode: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_seek(self, message, args):
        """Handle /seek command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            # TODO: Implement seek functionality
            await self.bot.send_message(chat_id, "🔍 Seek functionality coming soon!")
            
        except Exception as e:
            logger.error(f"Error handling seek: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_radio(self, message, args):
        """Handle /radio command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            if not args:
                await self.bot.send_message(chat_id, "❌ Please provide frequency and message. Usage: `/radio <freq> <message>`")
                return
            
            parts = args.split(' ', 1)
            if len(parts) < 2:
                await self.bot.send_message(chat_id, "❌ Please provide both frequency and message. Usage: `/radio <freq> <message>`")
                return
            
            frequency = parts[0]
            message_text = parts[1]
            
            from systems.radio_system import radio_system
            result = radio_system.send_radio_message(user_id, frequency, message_text)
            
            if result["success"]:
                await self.bot.send_message(chat_id, f"✅ Radio message sent to {result['listeners']} listeners")
            else:
                await self.bot.send_message(chat_id, f"❌ {result['error']}")
            
        except Exception as e:
            logger.error(f"Error handling radio: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_setfreq(self, message, args):
        """Handle /setfreq command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            if not args:
                await self.bot.send_message(chat_id, "❌ Please provide a frequency. Usage: `/setfreq <frequency>`")
                return
            
            frequency = args.strip()
            
            from systems.radio_system import radio_system
            result = radio_system.set_frequency(user_id, frequency)
            
            if result["success"]:
                await self.bot.send_message(chat_id, result["message"])
            else:
                await self.bot.send_message(chat_id, f"❌ {result['error']}")
            
        except Exception as e:
            logger.error(f"Error handling setfreq: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_intel(self, message, args):
        """Handle /intel command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            if not args:
                await self.bot.send_message(chat_id, "❌ Please provide an action. Usage: `/intel <action>`")
                return
            
            parts = args.split()
            action = parts[0]
            
            from systems.spotter_system import spotter_system
            
            if action == "buy_spotter":
                result = spotter_system.buy_spotter(user_id)
                if result["success"]:
                    await self.bot.send_message(chat_id, result["message"])
                else:
                    await self.bot.send_message(chat_id, f"❌ {result['error']}")
            
            elif action == "use_spotter":
                if len(parts) < 2:
                    await self.bot.send_message(chat_id, "❌ Please provide a target. Usage: `/intel use_spotter <target>`")
                    return
                
                target = parts[1]
                result = spotter_system.use_spotter(user_id, target)
                
                if result["success"]:
                    await self.bot.send_message(chat_id, result["report"])
                else:
                    await self.bot.send_message(chat_id, f"❌ {result['error']}")
            
            else:
                await self.bot.send_message(chat_id, "❌ Invalid action. Use `buy_spotter` or `use_spotter <target>`")
            
        except Exception as e:
            logger.error(f"Error handling intel: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_mine(self, message, args):
        """Handle /mine command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            # TODO: Implement mining functionality
            await self.bot.send_message(chat_id, "⛏️ Mining functionality coming soon!")
            
        except Exception as e:
            logger.error(f"Error handling mine: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_chop(self, message, args):
        """Handle /chop command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            # TODO: Implement chopping functionality
            await self.bot.send_message(chat_id, "🪓 Chopping functionality coming soon!")
            
        except Exception as e:
            logger.error(f"Error handling chop: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")
    
    async def _handle_vehicle(self, message, args):
        """Handle /vehicle command"""
        try:
            chat_id = str(message.chat.id)
            user_id = str(message.from_user.id)
            
            # TODO: Implement vehicle functionality
            await self.bot.send_message(chat_id, "🚗 Vehicle functionality coming soon!")
            
        except Exception as e:
            logger.error(f"Error handling vehicle: {e}")
            await self.bot.send_message(str(message.chat.id), "❌ An error occurred.")