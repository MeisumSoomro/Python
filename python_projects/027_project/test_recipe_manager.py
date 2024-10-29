import unittest
import os
import tkinter as tk
from recipe_manager import RecipeManager
from recipe_database import RecipeDatabase
from recipe_search import RecipeSearch

class TestRecipeManager(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = RecipeManager(self.root)
        
    def tearDown(self):
        self.root.destroy()
        # Clean up test files
        test_files = ['recipes.db', 'test_recipes.json']
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
                
    def test_database_operations(self):
        db = RecipeDatabase()
        
        # Test adding recipe
        test_recipe = {
            'name': 'Test Recipe',
            'category': 'Dinner',
            'prep_time': '30 mins',
            'rating': 4,
            'image_path': '',
            'ingredients': 'Test ingredients',
            'instructions': 'Test instructions',
            'created_date': '2024-01-01 12:00'
        }
        
        db.add_recipe(test_recipe)
        recipes = db.get_all_recipes()
        
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0]['name'], 'Test Recipe')
        
        # Test search
        search = RecipeSearch(db)
        results = search.search_recipes('test')
        self.assertEqual(len(results), 1)
        
        # Test category filter
        results = search.search_recipes('', 'Dinner')
        self.assertEqual(len(results), 1)
        
        db.close()
        
    def test_recipe_search(self):
        db = RecipeDatabase()
        search = RecipeSearch(db)
        
        # Add test recipes
        recipes = [
            {
                'name': 'Pasta Recipe',
                'category': 'Dinner',
                'prep_time': '20 mins',
                'rating': 4,
                'image_path': '',
                'ingredients': 'pasta, sauce, cheese',
                'instructions': 'Cook pasta',
                'created_date': '2024-01-01 12:00'
            },
            {
                'name': 'Salad Recipe',
                'category': 'Lunch',
                'prep_time': '10 mins',
                'rating': 3,
                'image_path': '',
                'ingredients': 'lettuce, tomato, cucumber',
                'instructions': 'Mix ingredients',
                'created_date': '2024-01-01 12:00'
            }
        ]
        
        for recipe in recipes:
            db.add_recipe(recipe)
            
        # Test text search
        results = search.search_recipes('pasta')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Pasta Recipe')
        
        # Test ingredient search
        results = search.search_by_ingredients(['lettuce', 'tomato'])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Salad Recipe')
        
        db.close()
        
if __name__ == '__main__':
    try:
        import PIL
        unittest.main()
    except ImportError as e:
        print("Error: Missing required dependencies.")
        print("Please install required packages using:")
        print("pip install -r requirements.txt")
        exit(1) 