#!/usr/bin/env python3
"""
BalletBot: Outbreak Dominion
A real-time, persistent multiplayer zombie survival simulator for Bale messenger
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from bale_api import BaleAPI
from core.game_loop import GameLoop
from core.world_manager import WorldManager
from core.scheduler import Scheduler
from utils.logger import setup_logging
from config import BOT_TOKEN

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

class BalletBot:
    """Main bot class that orchestrates all game systems"""
    
    def __init__(self):
        self.bot = BaleAPI(BOT_TOKEN)
        self.world_manager = WorldManager()
        self.scheduler = Scheduler(self.world_manager)
        self.game_loop = GameLoop(self.bot, self.world_manager, self.scheduler)
        
    async def start(self):
        """Start the bot and all game systems"""
        logger.info("Starting BalletBot: Outbreak Dominion...")
        
        try:
            # Initialize world manager
            await self.world_manager.initialize()
            
            # Start scheduler
            await self.scheduler.start()
            
            # Start game loop
            await self.game_loop.start()
            
            logger.info("BalletBot started successfully!")
            
        except Exception as e:
            logger.error(f"Failed to start BalletBot: {e}")
            raise
    
    async def stop(self):
        """Stop the bot gracefully"""
        logger.info("Stopping BalletBot...")
        await self.scheduler.stop()
        await self.game_loop.stop()
        logger.info("BalletBot stopped")

async def main():
    """Main entry point"""
    bot = BalletBot()
    
    try:
        await bot.start()
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())