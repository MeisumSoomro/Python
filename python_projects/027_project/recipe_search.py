class RecipeSearch:
    def __init__(self, database):
        self.db = database
        
    def search_recipes(self, search_text, category=None):
        """Search recipes with text and category filters"""
        if not search_text and (not category or category == "All"):
            return self.db.get_all_recipes()
            
        return self.db.search_recipes(search_text.lower(), category)
        
    def search_by_ingredients(self, ingredients):
        """Search recipes that contain specific ingredients"""
        recipes = self.db.get_all_recipes()
        matching_recipes = []
        
        for recipe in recipes:
            recipe_ingredients = recipe['ingredients'].lower()
            if all(ing.lower() in recipe_ingredients for ing in ingredients):
                matching_recipes.append(recipe)
                
        return matching_recipes
        
    def get_recipe_suggestions(self, ingredients):
        """Get recipe suggestions based on available ingredients"""
        all_recipes = self.db.get_all_recipes()
        suggestions = []
        
        for recipe in all_recipes:
            recipe_ingredients = recipe['ingredients'].lower()
            matching_count = sum(1 for ing in ingredients 
                               if ing.lower() in recipe_ingredients)
            if matching_count > 0:
                suggestions.append({
                    'recipe': recipe,
                    'match_score': matching_count / len(ingredients)
                })
                
        # Sort by match score
        suggestions.sort(key=lambda x: x['match_score'], reverse=True)
        return [s['recipe'] for s in suggestions] 