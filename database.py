"""
Database models and operations for Xiaohongshu scraper
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class Database:
    """Database management class"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
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
        
        # Create notes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            title TEXT,
            content TEXT,
            author TEXT,
            publish_time TIMESTAMP,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            collections_count INTEGER DEFAULT 0,
            shares_count INTEGER DEFAULT 0,
            url TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(id, topic)
        )
        ''')
        
        # Create daily ranking table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            note_id TEXT NOT NULL,
            rank_position INTEGER,
            likes_count INTEGER,
            comments_count INTEGER,
            collections_count INTEGER,
            publish_time TIMESTAMP,
            scraped_date DATE,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes(id)
        )
        ''')
        
        # Create topic tracking table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_scraped_at TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def insert_note(self, note_data: Dict[str, Any]) -> bool:
        """Insert or update a note"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT OR REPLACE INTO notes 
            (id, topic, title, content, author, publish_time, likes_count, 
             comments_count, collections_count, shares_count, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                note_data.get('id'),
                note_data.get('topic'),
                note_data.get('title'),
                note_data.get('content'),
                note_data.get('author'),
                note_data.get('publish_time'),
                note_data.get('likes_count', 0),
                note_data.get('comments_count', 0),
                note_data.get('collections_count', 0),
                note_data.get('shares_count', 0),
                note_data.get('url')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error inserting note: {e}")
            return False
    
    def insert_ranking(self, ranking_data: Dict[str, Any]) -> bool:
        """Insert daily ranking data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO daily_ranking
            (topic, note_id, rank_position, likes_count, comments_count, 
             collections_count, publish_time, scraped_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ranking_data.get('topic'),
                ranking_data.get('note_id'),
                ranking_data.get('rank_position'),
                ranking_data.get('likes_count'),
                ranking_data.get('comments_count'),
                ranking_data.get('collections_count'),
                ranking_data.get('publish_time'),
                ranking_data.get('scraped_date')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error inserting ranking: {e}")
            return False
    
    def get_notes_by_topic(self, topic: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get notes by topic"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM notes 
            WHERE topic = ? 
            ORDER BY scraped_at DESC 
            LIMIT ?
            ''', (topic, limit))
            
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting notes: {e}")
            return []
    
    def get_today_ranking(self, topic: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get today's ranking for a topic"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM daily_ranking 
            WHERE topic = ? AND date(scraped_date) = date('now')
            ORDER BY rank_position ASC 
            LIMIT ?
            ''', (topic, limit))
            
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting today's ranking: {e}")
            return []
    
    def record_topic(self, topic_name: str) -> bool:
        """Record a topic"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT OR IGNORE INTO topics (topic_name) VALUES (?)
            ''', (topic_name,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error recording topic: {e}")
            return False
    
    def update_topic_scrape_time(self, topic_name: str) -> bool:
        """Update topic last scrape time"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE topics SET last_scraped_at = CURRENT_TIMESTAMP 
            WHERE topic_name = ?
            ''', (topic_name,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating topic scrape time: {e}")
            return False
