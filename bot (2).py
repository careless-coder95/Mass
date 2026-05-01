#!/usr/bin/env python3
"""
Telegram Multi-Account Vault Bot
A secure bot for managing multiple Telegram accounts using Pyrogram
"""

import asyncio
import logging
from pyrogram import Client
import config

# Import handlers
from handlers.start import setup_start_handlers
from handlers.add_account import setup_add_account_handlers
from handlers.accounts import setup_accounts_handlers
from handlers.info import setup_info_handlers
from handlers.love import setup_love_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VaultBot:
    def __init__(self):
        self.app = Client(
            "vault_bot",
            bot_token=config.BOT_TOKEN,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
        )
        
        # Setup all handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Register all bot handlers"""
        logger.info("Setting up handlers...")
        
        setup_start_handlers(self.app)
        setup_add_account_handlers(self.app)
        setup_accounts_handlers(self.app)
        setup_info_handlers(self.app)
        setup_love_handlers(self.app)
        
        logger.info("All handlers registered successfully")
    
    async def start(self):
        """Start the bot"""
        logger.info("Starting Telegram Vault Bot...")
        await self.app.start()
        
        me = await self.app.get_me()
        logger.info(f"Bot started successfully as @{me.username}")
        logger.info("Bot is now running. Press Ctrl+C to stop.")
        
        # Keep the bot running
        await asyncio.Event().wait()
    
    async def stop(self):
        """Stop the bot"""
        logger.info("Stopping bot...")
        await self.app.stop()
        logger.info("Bot stopped")

async def main():
    """Main entry point"""
    bot = VaultBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Received stop signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
