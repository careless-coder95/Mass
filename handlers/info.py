from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from utils.auth import get_user_info
import states

async def info_menu_callback(client: Client, callback_query: CallbackQuery):
    """Show info menu"""
    user_id = callback_query.from_user.id
    
    accounts = db.get_accounts(user_id)
    
    if not accounts:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Account", callback_data="add_account")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ])
        
        await callback_query.message.edit_text(
            "ℹ️ **User Info Feature**\n\n"
            "❌ You need to add at least one account first to use this feature.\n\n"
            "This feature allows you to fetch information about any Telegram user.",
            reply_markup=keyboard
        )
        await callback_query.answer()
        return
    
    states.set_state(user_id, states.States.WAIT_INFO_INPUT)
    
    text = """
ℹ️ **Get User Information**

Please enter a **username** (without @) or **User ID**:

**Examples:**
• `telegram` (username)
• `777000` (user ID)

💡 This will fetch public information about the user.
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Cancel", callback_data="main_menu")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard)
    await callback_query.answer()

async def handle_info_input(client: Client, message: Message):
    """Handle username/user ID input"""
    user_id = message.from_user.id
    
    if states.get_state(user_id) != states.States.WAIT_INFO_INPUT:
        return
    
    username_or_id = message.text.strip().replace('@', '')
    
    # Send processing message
    processing_msg = await message.reply_text("🔍 Fetching user information...")
    
    # Get first available account session
    accounts = db.get_accounts(user_id)
    if not accounts:
        await processing_msg.edit_text(
            "❌ No accounts available.\n\n"
            "Please add an account first."
        )
        states.clear_state(user_id)
        return
    
    session_string = accounts[0]['session_string']
    
    try:
        result = await get_user_info(session_string, username_or_id)
        
        if result.get('success'):
            user_info = result
            
            # Store info for potential save
            states.set_data(user_id, 'fetched_user', user_info)
            
            username_display = f"@{user_info['username']}" if user_info.get('username') else "No username"
            
            text = f"""
✅ **User Information**

👤 **Name:** {user_info['full_name']}
🆔 **User ID:** `{user_info['user_id']}`
🔗 **Username:** {username_display}

Would you like to save this information?
"""
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💾 Save", callback_data="save_user_info")],
                [InlineKeyboardButton("🔄 Search Another", callback_data="info_menu")],
                [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
            ])
            
            await processing_msg.edit_text(text, reply_markup=keyboard)
            states.clear_state(user_id)
        
        else:
            error_msg = result.get('error', 'Unknown error')
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Try Again", callback_data="info_menu")],
                [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
            ])
            
            await processing_msg.edit_text(
                f"❌ {error_msg}\n\n"
                "Please check the username/ID and try again.",
                reply_markup=keyboard
            )
            states.clear_state(user_id)
    
    except Exception as e:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Try Again", callback_data="info_menu")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ])
        
        await processing_msg.edit_text(
            f"❌ Failed to fetch user info: {str(e)}\n\n"
            "Please try again later.",
            reply_markup=keyboard
        )
        states.clear_state(user_id)

async def save_user_info_callback(client: Client, callback_query: CallbackQuery):
    """Save fetched user info to database"""
    user_id = callback_query.from_user.id
    
    user_info = states.get_data(user_id, 'fetched_user')
    
    if not user_info:
        await callback_query.answer("❌ No user info to save!", show_alert=True)
        return
    
    # Save to database
    success = db.save_user_info(
        user_id,
        user_info['user_id'],
        user_info['full_name'],
        user_info.get('username')
    )
    
    if success:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Search Another", callback_data="info_menu")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ])
        
        await callback_query.message.edit_text(
            "✅ **User information saved successfully!**\n\n"
            f"👤 {user_info['full_name']}\n"
            f"🆔 {user_info['user_id']}",
            reply_markup=keyboard
        )
        await callback_query.answer("✅ Saved!")
    else:
        await callback_query.answer("❌ Failed to save!", show_alert=True)

def setup_info_handlers(app: Client):
    """Register info handlers"""
    app.add_handler(filters.callback_data("info_menu"), info_menu_callback)
    app.add_handler(filters.callback_data("save_user_info"), save_user_info_callback)
    app.add_handler(
        filters.text & filters.private & 
        filters.create(lambda _, __, m: states.get_state(m.from_user.id) == states.States.WAIT_INFO_INPUT),
        handle_info_input
    )
