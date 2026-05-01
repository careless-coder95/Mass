import os
from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
from utils.pdf_generator import generate_accounts_pdf

async def export_pdf_handler(client: Client, message: Message):
    user_id = message.from_user.id
    
    accounts = db.get_accounts(user_id)
    
    if not accounts:
        await message.reply_text("❌ No accounts found to export.")
        return
    
    file_path = f"accounts_{user_id}.pdf"
    
    # Generate PDF
    generate_accounts_pdf(accounts, file_path)
    
    # Send file
    await message.reply_document(
        document=file_path,
        caption="📄 Your Accounts Backup"
    )
    
    # Delete file after sending
    try:
        os.remove(file_path)
    except:
        pass

def setup_export_handler(app: Client):
    app.add_handler(filters.command("exportpdf") & filters.private, export_pdf_handler)
