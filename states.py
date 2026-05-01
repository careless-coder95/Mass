from enum import Enum

class States(Enum):
    """Finite State Machine states for bot conversation flow"""
    WAIT_PHONE = "wait_phone"
    WAIT_OTP = "wait_otp"
    WAIT_PASSWORD = "wait_password"
    WAIT_INFO_INPUT = "wait_info_input"
    WAIT_LOVE_COUNT = "wait_love_count"

# In-memory state storage for users
user_states = {}
user_data = {}

def set_state(user_id: int, state: States):
    """Set user state"""
    user_states[user_id] = state

def get_state(user_id: int):
    """Get current user state"""
    return user_states.get(user_id)

def clear_state(user_id: int):
    """Clear user state"""
    user_states.pop(user_id, None)
    user_data.pop(user_id, None)

def set_data(user_id: int, key: str, value):
    """Store temporary user data"""
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id][key] = value

def get_data(user_id: int, key: str):
    """Retrieve temporary user data"""
    return user_data.get(user_id, {}).get(key)

def get_all_data(user_id: int):
    """Get all user data"""
    return user_data.get(user_id, {})
