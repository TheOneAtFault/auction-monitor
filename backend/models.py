import sqlite3
import os
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app_data.db')

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create listeners table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listeners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            search_term TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT TRUE,
            UNIQUE(email, search_term)
        )
    ''')
    
    # Create auction_items table to track processed items
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS auction_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            description TEXT,
            price TEXT,
            end_time TEXT,
            image_url TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create notifications table to track sent notifications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listener_id INTEGER,
            auction_item_id INTEGER,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (listener_id) REFERENCES listeners (id),
            FOREIGN KEY (auction_item_id) REFERENCES auction_items (id)
        )
    ''')
    
    conn.commit()
    conn.close()

class Listener:
    def __init__(self, id=None, email=None, search_term=None, created_at=None, active=True):
        self.id = id
        self.email = email
        self.search_term = search_term
        self.created_at = created_at
        self.active = active
    
    def save(self):
        """Save the listener to the database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO listeners (email, search_term, active)
                VALUES (?, ?, ?)
            ''', (self.email, self.search_term, self.active))
            self.id = cursor.lastrowid
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Duplicate entry
        finally:
            conn.close()
    
    @staticmethod
    def get_all():
        """Get all active listeners"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM listeners WHERE active = TRUE')
        rows = cursor.fetchall()
        conn.close()
        
        listeners = []
        for row in rows:
            listener = Listener(
                id=row[0],
                email=row[1],
                search_term=row[2],
                created_at=row[3],
                active=row[4]
            )
            listeners.append(listener)
        
        return listeners
    
    @staticmethod
    def get_by_email(email):
        """Get all listeners for a specific email"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM listeners WHERE email = ? AND active = TRUE', (email,))
        rows = cursor.fetchall()
        conn.close()
        
        listeners = []
        for row in rows:
            listener = Listener(
                id=row[0],
                email=row[1],
                search_term=row[2],
                created_at=row[3],
                active=row[4]
            )
            listeners.append(listener)
        
        return listeners
    
    @staticmethod
    def delete(listener_id):
        """Delete a listener by ID"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE listeners SET active = FALSE WHERE id = ?', (listener_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted

class AuctionItem:
    def __init__(self, id=None, title=None, url=None, description=None, price=None, 
                 end_time=None, image_url=None, scraped_at=None):
        self.id = id
        self.title = title
        self.url = url
        self.description = description
        self.price = price
        self.end_time = end_time
        self.image_url = image_url
        self.scraped_at = scraped_at
    
    def save(self):
        """Save the auction item to the database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO auction_items (title, url, description, price, end_time, image_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.title, self.url, self.description, self.price, self.end_time, self.image_url))
            self.id = cursor.lastrowid
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Duplicate URL
        finally:
            conn.close()
    
    @staticmethod
    def url_exists(url):
        """Check if an auction item with this URL already exists"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM auction_items WHERE url = ?', (url,))
        exists = cursor.fetchone() is not None
        conn.close()
        
        return exists
    
    @staticmethod
    def get_all():
        """Get all auction items from the database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM auction_items ORDER BY scraped_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        items = []
        for row in rows:
            item = AuctionItem(
                id=row[0], title=row[1], url=row[2], description=row[3],
                price=row[4], end_time=row[5], image_url=row[6], scraped_at=row[7]
            )
            items.append(item)
        
        return items

class Notification:
    @staticmethod
    def save(listener_id, auction_item_id):
        """Save a notification record"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications (listener_id, auction_item_id)
            VALUES (?, ?)
        ''', (listener_id, auction_item_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def already_sent(listener_id, auction_item_id):
        """Check if a notification has already been sent"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM notifications 
            WHERE listener_id = ? AND auction_item_id = ?
        ''', (listener_id, auction_item_id))
        exists = cursor.fetchone() is not None
        conn.close()
        
        return exists

# Initialize database when module is imported
init_database()
