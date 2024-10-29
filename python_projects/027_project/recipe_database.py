import sqlite3
import json
import os
from datetime import datetime

class RecipeDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('recipes.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        """Create necessary database tables if they don't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                prep_time TEXT NOT NULL,
                rating INTEGER NOT NULL,
                image_path TEXT,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                created_date TEXT NOT NULL
            )
        ''')
        self.conn.commit()
        
    def add_recipe(self, recipe):
        """Add a new recipe to the database"""
        self.cursor.execute('''
            INSERT INTO recipes (name, category, prep_time, rating,
                               image_path, ingredients, instructions, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            recipe['name'],
            recipe['category'],
            recipe['prep_time'],
            recipe['rating'],
            recipe['image_path'],
            recipe['ingredients'],
            recipe['instructions'],
            recipe['created_date']
        ))
        self.conn.commit()
        
    def update_recipe(self, recipe):
        """Update an existing recipe"""
        self.cursor.execute('''
            UPDATE recipes
            SET name=?, category=?, prep_time=?, rating=?,
                image_path=?, ingredients=?, instructions=?
            WHERE id=?
        ''', (
            recipe['name'],
            recipe['category'],
            recipe['prep_time'],
            recipe['rating'],
            recipe['image_path'],
            recipe['ingredients'],
            recipe['instructions'],
            recipe['id']
        ))
        self.conn.commit()
        
    def delete_recipe(self, recipe_id):
        """Delete a recipe from the database"""
        self.cursor.execute('DELETE FROM recipes WHERE id=?', (recipe_id,))
        self.conn.commit()
        
    def get_recipe(self, recipe_id):
        """Get a single recipe by ID"""
        self.cursor.execute('SELECT * FROM recipes WHERE id=?', (recipe_id,))
        row = self.cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None
        
    def get_all_recipes(self):
        """Get all recipes from the database"""
        self.cursor.execute('SELECT * FROM recipes ORDER BY created_date DESC')
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
        
    def search_recipes(self, search_text, category=None):
        """Search recipes by text and category"""
        query = '''
            SELECT * FROM recipes 
            WHERE (LOWER(name) LIKE ? OR LOWER(ingredients) LIKE ?)
        '''
        params = [f'%{search_text}%', f'%{search_text}%']
        
        if category and category != "All":
            query += ' AND category = ?'
            params.append(category)
            
        self.cursor.execute(query, params)
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
        
    def get_recipes_by_category(self, category):
        """Get all recipes in a specific category"""
        self.cursor.execute('SELECT * FROM recipes WHERE category=?', (category,))
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
        
    def import_recipes(self, file_path):
        """Import recipes from JSON file"""
        with open(file_path, 'r') as f:
            recipes = json.load(f)
            
        for recipe in recipes:
            # Ensure recipe has created_date
            if 'created_date' not in recipe:
                recipe['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.add_recipe(recipe)
            
    def export_recipes(self, file_path):
        """Export all recipes to JSON file"""
        recipes = self.get_all_recipes()
        with open(file_path, 'w') as f:
            json.dump(recipes, f, indent=2)
            
    def _row_to_dict(self, row):
        """Convert a database row to a recipe dictionary"""
        return {
            'id': row[0],
            'name': row[1],
            'category': row[2],
            'prep_time': row[3],
            'rating': row[4],
            'image_path': row[5],
            'ingredients': row[6],
            'instructions': row[7],
            'created_date': row[8]
        }
        
    def close(self):
        """Close the database connection"""
        self.conn.close() 