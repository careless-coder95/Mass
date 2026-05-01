import os
from pyrogram import Client
from pyrogram.errors import (
    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    PasswordHashInvalid,
    PhoneNumberInvalid
)
import config

async def send_otp(phone: str) -> tuple[Client, str]:
    """
    Send OTP to phone number
    Returns: (client, phone_code_hash)
    """
    session_name = f"temp_{phone.replace('+', '')}"
    session_path = os.path.join(config.SESSION_FOLDER, session_name)
    
    client = Client(
        session_path,
        api_id=config.API_ID,
        api_hash=config.API_HASH
    )
    
    await client.connect()
    
    try:
        sent_code = await client.send_code(phone)
        return client, sent_code.phone_code_hash
    except PhoneNumberInvalid:
        await client.disconnect()
        raise ValueError("Invalid phone number format")
    except Exception as e:
        await client.disconnect()
        raise Exception(f"Failed to send OTP: {str(e)}")

async def verify_otp(client: Client, phone: str, phone_code_hash: str, otp: str) -> dict:
    """
    Verify OTP and login
    Returns: {
        'success': bool,
        'needs_password': bool,
        'session_string': str (if success),
        'error': str (if failed)
    }
    """
    try:
        await client.sign_in(phone, phone_code_hash, otp)
        
        # OTP verified successfully
        session_string = await client.export_session_string()
        await client.disconnect()
        
        # Clean up temp session file
        session_name = f"temp_{phone.replace('+', '')}"
        session_path = os.path.join(config.SESSION_FOLDER, session_name)
        try:
            os.remove(f"{session_path}.session")
        except:
            pass
        
        return {
            'success': True,
            'needs_password': False,
            'session_string': session_string
        }
    
    except SessionPasswordNeeded:
        # 2FA is enabled, need password
        return {
            'success': False,
            'needs_password': True
        }
    
    except PhoneCodeInvalid:
        await client.disconnect()
        return {
            'success': False,
            'needs_password': False,
            'error': 'Invalid OTP code'
        }
    
    except PhoneCodeExpired:
        await client.disconnect()
        return {
            'success': False,
            'needs_password': False,
            'error': 'OTP code expired. Please start again.'
        }
    
    except Exception as e:
        await client.disconnect()
        return {
            'success': False,
            'needs_password': False,
            'error': f'Login failed: {str(e)}'
        }

async def verify_password(client: Client, phone: str, password: str) -> dict:
    """
    Verify 2FA password and complete login
    Returns: {
        'success': bool,
        'session_string': str (if success),
        'error': str (if failed)
    }
    """
    try:
        await client.check_password(password)
        
        # Password verified successfully
        session_string = await client.export_session_string()
        await client.disconnect()
        
        # Clean up temp session file
        session_name = f"temp_{phone.replace('+', '')}"
        session_path = os.path.join(config.SESSION_FOLDER, session_name)
        try:
            os.remove(f"{session_path}.session")
        except:
            pass
        
        return {
            'success': True,
            'session_string': session_string
        }
    
    except PasswordHashInvalid:
        await client.disconnect()
        return {
            'success': False,
            'error': 'Invalid 2FA password'
        }
    
    except Exception as e:
        await client.disconnect()
        return {
            'success': False,
            'error': f'Password verification failed: {str(e)}'
        }

async def get_user_info(session_string: str, username_or_id: str) -> dict:
    """
    Get user information using saved session
    Returns user details or error
    """
    session_name = f"info_{username_or_id}"
    session_path = os.path.join(config.SESSION_FOLDER, session_name)
    
    client = Client(
        session_path,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=session_string
    )
    
    try:
        await client.start()
        
        # Try to get user
        try:
            user = await client.get_users(username_or_id)
        except Exception:
            await client.stop()
            return {
                'success': False,
                'error': 'User not found'
            }
        
        await client.stop()
        
        # Clean up temp session
        try:
            os.remove(f"{session_path}.session")
        except:
            pass
        
        return {
            'success': True,
            'user_id': user.id,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'full_name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
            'username': user.username
        }
    
    except Exception as e:
        try:
            await client.stop()
        except:
            pass
        return {
            'success': False,
            'error': f'Failed to get user info: {str(e)}'
      }
