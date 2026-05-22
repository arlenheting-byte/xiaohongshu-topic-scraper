"""
Query and analyze scraped data
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import logging

from database import Database
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class DataAnalyzer:
    """Analyze scraped data"""
    
    def __init__(self):
        self.db = Database()
    
    def get_today_top_notes(self, topic: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get today's top notes by engagement"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT n.*, dr.rank_position, dr.scraped_date
            FROM notes n
            JOIN daily_ranking dr ON n.id = dr.note_id
            WHERE n.topic = ? AND date(dr.scraped_date) = date('now')
            ORDER BY (n.likes_count + n.comments_count + n.collections_count) DESC
            LIMIT ?
            ''', (topic, limit))
            
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting top notes: {e}")
            return []
    
    def get_trending_notes(self, topic: str, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """Get trending notes (highest engagement growth in last N hours)"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT n.*, COUNT(dr.id) as times_appeared,
                   AVG(dr.rank_position) as avg_rank,
                   MAX(dr.likes_count) as max_likes
            FROM notes n
            JOIN daily_ranking dr ON n.id = dr.note_id
            WHERE n.topic = ? 
              AND dr.scraped_at > datetime('now', '-{} hours')
            GROUP BY n.id
            ORDER BY max_likes DESC, times_appeared DESC
            LIMIT ?
            '''.format(hours), (topic, limit))
            
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting trending notes: {e}")
            return []
    
    def get_topic_stats(self, topic: str) -> Dict[str, Any]:
        """Get statistics for a topic"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Total notes
            cursor.execute('SELECT COUNT(*) as count FROM notes WHERE topic = ?', (topic,))
            total_notes = cursor.fetchone()['count']
            
            # Average engagement
            cursor.execute('''
            SELECT AVG(likes_count) as avg_likes,
                   AVG(comments_count) as avg_comments,
                   AVG(collections_count) as avg_collections
            FROM notes WHERE topic = ?
            ''', (topic,))
            avg_engagement = dict(cursor.fetchone())
            
            # Max engagement
            cursor.execute('''
            SELECT MAX(likes_count) as max_likes,
                   MAX(comments_count) as max_comments,
                   MAX(collections_count) as max_collections
            FROM notes WHERE topic = ?
            ''', (topic,))
            max_engagement = dict(cursor.fetchone())
            
            # Top authors
            cursor.execute('''
            SELECT author, COUNT(*) as count
            FROM notes WHERE topic = ?
            GROUP BY author
            ORDER BY count DESC
            LIMIT 10
            ''', (topic,))
            top_authors = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'topic': topic,
                'total_notes': total_notes,
                'average_engagement': avg_engagement,
                'max_engagement': max_engagement,
                'top_authors': top_authors
            }
        except Exception as e:
            logger.error(f"Error getting topic stats: {e}")
            return {}
    
    def compare_topics(self, topics: List[str]) -> Dict[str, Any]:
        """Compare statistics across multiple topics"""
        comparison = {}
        for topic in topics:
            comparison[topic] = self.get_topic_stats(topic)
        return comparison
    
    def export_to_json(self, topic: str, filepath: str) -> bool:
        """Export topic data to JSON"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM notes WHERE topic = ?', (topic,))
            notes = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'topic': topic,
                    'export_time': datetime.now().isoformat(),
                    'total_notes': len(notes),
                    'notes': notes
                }, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported {len(notes)} notes to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False

def main():
    """Example usage"""
    analyzer = DataAnalyzer()
    
    # Get today's top notes
    top_notes = analyzer.get_today_top_notes('穿搭', limit=10)
    print("\n=== Today's Top Notes ===")
    for note in top_notes:
        print(f"Title: {note['title']}")
        print(f"Likes: {note['likes_count']}, Comments: {note['comments_count']}, Collections: {note['collections_count']}")
        print()
    
    # Get topic statistics
    stats = analyzer.get_topic_stats('穿搭')
    print("\n=== Topic Statistics ===")
    print(f"Total Notes: {stats.get('total_notes', 0)}")
    print(f"Average Likes: {stats.get('average_engagement', {}).get('avg_likes', 0):.0f}")
    print()
    
    # Export to JSON
    analyzer.export_to_json('穿搭', 'export_穿搭.json')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
