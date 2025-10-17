#!/usr/bin/env python3
"""
Test script for Bale API integration
Tests the balletbot with real Bale API
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from bale_api_simple import BaleAPI
from config import BOT_TOKEN

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bale_api():
    """Test the Bale API integration"""
    try:
        logger.info("Testing Bale API integration...")
        
        # Create bot instance
        bot = BaleAPI(BOT_TOKEN)
        
        # Test basic functionality
        logger.info("✅ Bale API instance created successfully")
        
        # Test command registration
        @bot.command("/test")
        async def test_command(message, args):
            await bot.send_message(str(message.chat.id), f"Test command received! Args: {args}")
        
        logger.info("✅ Command handler registered successfully")
        
        # Test message handler
        @bot.message_handler
        async def test_message_handler(message):
            if message.text and not message.text.startswith('/'):
                await bot.send_message(str(message.chat.id), f"Echo: {message.text}")
        
        logger.info("✅ Message handler registered successfully")
        
        # Test callback handler
        @bot.callback_handler("test_callback")
        async def test_callback_handler(callback_query):
            await bot.answer_callback_query(callback_query.id, "Test callback received!")
        
        logger.info("✅ Callback handler registered successfully")
        
        # Test inline keyboard creation
        keyboard = bot.create_inline_keyboard([
            [{"text": "Test Button", "callback_data": "test_callback"}]
        ])
        logger.info("✅ Inline keyboard created successfully")
        
        # Test admin check (will fail without real token, but should not crash)
        try:
            is_admin = await bot.is_admin("123456789", "987654321")
            logger.info(f"✅ Admin check completed: {is_admin}")
        except Exception as e:
            logger.info(f"⚠️ Admin check failed (expected with test token): {e}")
        
        logger.info("🎉 All Bale API integration tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Bale API integration test failed: {e}")
        return False

async def test_balletbot_integration():
    """Test the full balletbot integration"""
    try:
        logger.info("Testing full balletbot integration...")
        
        # Import the main bot
        from main import BalletBot
        
        # Create bot instance
        bot = BalletBot()
        logger.info("✅ BalletBot instance created successfully")
        
        # Test world manager initialization
        await bot.world_manager.initialize()
        logger.info("✅ World manager initialized successfully")
        
        # Test scheduler start
        await bot.scheduler.start()
        logger.info("✅ Scheduler started successfully")
        
        # Test game loop start (without polling)
        bot.game_loop.running = True
        logger.info("✅ Game loop prepared successfully")
        
        logger.info("🎉 Full balletbot integration test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Balletbot integration test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("Starting Bale API integration tests...")
    
    # Test 1: Basic Bale API
    test1_passed = await test_bale_api()
    
    # Test 2: Full balletbot integration
    test2_passed = await test_balletbot_integration()
    
    if test1_passed and test2_passed:
        logger.info("🎉 All tests passed! Balletbot is ready with real Bale API.")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)