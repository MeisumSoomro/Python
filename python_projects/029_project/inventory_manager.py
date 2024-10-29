import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import json
import os
from inventory_database import InventoryDatabase
from barcode_handler import BarcodeHandler
from report_generator import ReportGenerator

class InventoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        
        # Initialize handlers
        self.db = InventoryDatabase()
        self.barcode = BarcodeHandler()
        self.reports = ReportGenerator()
        
        # Product categories
        self.categories = ["Electronics", "Clothing", "Food", "Books", 
                         "Home", "Office", "Other"]
        
        # Create GUI elements
        self.create_menu()
        self.create_main_layout()
        
        # Load inventory
        self.load_inventory()
        
        # Check for low stock
        self.check_low_stock()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Product", command=self.new_product)
        file_menu.add_command(label="Import Data", command=self.import_data)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="Stock Report", 
                               command=self.generate_stock_report)
        reports_menu.add_command(label="Sales Report", 
                               command=self.generate_sales_report)
        reports_menu.add_command(label="Low Stock Alert", 
                               command=self.show_low_stock)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Scan Barcode", command=self.scan_barcode)
        tools_menu.add_command(label="Generate Barcode", 
                             command=self.generate_barcode)
        
    def create_main_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel with search and filters
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Search
        search_frame = ttk.LabelFrame(left_frame, text="Search")
        search_frame.pack(fill=tk.X, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.search_products)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(fill=tk.X, 
                                                                  padx=5, pady=5)
        
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
        
        # Quick add product
        ttk.Button(left_frame, text="Add Product", 
                  command=self.new_product).pack(fill=tk.X, pady=5)
        
        # Right panel with inventory list
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Inventory treeview
        columns = ('SKU', 'Name', 'Category', 'Quantity', 'Price')
        self.inventory_tree = ttk.Treeview(right_frame, columns=columns, 
                                         show='headings')
        
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            self.inventory_tree.column(col, width=100)
        
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.inventory_tree.bind('<Double-1>', self.edit_product)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, 
                                command=self.inventory_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        
    def new_product(self):
        product_window = tk.Toplevel(self.root)
        product_window.title("New Product")
        product_window.geometry("400x500")
        
        # Product form
        form_frame = ttk.Frame(product_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # SKU
        ttk.Label(form_frame, text="SKU:").pack(anchor='w')
        sku_entry = ttk.Entry(form_frame)
        sku_entry.pack(fill=tk.X)
        
        # Generate SKU button
        ttk.Button(form_frame, text="Generate SKU", 
                  command=lambda: sku_entry.insert(0, self.generate_sku())
                  ).pack(pady=2)
        
        # Name
        ttk.Label(form_frame, text="Product Name:").pack(anchor='w')
        name_entry = ttk.Entry(form_frame)
        name_entry.pack(fill=tk.X)
        
        # Category
        ttk.Label(form_frame, text="Category:").pack(anchor='w')
        category_combo = ttk.Combobox(form_frame, values=self.categories)
        category_combo.pack(fill=tk.X)
        
        # Quantity
        ttk.Label(form_frame, text="Quantity:").pack(anchor='w')
        quantity_entry = ttk.Entry(form_frame)
        quantity_entry.pack(fill=tk.X)
        
        # Price
        ttk.Label(form_frame, text="Price:").pack(anchor='w')
        price_entry = ttk.Entry(form_frame)
        price_entry.pack(fill=tk.X)
        
        # Low stock threshold
        ttk.Label(form_frame, text="Low Stock Alert Threshold:").pack(anchor='w')
        threshold_entry = ttk.Entry(form_frame)
        threshold_entry.pack(fill=tk.X)
        
        # Description
        ttk.Label(form_frame, text="Description:").pack(anchor='w')
        desc_text = tk.Text(form_frame, height=4)
        desc_text.pack(fill=tk.BOTH, expand=True)
        
        def save_product():
            # Validate inputs
            try:
                sku = sku_entry.get().strip()
                name = name_entry.get().strip()
                category = category_combo.get().strip()
                quantity = int(quantity_entry.get().strip())
                price = float(price_entry.get().strip())
                threshold = int(threshold_entry.get().strip())
                description = desc_text.get(1.0, tk.END).strip()
                
                if not all([sku, name, category]):
                    messagebox.showwarning("Warning", 
                                         "Please fill in all required fields")
                    return
                    
                # Create product dictionary
                product = {
                    'sku': sku,
                    'name': name,
                    'category': category,
                    'quantity': quantity,
                    'price': price,
                    'threshold': threshold,
                    'description': description,
                    'created_date': datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                # Save to database
                self.db.add_product(product)
                self.load_inventory()
                product_window.destroy()
                
            except ValueError:
                messagebox.showerror("Error", 
                                   "Please enter valid numbers for quantity and price")
                
        ttk.Button(form_frame, text="Save Product", 
                  command=save_product).pack(pady=10)
        
    def edit_product(self, event=None):
        selection = self.inventory_tree.selection()
        if not selection:
            return
            
        # Get product details
        product_id = selection[0]
        product = self.db.get_product(product_id)
        if not product:
            return
            
        product_window = tk.Toplevel(self.root)
        product_window.title("Edit Product")
        product_window.geometry("400x500")
        
        # Product form
        form_frame = ttk.Frame(product_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Pre-fill form with existing data
        ttk.Label(form_frame, text="SKU:").pack(anchor='w')
        sku_entry = ttk.Entry(form_frame)
        sku_entry.insert(0, product['sku'])
        sku_entry.config(state='readonly')
        sku_entry.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Product Name:").pack(anchor='w')
        name_entry = ttk.Entry(form_frame)
        name_entry.insert(0, product['name'])
        name_entry.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Category:").pack(anchor='w')
        category_combo = ttk.Combobox(form_frame, values=self.categories)
        category_combo.set(product['category'])
        category_combo.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Quantity:").pack(anchor='w')
        quantity_entry = ttk.Entry(form_frame)
        quantity_entry.insert(0, product['quantity'])
        quantity_entry.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Price:").pack(anchor='w')
        price_entry = ttk.Entry(form_frame)
        price_entry.insert(0, product['price'])
        price_entry.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Low Stock Alert Threshold:").pack(anchor='w')
        threshold_entry = ttk.Entry(form_frame)
        threshold_entry.insert(0, product['threshold'])
        threshold_entry.pack(fill=tk.X)
        
        ttk.Label(form_frame, text="Description:").pack(anchor='w')
        desc_text = tk.Text(form_frame, height=4)
        desc_text.insert(1.0, product['description'])
        desc_text.pack(fill=tk.BOTH, expand=True)
        
        def update_product():
            try:
                # Update product dictionary
                updated_product = {
                    'id': product['id'],
                    'sku': product['sku'],
                    'name': name_entry.get().strip(),
                    'category': category_combo.get().strip(),
                    'quantity': int(quantity_entry.get().strip()),
                    'price': float(price_entry.get().strip()),
                    'threshold': int(threshold_entry.get().strip()),
                    'description': desc_text.get(1.0, tk.END).strip()
                }
                
                # Save to database
                self.db.update_product(updated_product)
                self.load_inventory()
                product_window.destroy()
                
            except ValueError:
                messagebox.showerror("Error", 
                                   "Please enter valid numbers for quantity and price")
                
        def delete_product():
            if messagebox.askyesno("Confirm Delete", 
                                 "Are you sure you want to delete this product?"):
                self.db.delete_product(product['id'])
                self.load_inventory()
                product_window.destroy()
                
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Update", 
                  command=update_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", 
                  command=delete_product).pack(side=tk.LEFT, padx=5)
        
    def generate_sku(self):
        """Generate a unique SKU"""
        return self.db.generate_sku()
        
    def search_products(self, *args):
        """Search products based on search text and filters"""
        search_text = self.search_var.get().lower()
        category = self.category_var.get()
        
        products = self.db.search_products(search_text, category)
        self.update_inventory_list(products)
        
    def apply_filters(self, event=None):
        """Apply category filter"""
        self.search_products()
        
    def update_inventory_list(self, products):
        """Update inventory list with search/filter results"""
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        
        for product in products:
            self.inventory_tree.insert('', 'end', product['id'], values=(
                product['sku'],
                product['name'],
                product['category'],
                product['quantity'],
                f"${product['price']:.2f}"
            ))
            
    def load_inventory(self):
        """Load all products from database"""
        products = self.db.get_all_products()
        self.update_inventory_list(products)
        
    def check_low_stock(self):
        """Check for low stock items"""
        low_stock = self.db.get_low_stock_products()
        if low_stock:
            messagebox.showwarning(
                "Low Stock Alert",
                f"There are {len(low_stock)} items with low stock!"
            )
            
    def scan_barcode(self):
        """Scan barcode using camera"""
        barcode = self.barcode.scan_barcode()
        if barcode:
            product = self.db.get_product_by_sku(barcode)
            if product:
                self.show_product_details(product)
            else:
                messagebox.showinfo("Not Found", 
                                  "No product found with this barcode")
                
    def generate_barcode(self):
        """Generate barcode for selected product"""
        selection = self.inventory_tree.selection()
        if not selection:
            return
            
        product = self.db.get_product(selection[0])
        if product:
            self.barcode.generate_barcode(product['sku'])
            
    def generate_stock_report(self):
        """Generate stock report"""
        products = self.db.get_all_products()
        self.reports.generate_stock_report(products)
        
    def generate_sales_report(self):
        """Generate sales report"""
        sales = self.db.get_sales_data()
        self.reports.generate_sales_report(sales)
        
    def show_low_stock(self):
        """Show low stock items"""
        products = self.db.get_low_stock_products()
        self.reports.show_low_stock_report(products)
        
    def import_data(self):
        """Import inventory data from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.db.import_data(file_path)
                self.load_inventory()
                messagebox.showinfo("Success", "Data imported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not import data: {str(e)}")
                
    def export_data(self):
        """Export inventory data to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.db.export_data(file_path)
                messagebox.showinfo("Success", "Data exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export data: {str(e)}")

def main():
    root = tk.Tk()
    root.geometry("1200x800")
    app = InventoryManager(root)
    root.mainloop()

if __name__ == "__main__":
    main() 