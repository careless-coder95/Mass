from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import states

async def view_accounts_callback(client: Client, callback_query: CallbackQuery):
    """Show list of saved accounts"""
    user_id = callback_query.from_user.id
    
    # Clear state
    states.clear_state(user_id)
    
    accounts = db.get_accounts(user_id)
    
    if not accounts:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Account", callback_data="add_account")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ])
        
        await callback_query.message.edit_text(
            "📂 **Your Accounts**\n\n"
            "You don't have any saved accounts yet.\n\n"
            "Click 'Add Account' to get started!",
            reply_markup=keyboard
        )
        await callback_query.answer()
        return
    
    # Create inline keyboard with account buttons
    keyboard_buttons = []
    for account in accounts:
        phone = account['phone']
        # Mask middle digits for privacy
        masked_phone = phone[:4] + "XXX" + phone[-4:] if len(phone) > 8 else phone
        keyboard_buttons.append([
            InlineKeyboardButton(
                f"📱 {masked_phone}",
                callback_data=f"view_account:{phone}"
            )
        ])
    
    keyboard_buttons.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    
    text = f"""
📂 **Your Accounts**

Total Accounts: **{len(accounts)}**

Click on an account to view details:
"""
    
    await callback_query.message.edit_text(
        text,
        reply_markup=keyboard
    )
    await callback_query.answer()

async def view_single_account_callback(client: Client, callback_query: CallbackQuery):
    """Show details of a single account"""
    user_id = callback_query.from_user.id
    
    # Extract phone from callback data
    phone = callback_query.data.split(":", 1)[1]
    
    account = db.get_account_by_phone(user_id, phone)
    
    if not account:
        await callback_query.answer("❌ Account not found!", show_alert=True)
        return
    
    # Mask phone for display
    masked_phone = phone[:4] + "XXX" + phone[-4:] if len(phone) > 8 else phone
    
    # Check if 2FA is enabled
    has_2fa = "✅ Enabled" if account.get('password') else "❌ Disabled"
    
    text = f"""
📱 **Account Details**

📞 Phone: `{masked_phone}`
🔐 Session: Active
🔑 2FA: {has_2fa}
📅 Added: {account['created_at'][:10]}

⚠️ Keep your session safe and never share it!
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Accounts", callback_data="view_accounts")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])
    
    await callback_query.message.edit_text(
        text,
        reply_markup=keyboard
    )
    await callback_query.answer()

def setup_accounts_handlers(app: Client):
    """Register accounts handlers"""
    app.add_handler(filters.callback_data("view_accounts"), view_accounts_callback)
    app.add_handler(filters.regex(r"^view_account:"), view_single_account_callback)
