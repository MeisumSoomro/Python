import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk
import os
from recipe_database import RecipeDatabase
from recipe_search import RecipeSearch

class RecipeManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Manager")
        
        # Initialize database
        self.db = RecipeDatabase()
        self.search = RecipeSearch(self.db)
        
        # Recipe categories
        self.categories = ["Breakfast", "Lunch", "Dinner", "Dessert", 
                         "Snack", "Beverage", "Other"]
        
        # Create GUI elements
        self.create_menu()
        self.create_main_layout()
        
        # Load recipes
        self.load_recipes()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Recipe", command=self.new_recipe)
        file_menu.add_command(label="Import Recipes", command=self.import_recipes)
        file_menu.add_command(label="Export Recipes", command=self.export_recipes)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Generate Shopping List", 
                             command=self.generate_shopping_list)
        tools_menu.add_command(label="Meal Planner", 
                             command=self.show_meal_planner)
        
    def create_main_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel with search and filters
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Search
        search_frame = ttk.LabelFrame(left_frame, text="Search")
        search_frame.pack(fill=tk.X, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.search_recipes)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(fill=tk.X, padx=5, pady=5)
        
        # Filters
        filter_frame = ttk.LabelFrame(left_frame, text="Filters")
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="Category:").pack(pady=2)
        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(filter_frame, 
                                    values=["All"] + self.categories,
                                    textvariable=self.category_var)
        category_combo.pack(fill=tk.X, padx=5)
        category_combo.bind('<<ComboboxSelected>>', self.apply_filters)
        
        # Quick add recipe
        ttk.Button(left_frame, text="Add Recipe", 
                  command=self.new_recipe).pack(fill=tk.X, pady=5)
        
        # Right panel with recipe list and details
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Recipe list
        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Recipe treeview
        columns = ('Name', 'Category', 'Prep Time', 'Rating')
        self.recipe_tree = ttk.Treeview(list_frame, columns=columns, 
                                      show='headings')
        
        for col in columns:
            self.recipe_tree.heading(col, text=col)
            self.recipe_tree.column(col, width=100)
        
        self.recipe_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.recipe_tree.bind('<<TreeviewSelect>>', self.show_recipe_details)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                command=self.recipe_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recipe_tree.configure(yscrollcommand=scrollbar.set)
        
        # Recipe details frame
        self.details_frame = ttk.LabelFrame(right_frame, text="Recipe Details")
        self.details_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Initialize empty details
        self.clear_recipe_details()
        
    def clear_recipe_details(self):
        """Clear and initialize empty recipe details view"""
        for widget in self.details_frame.winfo_children():
            widget.destroy()
            
        ttk.Label(self.details_frame, 
                 text="Select a recipe to view details").pack(pady=20)
        
    def show_recipe_details(self, event=None):
        """Display details of selected recipe"""
        selection = self.recipe_tree.selection()
        if not selection:
            return
            
        # Get recipe details from database
        recipe_id = selection[0]
        recipe = self.db.get_recipe(recipe_id)
        if not recipe:
            return
            
        # Clear current details
        for widget in self.details_frame.winfo_children():
            widget.destroy()
            
        # Create details layout
        details_container = ttk.Frame(self.details_frame)
        details_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side - Image and basic info
        left_details = ttk.Frame(details_container)
        left_details.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Recipe image
        if recipe['image_path'] and os.path.exists(recipe['image_path']):
            img = Image.open(recipe['image_path'])
            img.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(img)
            img_label = ttk.Label(left_details, image=photo)
            img_label.image = photo
            img_label.pack(pady=5)
            
        # Basic info
        ttk.Label(left_details, 
                 text=recipe['name'],
                 font=('Arial', 12, 'bold')).pack(pady=2)
        ttk.Label(left_details, 
                 text=f"Category: {recipe['category']}").pack()
        ttk.Label(left_details, 
                 text=f"Prep Time: {recipe['prep_time']}").pack()
        ttk.Label(left_details, 
                 text=f"Rating: {'★' * recipe['rating']}").pack()
        
        # Right side - Ingredients and instructions
        right_details = ttk.Frame(details_container)
        right_details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Ingredients
        ttk.Label(right_details, 
                 text="Ingredients:",
                 font=('Arial', 10, 'bold')).pack(anchor='w')
        ingredients_text = tk.Text(right_details, height=6, width=40)
        ingredients_text.insert('1.0', recipe['ingredients'])
        ingredients_text.config(state='disabled')
        ingredients_text.pack(fill=tk.X, pady=5)
        
        # Instructions
        ttk.Label(right_details, 
                 text="Instructions:",
                 font=('Arial', 10, 'bold')).pack(anchor='w')
        instructions_text = tk.Text(right_details, height=8, width=40)
        instructions_text.insert('1.0', recipe['instructions'])
        instructions_text.config(state='disabled')
        instructions_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(right_details)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Edit", 
                  command=lambda: self.edit_recipe(recipe)
                  ).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", 
                  command=lambda: self.delete_recipe(recipe_id)
                  ).pack(side=tk.LEFT, padx=5)
        
    def new_recipe(self):
        """Create new recipe dialog"""
        recipe_window = tk.Toplevel(self.root)
        recipe_window.title("New Recipe")
        recipe_window.geometry("600x800")
        
        # Recipe form
        form_frame = ttk.Frame(recipe_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Basic info
        ttk.Label(form_frame, text="Recipe Name:").pack(anchor='w')
        name_entry = ttk.Entry(form_frame)
        name_entry.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Category:").pack(anchor='w')
        category_combo = ttk.Combobox(form_frame, values=self.categories)
        category_combo.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Preparation Time:").pack(anchor='w')
        prep_time_entry = ttk.Entry(form_frame)
        prep_time_entry.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Rating:").pack(anchor='w')
        rating_var = tk.IntVar(value=3)
        rating_frame = ttk.Frame(form_frame)
        rating_frame.pack(fill=tk.X)
        for i in range(1, 6):
            ttk.Radiobutton(rating_frame, text=f"{i}★", 
                          variable=rating_var, value=i).pack(side=tk.LEFT)
        
        # Image
        ttk.Label(form_frame, text="Recipe Image:").pack(anchor='w')
        image_frame = ttk.Frame(form_frame)
        image_frame.pack(fill=tk.X)
        
        image_path_var = tk.StringVar()
        ttk.Entry(image_frame, textvariable=image_path_var, 
                 state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def choose_image():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if file_path:
                image_path_var.set(file_path)
                
        ttk.Button(image_frame, text="Browse", 
                  command=choose_image).pack(side=tk.LEFT, padx=5)
        
        # Ingredients
        ttk.Label(form_frame, text="Ingredients:").pack(anchor='w')
        ingredients_text = tk.Text(form_frame, height=8)
        ingredients_text.pack(fill=tk.X)
        
        # Instructions
        ttk.Label(form_frame, text="Instructions:").pack(anchor='w')
        instructions_text = tk.Text(form_frame, height=12)
        instructions_text.pack(fill=tk.BOTH, expand=True)
        
        def save_recipe():
            # Validate inputs
            name = name_entry.get().strip()
            category = category_combo.get().strip()
            prep_time = prep_time_entry.get().strip()
            ingredients = ingredients_text.get('1.0', tk.END).strip()
            instructions = instructions_text.get('1.0', tk.END).strip()
            
            if not all([name, category, prep_time, ingredients, instructions]):
                messagebox.showwarning("Warning", "Please fill in all required fields")
                return
                
            # Create recipe dictionary
            recipe = {
                'name': name,
                'category': category,
                'prep_time': prep_time,
                'rating': rating_var.get(),
                'image_path': image_path_var.get(),
                'ingredients': ingredients,
                'instructions': instructions,
                'created_date': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
            # Save to database
            self.db.add_recipe(recipe)
            self.load_recipes()
            recipe_window.destroy()
            
        # Save button
        ttk.Button(form_frame, text="Save Recipe", 
                  command=save_recipe).pack(pady=10)
        
    def edit_recipe(self, recipe):
        """Edit existing recipe"""
        recipe_window = tk.Toplevel(self.root)
        recipe_window.title("Edit Recipe")
        recipe_window.geometry("600x800")
        
        # Recipe form (similar to new_recipe but pre-filled)
        form_frame = ttk.Frame(recipe_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Basic info
        ttk.Label(form_frame, text="Recipe Name:").pack(anchor='w')
        name_entry = ttk.Entry(form_frame)
        name_entry.insert(0, recipe['name'])
        name_entry.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Category:").pack(anchor='w')
        category_combo = ttk.Combobox(form_frame, values=self.categories)
        category_combo.set(recipe['category'])
        category_combo.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Preparation Time:").pack(anchor='w')
        prep_time_entry = ttk.Entry(form_frame)
        prep_time_entry.insert(0, recipe['prep_time'])
        prep_time_entry.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Rating:").pack(anchor='w')
        rating_var = tk.IntVar(value=recipe['rating'])
        rating_frame = ttk.Frame(form_frame)
        rating_frame.pack(fill=tk.X)
        for i in range(1, 6):
            ttk.Radiobutton(rating_frame, text=f"{i}★", 
                          variable=rating_var, value=i).pack(side=tk.LEFT)
        
        # Image
        ttk.Label(form_frame, text="Recipe Image:").pack(anchor='w')
        image_frame = ttk.Frame(form_frame)
        image_frame.pack(fill=tk.X)
        
        image_path_var = tk.StringVar(value=recipe['image_path'])
        ttk.Entry(image_frame, textvariable=image_path_var, 
                 state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def choose_image():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if file_path:
                image_path_var.set(file_path)
                
        ttk.Button(image_frame, text="Browse", 
                  command=choose_image).pack(side=tk.LEFT, padx=5)
        
        # Ingredients
        ttk.Label(form_frame, text="Ingredients:").pack(anchor='w')
        ingredients_text = tk.Text(form_frame, height=8)
        ingredients_text.insert('1.0', recipe['ingredients'])
        ingredients_text.pack(fill=tk.X)
        
        # Instructions
        ttk.Label(form_frame, text="Instructions:").pack(anchor='w')
        instructions_text = tk.Text(form_frame, height=12)
        instructions_text.insert('1.0', recipe['instructions'])
        instructions_text.pack(fill=tk.BOTH, expand=True)
        
        def update_recipe():
            # Validate inputs
            name = name_entry.get().strip()
            category = category_combo.get().strip()
            prep_time = prep_time_entry.get().strip()
            ingredients = ingredients_text.get('1.0', tk.END).strip()
            instructions = instructions_text.get('1.0', tk.END).strip()
            
            if not all([name, category, prep_time, ingredients, instructions]):
                messagebox.showwarning("Warning", "Please fill in all required fields")
                return
                
            # Update recipe dictionary
            updated_recipe = {
                'id': recipe['id'],
                'name': name,
                'category': category,
                'prep_time': prep_time,
                'rating': rating_var.get(),
                'image_path': image_path_var.get(),
                'ingredients': ingredients,
                'instructions': instructions,
                'created_date': recipe['created_date']
            }
            
            # Save to database
            self.db.update_recipe(updated_recipe)
            self.load_recipes()
            recipe_window.destroy()
            
        # Update button
        ttk.Button(form_frame, text="Update Recipe", 
                  command=update_recipe).pack(pady=10)
        
    def delete_recipe(self, recipe_id):
        """Delete recipe from database"""
        if messagebox.askyesno("Confirm Delete", 
                             "Are you sure you want to delete this recipe?"):
            self.db.delete_recipe(recipe_id)
            self.load_recipes()
            self.clear_recipe_details()
            
    def search_recipes(self, *args):
        """Search recipes based on search text and filters"""
        search_text = self.search_var.get().lower()
        category = self.category_var.get()
        
        recipes = self.search.search_recipes(search_text, category)
        self.update_recipe_list(recipes)
        
    def apply_filters(self, event=None):
        """Apply category filter"""
        self.search_recipes()
        
    def update_recipe_list(self, recipes):
        """Update recipe list with search/filter results"""
        self.recipe_tree.delete(*self.recipe_tree.get_children())
        
        for recipe in recipes:
            self.recipe_tree.insert('', 'end', recipe['id'], values=(
                recipe['name'],
                recipe['category'],
                recipe['prep_time'],
                '★' * recipe['rating']
            ))
            
    def load_recipes(self):
        """Load all recipes from database"""
        recipes = self.db.get_all_recipes()
        self.update_recipe_list(recipes)
        
    def import_recipes(self):
        """Import recipes from JSON file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.db.import_recipes(file_path)
                self.load_recipes()
                messagebox.showinfo("Success", "Recipes imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not import recipes: {str(e)}")
                
    def export_recipes(self):
        """Export recipes to JSON file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.db.export_recipes(file_path)
                messagebox.showinfo("Success", "Recipes exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export recipes: {str(e)}")
                
    def generate_shopping_list(self):
        """Generate shopping list from selected recipes"""
        # TODO: Implement shopping list generation
        pass
        
    def show_meal_planner(self):
        """Show meal planning window"""
        # TODO: Implement meal planner
        pass

def main():
    root = tk.Tk()
    root.geometry("1000x800")
    app = RecipeManager(root)
    root.mainloop()

if __name__ == "__main__":
    main() 