import sqlite3
import json
import os
from datetime import datetime
import random
import string

class InventoryDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('inventory.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        """Create necessary database tables"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                threshold INTEGER NOT NULL,
                description TEXT,
                created_date TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                sale_date TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        self.conn.commit()
        
    def generate_sku(self):
        """Generate a unique SKU"""
        while True:
            # Generate random SKU: 2 letters + 4 digits
            letters = ''.join(random.choices(string.ascii_uppercase, k=2))
            numbers = ''.join(random.choices(string.digits, k=4))
            sku = f"{letters}{numbers}"
            
            # Check if SKU exists
            self.cursor.execute('SELECT COUNT(*) FROM products WHERE sku=?', (sku,))
            if self.cursor.fetchone()[0] == 0:
                return sku
                
    def add_product(self, product):
        """Add a new product"""
        self.cursor.execute('''
            INSERT INTO products (sku, name, category, quantity, price,
                                threshold, description, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product['sku'],
            product['name'],
            product['category'],
            product['quantity'],
            product['price'],
            product['threshold'],
            product['description'],
            product['created_date']
        ))
        self.conn.commit()
        
    def update_product(self, product):
        """Update an existing product"""
        self.cursor.execute('''
            UPDATE products
            SET name=?, category=?, quantity=?, price=?,
                threshold=?, description=?
            WHERE id=?
        ''', (
            product['name'],
            product['category'],
            product['quantity'],
            product['price'],
            product['threshold'],
            product['description'],
            product['id']
        ))
        self.conn.commit()
        
    def delete_product(self, product_id):
        """Delete a product"""
        self.cursor.execute('DELETE FROM products WHERE id=?', (product_id,))
        self.conn.commit()
        
    def get_product(self, product_id):
        """Get a single product by ID"""
        self.cursor.execute('SELECT * FROM products WHERE id=?', (product_id,))
        row = self.cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None
        
    def get_product_by_sku(self, sku):
        """Get a product by SKU"""
        self.cursor.execute('SELECT * FROM products WHERE sku=?', (sku,))
        row = self.cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None
        
    def get_all_products(self):
        """Get all products"""
        self.cursor.execute('SELECT * FROM products ORDER BY name')
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
        
    def search_products(self, search_text, category=None):
        """Search products by text and category"""
        query = '''
            SELECT * FROM products 
            WHERE (LOWER(name) LIKE ? OR LOWER(sku) LIKE ?)
        '''
        params = [f'%{search_text}%', f'%{search_text}%']
        
        if category and category != "All":
            query += ' AND category = ?'
            params.append(category)
            
        self.cursor.execute(query, params)
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
        
    def get_low_stock_products(self):
        """Get products with quantity below threshold"""
        self.cursor.execute(
            'SELECT * FROM products WHERE quantity <= threshold'
        )
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
        
    def record_sale(self, product_id, quantity):
        """Record a product sale"""
        self.cursor.execute('''
            INSERT INTO sales (product_id, quantity, sale_date)
            VALUES (?, ?, ?)
        ''', (
            product_id,
            quantity,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        
        # Update product quantity
        self.cursor.execute('''
            UPDATE products
            SET quantity = quantity - ?
            WHERE id = ?
        ''', (quantity, product_id))
        
        self.conn.commit()
        
    def get_sales_data(self, start_date=None, end_date=None):
        """Get sales data for reporting"""
        query = '''
            SELECT p.name, p.sku, p.category, 
                   SUM(s.quantity) as total_quantity,
                   COUNT(*) as total_sales,
                   p.price * SUM(s.quantity) as total_revenue
            FROM sales s
            JOIN products p ON s.product_id = p.id
        '''
        params = []
        
        if start_date and end_date:
            query += ' WHERE s.sale_date BETWEEN ? AND ?'
            params.extend([start_date, end_date])
            
        query += ' GROUP BY p.id'
        
        self.cursor.execute(query, params)
        return [dict(zip([
            'name', 'sku', 'category', 'quantity', 
            'sales_count', 'revenue'
        ], row)) for row in self.cursor.fetchall()]
        
    def import_data(self, file_path):
        """Import inventory data from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        for product in data:
            if 'created_date' not in product:
                product['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.add_product(product)
            
    def export_data(self, file_path):
        """Export inventory data to JSON file"""
        products = self.get_all_products()
        with open(file_path, 'w') as f:
            json.dump(products, f, indent=2)
            
    def _row_to_dict(self, row):
        """Convert a database row to a product dictionary"""
        return {
            'id': row[0],
            'sku': row[1],
            'name': row[2],
            'category': row[3],
            'quantity': row[4],
            'price': row[5],
            'threshold': row[6],
            'description': row[7],
            'created_date': row[8]
        }
        
    def close(self):
        """Close the database connection"""
        self.conn.close() 