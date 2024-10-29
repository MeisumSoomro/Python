import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ReportGenerator:
    def __init__(self):
        self.report_dir = "reports"
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
            
    def generate_stock_report(self, products):
        """Generate stock level report"""
        # Create DataFrame
        df = pd.DataFrame(products)
        
        # Generate report file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.report_dir, f"stock_report_{timestamp}.xlsx")
        
        # Create Excel writer
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            # Stock levels sheet
            df[['sku', 'name', 'category', 'quantity', 'threshold']].to_excel(
                writer, sheet_name='Stock Levels', index=False
            )
            
            # Low stock sheet
            low_stock = df[df['quantity'] <= df['threshold']]
            if not low_stock.empty:
                low_stock[['sku', 'name', 'quantity', 'threshold']].to_excel(
                    writer, sheet_name='Low Stock Alert', index=False
                )
                
        # Show report window
        self.show_stock_report_window(df)
        
    def generate_sales_report(self, sales):
        """Generate sales analysis report"""
        # Create DataFrame
        df = pd.DataFrame(sales)
        
        # Generate report file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.report_dir, f"sales_report_{timestamp}.xlsx")
        
        # Create Excel writer
        with pd.ExcelWriter(report_path, engine='openpyxl') as writer:
            # Sales summary sheet
            df.to_excel(writer, sheet_name='Sales Summary', index=False)
            
            # Category analysis
            pivot = pd.pivot_table(df, 
                                 values=['quantity', 'revenue'],
                                 index='category',
                                 aggfunc='sum')
            pivot.to_excel(writer, sheet_name='Category Analysis')
            
        # Show report window
        self.show_sales_report_window(df)
        
    def show_stock_report_window(self, df):
        """Display stock report in a window"""
        window = tk.Toplevel()
        window.title("Stock Report")
        window.geometry("800x600")
        
        # Create notebook for different views
        notebook = ttk.Notebook(window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Stock levels tab
        stock_frame = ttk.Frame(notebook)
        notebook.add(stock_frame, text="Stock Levels")
        
        # Create stock level chart
        fig, ax = plt.subplots(figsize=(8, 4))
        df.groupby('category')['quantity'].sum().plot(kind='bar', ax=ax)
        ax.set_title('Stock Levels by Category')
        ax.set_ylabel('Quantity')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=stock_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Low stock tab
        low_stock_frame = ttk.Frame(notebook)
        notebook.add(low_stock_frame, text="Low Stock")
        
        # Create low stock table
        low_stock = df[df['quantity'] <= df['threshold']]
        columns = ('SKU', 'Name', 'Quantity', 'Threshold')
        tree = ttk.Treeview(low_stock_frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
            
        for _, row in low_stock.iterrows():
            tree.insert('', 'end', values=(
                row['sku'],
                row['name'],
                row['quantity'],
                row['threshold']
            ))
            
        tree.pack(fill=tk.BOTH, expand=True)
        
    def show_sales_report_window(self, df):
        """Display sales report in a window"""
        window = tk.Toplevel()
        window.title("Sales Report")
        window.geometry("800x600")
        
        # Create notebook for different views
        notebook = ttk.Notebook(window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sales summary tab
        summary_frame = ttk.Frame(notebook)
        notebook.add(summary_frame, text="Sales Summary")
        
        # Create sales chart
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        
        # Revenue by category
        df.groupby('category')['revenue'].sum().plot(kind='bar', ax=ax1)
        ax1.set_title('Revenue by Category')
        ax1.set_ylabel('Revenue ($)')
        
        # Quantity by category
        df.groupby('category')['quantity'].sum().plot(kind='bar', ax=ax2)
        ax2.set_title('Units Sold by Category')
        ax2.set_ylabel('Quantity')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=summary_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Details tab
        details_frame = ttk.Frame(notebook)
        notebook.add(details_frame, text="Details")
        
        # Create details table
        columns = ('Name', 'SKU', 'Category', 'Quantity', 'Revenue')
        tree = ttk.Treeview(details_frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
            
        for _, row in df.iterrows():
            tree.insert('', 'end', values=(
                row['name'],
                row['sku'],
                row['category'],
                row['quantity'],
                f"${row['revenue']:.2f}"
            ))
            
        tree.pack(fill=tk.BOTH, expand=True)
        
    def show_low_stock_report(self, products):
        """Display low stock alert window"""
        window = tk.Toplevel()
        window.title("Low Stock Alert")
        window.geometry("600x400")
        
        # Create table
        columns = ('SKU', 'Name', 'Quantity', 'Threshold')
        tree = ttk.Treeview(window, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
            
        for product in products:
            tree.insert('', 'end', values=(
                product['sku'],
                product['name'],
                product['quantity'],
                product['threshold']
            ))
            
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5) 