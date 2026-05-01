import sqlite3
from typing import List, Optional, Dict
import config

class Database:
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                phone TEXT NOT NULL,
                password TEXT,
                session_string TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, phone)
            )
        """)
        
        # Saved info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                target_user_id INTEGER NOT NULL,
                name TEXT,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, target_user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_or_create_user(self, telegram_user_id: int) -> int:
        """Get or create user, return user ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE telegram_user_id = ?", (telegram_user_id,))
        result = cursor.fetchone()
        
        if result:
            user_id = result['id']
        else:
            cursor.execute("INSERT INTO users (telegram_user_id) VALUES (?)", (telegram_user_id,))
            user_id = cursor.lastrowid
            conn.commit()
        
        conn.close()
        return user_id
    
    def add_account(self, telegram_user_id: int, phone: str, password: Optional[str], session_string: str) -> bool:
        """Add new account"""
        try:
            user_id = self.get_or_create_user(telegram_user_id)
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO accounts (user_id, phone, password, session_string)
                VALUES (?, ?, ?, ?)
            """, (user_id, phone, password, session_string))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Account already exists
            return False
    
    def get_accounts(self, telegram_user_id: int) -> List[Dict]:
        """Get all accounts for user"""
        user_id = self.get_or_create_user(telegram_user_id)
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT phone, password, session_string, created_at
            FROM accounts
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        
        accounts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return accounts
    
    def get_account_by_phone(self, telegram_user_id: int, phone: str) -> Optional[Dict]:
        """Get specific account by phone"""
        user_id = self.get_or_create_user(telegram_user_id)
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT phone, password, session_string, created_at
            FROM accounts
            WHERE user_id = ? AND phone = ?
        """, (user_id, phone))
        
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def get_accounts_count(self, telegram_user_id: int) -> int:
        """Get total number of accounts"""
        user_id = self.get_or_create_user(telegram_user_id)
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM accounts WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result['count']
    
    def save_user_info(self, telegram_user_id: int, target_user_id: int, name: str, username: Optional[str]) -> bool:
        """Save user info"""
        try:
            user_id = self.get_or_create_user(telegram_user_id)
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO saved_info (user_id, target_user_id, name, username)
                VALUES (?, ?, ?, ?)
            """, (user_id, target_user_id, name, username))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving user info: {e}")
            return False
    
    def delete_account(self, telegram_user_id: int, phone: str) -> bool:
        """Delete account"""
        try:
            user_id = self.get_or_create_user(telegram_user_id)
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM accounts WHERE user_id = ? AND phone = ?", (user_id, phone))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

# Global database instance
db = Database()
