# 🔐 Telegram Multi-Account Vault Bot

A secure Telegram bot for managing multiple Telegram accounts using Pyrogram. This bot allows you to add multiple Telegram accounts, generate and store their session strings securely, and perform various operations with them.

## ✨ Features

- 🔐 **Secure Session Management** - Add multiple Telegram accounts with OTP and 2FA support
- 🗃️ **Encrypted Storage** - Passwords encrypted using Fernet encryption
- 📱 **Account Management** - View and manage all your saved accounts
- ℹ️ **User Info Fetcher** - Get information about any Telegram user
- ❤️ **Love Feature** - Send love messages using your accounts
- 🎨 **Clean UI** - Intuitive inline keyboard navigation
- 🔒 **Private & Secure** - All data stored locally in SQLite

## 🛠️ Tech Stack

- **Python 3.10+**
- **Pyrogram** - Modern Telegram MTProto API framework
- **TgCrypto** - Fast encryption library for Pyrogram
- **SQLite** - Local database (easily switchable to MongoDB)
- **Cryptography** - Fernet encryption for passwords

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Python 3.10 or higher** installed
2. **Telegram API credentials** (API ID and API Hash)
3. **Bot Token** from BotFather

## 🚀 Setup Instructions

### Step 1: Get Telegram API Credentials

1. Visit https://my.telegram.org/auth
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Note down your `API_ID` and `API_HASH`

### Step 2: Create Bot with BotFather

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. Copy the **Bot Token** provided

### Step 3: Clone/Download the Project

```bash
# Clone or download the project
cd telegram-vault-bot
```

### Step 4: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Edit `.env` file and add your credentials:

```env
BOT_TOKEN=your_bot_token_from_botfather
API_ID=your_api_id
API_HASH=your_api_hash
ENCRYPTION_KEY=your_generated_fernet_key
DATABASE_PATH=vault.db
```

### Step 6: Run the Bot

```bash
# Make the bot executable (Linux/Mac)
chmod +x bot.py

# Run the bot
python bot.py
```

Or run directly:

```bash
python3 bot.py
```

## 📱 Usage Guide

### Adding an Account

1. Start the bot with `/start`
2. Click **"🚀 Start Your System"**
3. Click **"➕ Add Account"**
4. Enter your phone number with country code (e.g., `+919876543210`)
5. Enter the OTP code sent to your phone
6. If 2FA is enabled, enter your password
7. Account saved successfully! ✅

### Viewing Accounts

1. From main menu, click **"📂 Accounts"**
2. See all your saved accounts
3. Click on any account to view details

### Getting User Info

1. Click **"ℹ️ INFO"** from main menu
2. Enter a username (without @) or User ID
3. View the fetched information
4. Optionally save it to database

### Using Love Feature

1. Click **"❤️ Start Love"** from main menu
2. Enter how many times you want to love
3. See the love messages generated with your accounts

## 🗂️ Project Structure

```
telegram-vault-bot/
│
├── bot.py                 # Main bot entry point
├── config.py              # Configuration management
├── database.py            # SQLite database operations
├── states.py              # FSM state management
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create from .env.example)
├── .env.example          # Environment template
│
├── handlers/             # Bot command handlers
│   ├── start.py          # Start command & main menu
│   ├── add_account.py    # Account addition flow
│   ├── accounts.py       # Account viewing
│   ├── info.py           # User info feature
│   └── love.py           # Love feature
│
├── utils/                # Utility modules
│   ├── auth.py           # Pyrogram authentication
│   └── encryption.py     # Password encryption
│
└── sessions/             # Temporary session files (auto-created)
```

## 🔐 Security Features

- **Encrypted Passwords** - All 2FA passwords encrypted with Fernet
- **Secure Sessions** - Session strings stored securely in database
- **Private Bot** - Designed for personal use only
- **Clean Temp Files** - Temporary session files automatically removed
- **Password Deletion** - User's password messages deleted after processing

## 🗄️ Database Schema

### Users Table
```sql
- id (Primary Key)
- telegram_user_id (Unique)
- created_at
```

### Accounts Table
```sql
- id (Primary Key)
- user_id (Foreign Key)
- phone (Unique with user_id)
- password (Encrypted)
- session_string
- created_at
```

### Saved Info Table
```sql
- id (Primary Key)
- user_id (Foreign Key)
- target_user_id
- name
- username
- created_at
```

## 🔄 Switching to MongoDB (Optional)

To use MongoDB instead of SQLite:

1. Install MongoDB driver:
```bash
pip install pymongo
```

2. Update `.env`:
```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=telegram_vault
```

3. Implement MongoDB adapter in `database.py` using the same interface

## 🛡️ Error Handling

The bot handles:
- ✅ Invalid phone numbers
- ✅ Wrong OTP codes
- ✅ Expired OTP codes
- ✅ Invalid 2FA passwords
- ✅ Network errors
- ✅ User not found errors
- ✅ Duplicate account prevention

## 📝 Important Notes

1. **Keep your `.env` file secure** - Never commit it to Git
2. **API credentials are sensitive** - Don't share them
3. **Session strings are powerful** - They provide full account access
4. **Use responsibly** - Respect Telegram's terms of service
5. **Bot is private** - Designed for personal use, not public deployment

## 🚨 Troubleshooting

### Bot doesn't start
- Check if all credentials in `.env` are correct
- Ensure Python 3.10+ is installed
- Verify all dependencies are installed

### OTP not received
- Check phone number format (must include country code with +)
- Ensure the number is registered on Telegram
- Check for Telegram service status

### "Invalid API_ID or API_HASH"
- Verify credentials from https://my.telegram.org
- Ensure no extra spaces in `.env` file
- API_ID must be a number (no quotes)

### Database errors
- Ensure write permissions in project directory
- Check if `vault.db` is not locked by another process

## 🔧 Development

### Adding New Features

1. Create handler in `handlers/` directory
2. Define states in `states.py` if needed
3. Register handler in `bot.py`
4. Update README with new feature

### Code Style

- Follow PEP 8 guidelines
- Use async/await for all Pyrogram operations
- Add docstrings to functions
- Handle exceptions properly

## 📄 License

This project is for educational purposes. Use responsibly and in accordance with Telegram's Terms of Service.

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## ⚠️ Disclaimer

This bot is provided as-is. The developers are not responsible for any misuse or violations of Telegram's Terms of Service. Use at your own risk.

## 📞 Support

For issues or questions:
1. Check this README thoroughly
2. Review error messages carefully
3. Ensure all setup steps are followed correctly

---

**Made with ❤️ using Pyrogram**

*Last Updated: May 2026*
