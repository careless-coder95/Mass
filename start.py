from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import states

# Welcome banner (you can replace with actual image URL)
BANNER_URL = "https://i.ibb.co/0h8qGwT/telegram-vault-banner.png"

WELCOME_TEXT = """
🔐 **Welcome to Telegram Multi-Account Vault Bot!**

This bot helps you securely manage multiple Telegram accounts using Pyrogram sessions.

**Features:**
✅ Add multiple Telegram accounts
✅ Secure session storage with encryption
✅ Fetch user information
✅ Love feature for account interaction

Click the button below to get started!
"""

async def start_command(client: Client, message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    
    # Clear any existing state
    states.clear_state(user_id)
    
    # Create user in database
    db.get_or_create_user(user_id)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Start Your System", callback_data="main_menu")]
    ])
    
    try:
        await message.reply_photo(
            photo=BANNER_URL,
            caption=WELCOME_TEXT,
            reply_markup=keyboard
        )
    except:
        # If banner fails, send text only
        await message.reply_text(
            WELCOME_TEXT,
            reply_markup=keyboard
        )

async def main_menu_callback(client: Client, callback_query: CallbackQuery):
    """Show main menu"""
    user_id = callback_query.from_user.id
    
    # Clear state
    states.clear_state(user_id)
    
    # Get account count
    count = db.get_accounts_count(user_id)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Account", callback_data="add_account")],
        [InlineKeyboardButton(f"📂 Accounts ({count})", callback_data="view_accounts")],
        [InlineKeyboardButton("ℹ️ INFO", callback_data="info_menu")],
        [InlineKeyboardButton("❤️ Start Love", callback_data="love_menu")]
    ])
    
    text = """
🏠 **Main Menu**

Choose an option below:

➕ **Add Account** - Add a new Telegram account
📂 **Accounts** - View your saved accounts
ℹ️ **INFO** - Get user information
❤️ **Start Love** - Send love using your accounts
"""
    
    await callback_query.message.edit_text(
        text,
        reply_markup=keyboard
    )
    await callback_query.answer()

def setup_start_handlers(app: Client):
    """Register start handlers"""
    app.add_handler(filters.command("start") & filters.private, start_command)
    app.add_handler(filters.callback_data("main_menu"), main_menu_callback)
