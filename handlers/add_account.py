from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from utils.auth import send_otp, verify_otp, verify_password
from utils.encryption import encryptor
import states
from pyrogram.handlers import CallbackQueryHandler, MessageHandler

async def add_account_callback(client: Client, callback_query: CallbackQuery):
    """Start add account flow"""
    user_id = callback_query.from_user.id
    
    states.set_state(user_id, states.States.WAIT_PHONE)
    
    text = """
📱 **Add New Account**

Please enter your phone number with country code.

**Example:** `+919876543210`

⚠️ Make sure the number is correct!
"""
    
    await callback_query.message.edit_text(text)
    await callback_query.answer()

async def handle_phone_input(client: Client, message: Message):
    """Handle phone number input"""
    user_id = message.from_user.id
    
    if states.get_state(user_id) != states.States.WAIT_PHONE:
        return
    
    phone = message.text.strip()
    
    # Basic validation
    if not phone.startswith('+') or len(phone) < 10:
        await message.reply_text(
            "❌ Invalid phone number format!\n\n"
            "Please enter with country code.\n"
            "Example: `+919876543210`"
        )
        return
    
    # Send "processing" message
    processing_msg = await message.reply_text("📤 Sending OTP...")
    
    try:
        # Send OTP
        pyrogram_client, phone_code_hash = await send_otp(phone)
        
        # Store data
        states.set_data(user_id, 'phone', phone)
        states.set_data(user_id, 'phone_code_hash', phone_code_hash)
        states.set_data(user_id, 'pyrogram_client', pyrogram_client)
        
        # Update state
        states.set_state(user_id, states.States.WAIT_OTP)
        
        await processing_msg.edit_text(
            "✅ OTP sent successfully!\n\n"
            f"🔐 Please enter the OTP code sent to **{phone}**"
        )
    
    except ValueError as e:
        await processing_msg.edit_text(f"❌ {str(e)}\n\nPlease try again with correct format.")
        states.clear_state(user_id)
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Failed to send OTP: {str(e)}\n\n"
            "Please try again later or check your phone number."
        )
        states.clear_state(user_id)

async def handle_otp_input(client: Client, message: Message):
    """Handle OTP input"""
    user_id = message.from_user.id
    
    if states.get_state(user_id) != states.States.WAIT_OTP:
        return
    
    otp = message.text.strip()
    
    # Get stored data
    phone = states.get_data(user_id, 'phone')
    phone_code_hash = states.get_data(user_id, 'phone_code_hash')
    pyrogram_client = states.get_data(user_id, 'pyrogram_client')
    
    # Send processing message
    processing_msg = await message.reply_text("🔄 Verifying OTP...")
    
    try:
        result = await verify_otp(pyrogram_client, phone, phone_code_hash, otp)
        
        if result.get('success'):
            # OTP verified, login successful
            session_string = result['session_string']
            
            # Save to database (no password)
            encrypted_password = None
            db.add_account(user_id, phone, encrypted_password, session_string)
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
                [InlineKeyboardButton("➕ Add More Accounts", callback_data="add_account")]
            ])
            
            await processing_msg.edit_text(
                "✅ **Account Saved Successfully!**\n\n"
                f"📱 Phone: `{phone}`\n"
                "🔐 Session: Active",
                reply_markup=keyboard
            )
            
            states.clear_state(user_id)
        
        elif result.get('needs_password'):
            # 2FA enabled, ask for password
            states.set_state(user_id, states.States.WAIT_PASSWORD)
            
            await processing_msg.edit_text(
                "🔐 **2FA Enabled**\n\n"
                "Please enter your 2-Step Verification password:"
            )
        
        else:
            # Error occurred
            error_msg = result.get('error', 'Unknown error')
            await processing_msg.edit_text(
                f"❌ {error_msg}\n\n"
                "Please try again or use /start to restart."
            )
            states.clear_state(user_id)
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Verification failed: {str(e)}\n\n"
            "Please use /start to try again."
        )
        states.clear_state(user_id)

async def handle_password_input(client: Client, message: Message):
    """Handle 2FA password input"""
    user_id = message.from_user.id
    
    if states.get_state(user_id) != states.States.WAIT_PASSWORD:
        return
    
    password = message.text.strip()
    
    # Delete user's password message for security
    try:
        await message.delete()
    except:
        pass
    
    # Get stored data
    phone = states.get_data(user_id, 'phone')
    pyrogram_client = states.get_data(user_id, 'pyrogram_client')
    
    # Send processing message
    processing_msg = await client.send_message(
        user_id,
        "🔄 Verifying password..."
    )
    
    try:
        result = await verify_password(pyrogram_client, phone, password)
        
        if result.get('success'):
            # Password verified, login successful
            session_string = result['session_string']
            
            # Encrypt password before saving
            encrypted_password = encryptor.encrypt(password)
            
            # Save to database
            db.add_account(user_id, phone, encrypted_password, session_string)
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
                [InlineKeyboardButton("➕ Add More Accounts", callback_data="add_account")]
            ])
            
            await processing_msg.edit_text(
                "✅ **Account Saved Successfully!**\n\n"
                f"📱 Phone: `{phone}`\n"
                "🔐 Session: Active\n"
                "🔑 2FA: Enabled",
                reply_markup=keyboard
            )
            
            states.clear_state(user_id)
        
        else:
            # Error occurred
            error_msg = result.get('error', 'Unknown error')
            await processing_msg.edit_text(
                f"❌ {error_msg}\n\n"
                "Please use /start to try again."
            )
            states.clear_state(user_id)
    
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Password verification failed: {str(e)}\n\n"
            "Please use /start to try again."
        )
        states.clear_state(user_id)



def setup_add_account_handlers(app: Client):
    """Register add account handlers"""

    # ✅ FIXED callback handler
    app.add_handler(
        CallbackQueryHandler(add_account_callback, filters.regex("^add_account$"))
    )

    # ✅ Message handlers (ye already sahi hai, bas proper handler use karo)
    app.add_handler(
        MessageHandler(
            handle_phone_input,
            filters.text & filters.private &
            filters.create(lambda _, __, m: states.get_state(m.from_user.id) == states.States.WAIT_PHONE)
        )
    )

    app.add_handler(
        MessageHandler(
            handle_otp_input,
            filters.text & filters.private &
            filters.create(lambda _, __, m: states.get_state(m.from_user.id) == states.States.WAIT_OTP)
        )
    )

    app.add_handler(
        MessageHandler(
            handle_password_input,
            filters.text & filters.private &
            filters.create(lambda _, __, m: states.get_state(m.from_user.id) == states.States.WAIT_PASSWORD)
        )
    )
