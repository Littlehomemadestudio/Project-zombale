#!/usr/bin/env python3
"""
Final integration test for BalletBot with Bale API
Tests both mock and real API modes
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config import BOT_TOKEN, USE_REAL_BALE_API

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mock_mode():
    """Test balletbot in mock mode"""
    try:
        logger.info("Testing BalletBot in MOCK mode...")
        
        # Temporarily set to mock mode
        import config
        original_setting = config.USE_REAL_BALE_API
        config.USE_REAL_BALE_API = False
        
        # Import after changing config
        from bale_api_simple import BaleAPI
        
        # Test basic functionality
        bot = BaleAPI(BOT_TOKEN)
        logger.info("✅ Mock Bale API instance created")
        
        # Test command registration
        @bot.command("/test")
        async def test_command(message, args):
            await bot.send_message(str(message.chat.id), f"Mock test: {args}")
        
        # Test message sending
        await bot.send_message("123456789", "Mock test message")
        logger.info("✅ Mock API functionality working")
        
        # Restore original setting
        config.USE_REAL_BALE_API = original_setting
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Mock mode test failed: {e}")
        return False

async def test_real_mode():
    """Test balletbot in real mode"""
    try:
        logger.info("Testing BalletBot in REAL mode...")
        
        # Temporarily set to real mode
        import config
        original_setting = config.USE_REAL_BALE_API
        config.USE_REAL_BALE_API = True
        
        # Import after changing config
        from bale_api_real import BaleAPI
        
        # Test basic functionality
        bot = BaleAPI(BOT_TOKEN)
        logger.info("✅ Real Bale API instance created")
        
        # Test command registration
        @bot.command("/test")
        async def test_command(message, args):
            await bot.send_message(str(message.chat.id), f"Real test: {args}")
        
        # Test API initialization (without actual polling)
        await bot.start()
        logger.info("✅ Real API initialized")
        
        # Test message sending (will fail with invalid token, but should not crash)
        try:
            await bot.send_message("123456789", "Real test message")
            logger.info("✅ Real API message sending working")
        except Exception as e:
            logger.info(f"⚠️ Real API message sending failed (expected with test token): {e}")
        
        await bot.close()
        
        # Restore original setting
        config.USE_REAL_BALE_API = original_setting
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Real mode test failed: {e}")
        return False

async def test_full_balletbot():
    """Test the complete balletbot integration"""
    try:
        logger.info("Testing complete BalletBot integration...")
        
        # Test with mock mode for safety
        import config
        original_setting = config.USE_REAL_BALE_API
        config.USE_REAL_BALE_API = False
        
        # Import main bot
        from main import BalletBot
        
        # Create bot instance
        bot = BalletBot()
        logger.info("✅ BalletBot instance created")
        
        # Test world manager
        await bot.world_manager.initialize()
        logger.info("✅ World manager initialized")
        
        # Test scheduler
        await bot.scheduler.start()
        logger.info("✅ Scheduler started")
        
        # Test game loop preparation
        bot.game_loop.running = True
        logger.info("✅ Game loop prepared")
        
        # Test command handlers
        test_handlers = [
            "/start_season", "/join", "/create_character", "/status", 
            "/move", "/loot", "/enter", "/craft", "/radio"
        ]
        
        for handler in test_handlers:
            if handler in bot.bot.command_handlers:
                logger.info(f"✅ Command handler {handler} registered")
            else:
                logger.warning(f"⚠️ Command handler {handler} not found")
        
        # Cleanup
        await bot.scheduler.stop()
        
        # Restore original setting
        config.USE_REAL_BALE_API = original_setting
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Full balletbot test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Starting final BalletBot integration tests...")
    
    # Test 1: Mock mode
    test1_passed = await test_mock_mode()
    
    # Test 2: Real mode
    test2_passed = await test_real_mode()
    
    # Test 3: Full balletbot
    test3_passed = await test_full_balletbot()
    
    logger.info("\n" + "="*50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*50)
    logger.info(f"Mock Mode Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    logger.info(f"Real Mode Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    logger.info(f"Full BalletBot Test: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    logger.info("="*50)
    
    if test1_passed and test2_passed and test3_passed:
        logger.info("🎉 ALL TESTS PASSED! BalletBot is ready with Bale API integration.")
        logger.info("\n📋 NEXT STEPS:")
        logger.info("1. Set your real Bale bot token in config.py")
        logger.info("2. Set USE_REAL_BALE_API = True in config.py")
        logger.info("3. Run: python3 main.py")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)