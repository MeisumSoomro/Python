Code Snippet Manager
==================

Project Structure:
----------------
043_project/
├── code_snippet_manager.py  # Main program file
├── snippets.db             # SQLite database (created on first run)
└── README.txt             # This file

Requirements:
------------
1. Python 3.7 or higher
2. Required Python packages:
   - pygments (for syntax highlighting)

Installation:
------------
1. Install required package:
   pip install pygments

Features:
--------
1. Snippet Management
   - Add and store code snippets
   - Update existing snippets
   - Delete snippets
   - View snippet details

2. Syntax Highlighting
   - Automatic language detection
   - Multiple language support
   - Terminal-friendly formatting

3. Tag System
   - Tag-based organization
   - Multiple tags per snippet
   - Tag search functionality

4. Search Capabilities
   - Search by title
   - Search by content
   - Search by tags
   - Combined search

Database Schema:
--------------
1. snippets
   - id: INTEGER PRIMARY KEY
   - title: TEXT
   - code: TEXT
   - language: TEXT
   - description: TEXT
   - created_at: TEXT
   - updated_at: TEXT

2. tags
   - id: INTEGER PRIMARY KEY
   - name: TEXT UNIQUE

3. snippet_tags
   - snippet_id: INTEGER
   - tag_id: INTEGER
   - FOREIGN KEY references

Classes:
-------
1. CodeSnippet
   - Data class for snippet information
   - Handles serialization/deserialization
   - Manages snippet attributes

2. SnippetManager
   - Main management class
   - Database operations
   - Search functionality
   - Tag management

Usage:
-----
1. Run the program:
   python code_snippet_manager.py

2. Main Operations:
   - Add new snippets
   - View existing snippets
   - Update snippets
   - Delete snippets
   - Search snippets
   - Manage tags

3. Adding Snippets:
   - Enter title
   - Paste or type code
   - Select language (or auto-detect)
   - Add description
   - Add tags

Important Notes:
--------------
1. Database:
   - SQLite database for storage
   - Automatic creation on first run
   - Maintains relationships

2. Code Input:
   - Multi-line code support
   - Ctrl+D or Ctrl+Z to finish input
   - Language auto-detection

3. Tags:
   - Comma-separated input
   - Case-sensitive
   - Multiple tags per snippet

4. Search:
   - Partial matching
   - Case-insensitive
   - Combined criteria

Troubleshooting:
--------------
1. Common Issues:
   - ModuleNotFoundError: Install required package
   - Database errors: Check permissions
   - Input issues: Follow EOF instructions

2. Data Management:
   - Regular backups recommended
   - Check disk space
   - Verify database integrity

For Support:
----------
[Your contact information or repository link here] 