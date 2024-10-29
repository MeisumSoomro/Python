import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime
import pygments
from pygments import lexers, formatters, highlight
from pygments.util import ClassNotFound
import sqlite3
from dataclasses import dataclass, asdict
import re

@dataclass
class CodeSnippet:
    id: Optional[int]
    title: str
    code: str
    language: str
    description: str
    tags: Set[str]
    created_at: str
    updated_at: str
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['tags'] = list(self.tags)  # Convert set to list for JSON
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CodeSnippet':
        data['tags'] = set(data['tags'])  # Convert list back to set
        return cls(**data)

class SnippetManager:
    def __init__(self):
        self.db_path = Path("snippets.db")
        self.setup_database()

    def setup_database(self):
        """Initialize SQLite database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create snippets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                code TEXT NOT NULL,
                language TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Create tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Create snippet_tags table for many-to-many relationship
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snippet_tags (
                snippet_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (snippet_id) REFERENCES snippets (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id),
                PRIMARY KEY (snippet_id, tag_id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def add_snippet(self, title: str, code: str, language: str, description: str = "", tags: Set[str] = None) -> bool:
        """Add a new code snippet"""
        if not title or not code:
            print("Title and code are required!")
            return False
        
        # Try to detect language if not provided
        if not language:
            try:
                lexer = lexers.guess_lexer(code)
                language = lexer.name.lower()
            except ClassNotFound:
                language = "text"
        
        tags = tags or set()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Insert snippet
            cursor.execute('''
                INSERT INTO snippets (title, code, language, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, code, language, description, now, now))
            
            snippet_id = cursor.lastrowid
            
            # Handle tags
            for tag in tags:
                # Insert tag if it doesn't exist
                cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
                cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
                tag_id = cursor.fetchone()[0]
                
                # Link tag to snippet
                cursor.execute('INSERT INTO snippet_tags (snippet_id, tag_id) VALUES (?, ?)',
                             (snippet_id, tag_id))
            
            conn.commit()
            print(f"Snippet '{title}' added successfully!")
            return True
            
        except sqlite3.Error as e:
            print(f"Error adding snippet: {e}")
            conn.rollback()
            return False
            
        finally:
            conn.close()

    def get_snippet(self, snippet_id: int) -> Optional[CodeSnippet]:
        """Retrieve a snippet by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get snippet
            cursor.execute('''
                SELECT id, title, code, language, description, created_at, updated_at
                FROM snippets WHERE id = ?
            ''', (snippet_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Get tags for snippet
            cursor.execute('''
                SELECT t.name FROM tags t
                JOIN snippet_tags st ON t.id = st.tag_id
                WHERE st.snippet_id = ?
            ''', (snippet_id,))
            
            tags = {row[0] for row in cursor.fetchall()}
            
            return CodeSnippet(
                id=row[0],
                title=row[1],
                code=row[2],
                language=row[3],
                description=row[4],
                tags=tags,
                created_at=row[5],
                updated_at=row[6]
            )
            
        finally:
            conn.close()

    def update_snippet(self, snippet_id: int, title: str = None, code: str = None,
                      language: str = None, description: str = None, tags: Set[str] = None) -> bool:
        """Update an existing snippet"""
        snippet = self.get_snippet(snippet_id)
        if not snippet:
            print(f"Snippet with ID {snippet_id} not found!")
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            updates = []
            values = []
            
            if title is not None:
                updates.append("title = ?")
                values.append(title)
            if code is not None:
                updates.append("code = ?")
                values.append(code)
            if language is not None:
                updates.append("language = ?")
                values.append(language)
            if description is not None:
                updates.append("description = ?")
                values.append(description)
            
            if updates:
                updates.append("updated_at = ?")
                values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                values.append(snippet_id)
                
                query = f"UPDATE snippets SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, values)
            
            if tags is not None:
                # Remove old tags
                cursor.execute('DELETE FROM snippet_tags WHERE snippet_id = ?', (snippet_id,))
                
                # Add new tags
                for tag in tags:
                    cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
                    cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
                    tag_id = cursor.fetchone()[0]
                    cursor.execute('INSERT INTO snippet_tags (snippet_id, tag_id) VALUES (?, ?)',
                                 (snippet_id, tag_id))
            
            conn.commit()
            print(f"Snippet updated successfully!")
            return True
            
        except sqlite3.Error as e:
            print(f"Error updating snippet: {e}")
            conn.rollback()
            return False
            
        finally:
            conn.close()

    def delete_snippet(self, snippet_id: int) -> bool:
        """Delete a snippet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Delete snippet tags
            cursor.execute('DELETE FROM snippet_tags WHERE snippet_id = ?', (snippet_id,))
            
            # Delete snippet
            cursor.execute('DELETE FROM snippets WHERE id = ?', (snippet_id,))
            
            if cursor.rowcount == 0:
                print(f"Snippet with ID {snippet_id} not found!")
                return False
            
            conn.commit()
            print(f"Snippet deleted successfully!")
            return True
            
        except sqlite3.Error as e:
            print(f"Error deleting snippet: {e}")
            conn.rollback()
            return False
            
        finally:
            conn.close()

    def search_snippets(self, query: str = "", tags: Set[str] = None) -> List[CodeSnippet]:
        """Search snippets by text and/or tags"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            base_query = '''
                SELECT DISTINCT s.id, s.title, s.code, s.language, s.description, 
                       s.created_at, s.updated_at
                FROM snippets s
            '''
            
            conditions = []
            params = []
            
            if query:
                conditions.append('''
                    (s.title LIKE ? OR s.code LIKE ? OR s.description LIKE ?)
                ''')
                query = f"%{query}%"
                params.extend([query, query, query])
            
            if tags:
                base_query += '''
                    JOIN snippet_tags st ON s.id = st.snippet_id
                    JOIN tags t ON st.tag_id = t.id
                '''
                placeholders = ','.join('?' * len(tags))
                conditions.append(f't.name IN ({placeholders})')
                params.extend(tags)
            
            if conditions:
                base_query += ' WHERE ' + ' AND '.join(conditions)
            
            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            
            snippets = []
            for row in rows:
                # Get tags for each snippet
                cursor.execute('''
                    SELECT t.name FROM tags t
                    JOIN snippet_tags st ON t.id = st.tag_id
                    WHERE st.snippet_id = ?
                ''', (row[0],))
                
                tags = {tag[0] for tag in cursor.fetchall()}
                
                snippet = CodeSnippet(
                    id=row[0],
                    title=row[1],
                    code=row[2],
                    language=row[3],
                    description=row[4],
                    tags=tags,
                    created_at=row[5],
                    updated_at=row[6]
                )
                snippets.append(snippet)
            
            return snippets
            
        finally:
            conn.close()

    def get_all_tags(self) -> List[str]:
        """Get all existing tags"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT name FROM tags ORDER BY name')
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

    def highlight_code(self, code: str, language: str) -> str:
        """Apply syntax highlighting to code"""
        try:
            lexer = lexers.get_lexer_by_name(language.lower())
        except ClassNotFound:
            try:
                lexer = lexers.guess_lexer(code)
            except ClassNotFound:
                lexer = lexers.get_lexer_by_name('text')
        
        formatter = formatters.TerminalFormatter()
        return highlight(code, lexer, formatter)

def main():
    manager = SnippetManager()
    
    while True:
        print("\nCode Snippet Manager")
        print("1. Add Snippet")
        print("2. View Snippet")
        print("3. Update Snippet")
        print("4. Delete Snippet")
        print("5. Search Snippets")
        print("6. List All Tags")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == "1":
            title = input("Enter snippet title: ")
            print("Enter code (press Ctrl+D or Ctrl+Z on a new line to finish):")
            code_lines = []
            while True:
                try:
                    line = input()
                    code_lines.append(line)
                except EOFError:
                    break
            code = "\n".join(code_lines)
            
            language = input("Enter language (or leave empty for auto-detection): ")
            description = input("Enter description (optional): ")
            tags_input = input("Enter tags (comma-separated): ")
            tags = {tag.strip() for tag in tags_input.split(",")} if tags_input else set()
            
            manager.add_snippet(title, code, language, description, tags)
        
        elif choice == "2":
            snippet_id = int(input("Enter snippet ID: "))
            snippet = manager.get_snippet(snippet_id)
            
            if snippet:
                print(f"\nTitle: {snippet.title}")
                print(f"Language: {snippet.language}")
                print(f"Description: {snippet.description}")
                print(f"Tags: {', '.join(snippet.tags)}")
                print(f"Created: {snippet.created_at}")
                print(f"Updated: {snippet.updated_at}")
                print("\nCode:")
                print(manager.highlight_code(snippet.code, snippet.language))
            else:
                print("Snippet not found!")
        
        elif choice == "3":
            snippet_id = int(input("Enter snippet ID: "))
            snippet = manager.get_snippet(snippet_id)
            
            if not snippet:
                print("Snippet not found!")
                continue
            
            print("\nLeave fields empty to keep current values")
            title = input(f"Title [{snippet.title}]: ").strip()
            print(f"Current code:\n{snippet.code}")
            print("\nEnter new code (press Ctrl+D or Ctrl+Z on a new line to finish, or just press it immediately to keep current code):")
            code_lines = []
            try:
                while True:
                    line = input()
                    code_lines.append(line)
            except EOFError:
                pass
            
            code = "\n".join(code_lines) if code_lines else None
            language = input(f"Language [{snippet.language}]: ").strip()
            description = input(f"Description [{snippet.description}]: ").strip()
            tags_input = input(f"Tags [{', '.join(snippet.tags)}]: ").strip()
            
            manager.update_snippet(
                snippet_id,
                title=title if title else None,
                code=code if code else None,
                language=language if language else None,
                description=description if description else None,
                tags={tag.strip() for tag in tags_input.split(",")} if tags_input else None
            )
        
        elif choice == "4":
            snippet_id = int(input("Enter snippet ID: "))
            if input(f"Are you sure you want to delete snippet {snippet_id}? (y/n): ").lower() == 'y':
                manager.delete_snippet(snippet_id)
        
        elif choice == "5":
            query = input("Enter search query (optional): ")
            tags_input = input("Enter tags to filter by (comma-separated, optional): ")
            tags = {tag.strip() for tag in tags_input.split(",")} if tags_input else None
            
            snippets = manager.search_snippets(query, tags)
            if snippets:
                print(f"\nFound {len(snippets)} snippets:")
                for snippet in snippets:
                    print(f"\nID: {snippet.id}")
                    print(f"Title: {snippet.title}")
                    print(f"Language: {snippet.language}")
                    print(f"Tags: {', '.join(snippet.tags)}")
                    print("-" * 30)
            else:
                print("No snippets found!")
        
        elif choice == "6":
            tags = manager.get_all_tags()
            if tags:
                print("\nAll Tags:")
                for tag in tags:
                    print(f"- {tag}")
            else:
                print("No tags found!")
        
        elif choice == "7":
            print("Thank you for using Code Snippet Manager!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 