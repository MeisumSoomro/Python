import sqlite3
import json
import os
from datetime import datetime

class NoteDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('notes.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        """Create necessary database tables"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                created_date TEXT NOT NULL,
                modified_date TEXT NOT NULL
            )
        ''')
        self.conn.commit()
        
    def add_note(self, note):
        """Add a new note"""
        self.cursor.execute('''
            INSERT INTO notes (title, category, content, created_date, modified_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            note['title'],
            note['category'],
            note['content'],
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            note['modified_date']
        ))
        self.conn.commit()
        
    def update_note(self, note):
        """Update an existing note"""
        self.cursor.execute('''
            UPDATE notes
            SET title=?, category=?, content=?, modified_date=?
            WHERE id=?
        ''', (
            note['title'],
            note['category'],
            note['content'],
            note['modified_date'],
            note['id']
        ))
        self.conn.commit()
        
    def delete_note(self, note_id):
        """Delete a note"""
        self.cursor.execute('DELETE FROM notes WHERE id=?', (note_id,))
        self.conn.commit()
        
    def get_note(self, note_id):
        """Get a single note by ID"""
        self.cursor.execute('SELECT * FROM notes WHERE id=?', (note_id,))
        row = self.cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None
        
    def get_all_notes(self):
        """Get all notes"""
        self.cursor.execute('SELECT * FROM notes ORDER BY modified_date DESC')
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
        
    def search_notes(self, search_text, category=None):
        """Search notes by text and category"""
        query = '''
            SELECT * FROM notes 
            WHERE (LOWER(title) LIKE ? OR LOWER(content) LIKE ?)
        '''
        params = [f'%{search_text}%', f'%{search_text}%']
        
        if category and category != "All":
            query += ' AND category = ?'
            params.append(category)
            
        query += ' ORDER BY modified_date DESC'
        
        self.cursor.execute(query, params)
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
        
    def import_notes(self, file_path):
        """Import notes from JSON file"""
        with open(file_path, 'r') as f:
            notes = json.load(f)
            
        for note in notes:
            if 'created_date' not in note:
                note['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            if 'modified_date' not in note:
                note['modified_date'] = note['created_date']
            self.add_note(note)
            
    def export_notes(self, file_path):
        """Export notes to JSON file"""
        notes = self.get_all_notes()
        with open(file_path, 'w') as f:
            json.dump(notes, f, indent=2)
            
    def _row_to_dict(self, row):
        """Convert a database row to a note dictionary"""
        return {
            'id': row[0],
            'title': row[1],
            'category': row[2],
            'content': row[3],
            'created_date': row[4],
            'modified_date': row[5]
        }
        
    def close(self):
        """Close the database connection"""
        self.conn.close() 