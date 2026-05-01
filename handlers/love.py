from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import states
from pyrogram.handlers import CallbackQueryHandler, MessageHandler

async def love_menu_callback(client: Client, callback_query: CallbackQuery):
    """Show love menu"""
    user_id = callback_query.from_user.id
    
    account_count = db.get_accounts_count(user_id)
    
    if account_count == 0:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Account", callback_data="add_account")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ])
        
        await callback_query.message.edit_text(
            "❤️ **Start Love**\n\n"
            "❌ You need to add at least one account first to use this feature.\n\n"
            "Add your accounts to start spreading love!",
            reply_markup=keyboard
        )
        await callback_query.answer()
        return
    
    states.set_state(user_id, states.States.WAIT_LOVE_COUNT)
    states.set_data(user_id, 'account_count', account_count)
    
    text = f"""
❤️ **Start Love**

You have **{account_count}** account(s) available.

How many times do you want to love?

Please enter a number:
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Cancel", callback_data="main_menu")]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard)
    await callback_query.answer()

async def handle_love_count_input(client: Client, message: Message):
    """Handle love count input"""
    user_id = message.from_user.id
    
    if states.get_state(user_id) != states.States.WAIT_LOVE_COUNT:
        return
    
    try:
        love_count = int(message.text.strip())
        
        if love_count <= 0:
            await message.reply_text(
                "❌ Please enter a positive number!"
            )
            return
        
        if love_count > 100:
            await message.reply_text(
                "❌ Maximum 100 loves allowed at once!\n\n"
                "Please enter a smaller number."
            )
            return
        
        # Get account count
        account_count = states.get_data(user_id, 'account_count')
        
        # Generate love messages
        love_messages = []
        love_words = [
            "First", "Second", "Third", "Fourth", "Fifth",
            "Sixth", "Seventh", "Eighth", "Ninth", "Tenth"
        ]
        
        for i in range(love_count):
            if i < len(love_words):
                word = love_words[i]
            else:
                word = f"{i + 1}th"
            
            love_messages.append(f"{word} love with {account_count} account(s) ❤️")
        
        # Create output text
        output = "❤️ **Love Messages:**\n\n" + "\n".join(love_messages)
        
        # Add info about total loves
        output += f"\n\n✅ **Total:** {love_count} loves with {account_count} account(s)"
        output += f"\n💝 **Total interactions:** {love_count * account_count}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Love Again", callback_data="love_menu")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ])
        
        await message.reply_text(output, reply_markup=keyboard)
        states.clear_state(user_id)
    
    except ValueError:
        await message.reply_text(
            "❌ Invalid input!\n\n"
            "Please enter a valid number."
        )

def setup_love_handlers(app: Client):
    """Register love handlers"""

    # ✅ Callback button
    app.add_handler(
        CallbackQueryHandler(love_menu_callback, filters.regex("^love_menu$"))
    )

    # ✅ Message handler
    app.add_handler(
        MessageHandler(
            handle_love_count_input,
            filters.text & filters.private &
            filters.create(lambda _, __, m: states.get_state(m.from_user.id) == states.States.WAIT_LOVE_COUNT)
        )
    )
