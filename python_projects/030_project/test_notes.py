import unittest
import os
import tkinter as tk
from note_editor import NoteEditor
from note_database import NoteDatabase
from note_sync import CloudSync

class TestNoteEditor(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = NoteEditor(self.root)
        
    def tearDown(self):
        self.root.destroy()
        # Clean up test files
        test_files = [
            'notes.db',
            'test_notes.json',
            'sync_config.json'
        ]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
                
    def test_database_operations(self):
        db = NoteDatabase()
        
        # Test adding note
        test_note = {
            'title': 'Test Note',
            'category': 'Work',
            'content': '# Test Content\nThis is a test note.',
            'modified_date': '2024-01-01 12:00'
        }
        
        db.add_note(test_note)
        notes = db.get_all_notes()
        
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]['title'], 'Test Note')
        
        # Test updating note
        notes[0]['content'] = 'Updated content'
        db.update_note(notes[0])
        
        updated = db.get_note(notes[0]['id'])
        self.assertEqual(updated['content'], 'Updated content')
        
        # Test search
        results = db.search_notes('test')
        self.assertEqual(len(results), 1)
        
        db.close()
        
    def test_markdown_rendering(self):
        # Test markdown to HTML conversion
        markdown_text = "# Test Heading\n**Bold text**"
        self.app.editor.delete('1.0', tk.END)
        self.app.editor.insert('1.0', markdown_text)
        
        self.app.update_preview()
        html = self.app.preview.get_html()
        
        self.assertIn("<h1>", html)
        self.assertIn("<strong>", html)
        
if __name__ == '__main__':
    try:
        import markdown
        import tkhtmlview
        unittest.main()
    except ImportError as e:
        print("Error: Missing required dependencies.")
        print("Please install required packages using:")
        print("pip install -r requirements.txt")
        exit(1) 