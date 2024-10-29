import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime, timedelta
import calendar
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class BudgetAnalysis:
    def __init__(self, transactions=None):
        self.transactions = transactions or self.load_transactions()
        
    def load_transactions(self):
        try:
            if os.path.exists('budget_data.json'):
                with open('budget_data.json', 'r') as f:
                    return defaultdict(list, json.load(f))
            return defaultdict(list)
        except Exception as e:
            print(f"Error loading transactions: {e}")
            return defaultdict(list)

    def show_monthly_summary(self, parent_window):
        summary_window = tk.Toplevel(parent_window)
        summary_window.title("Monthly Summary")
        summary_window.geometry("800x600")

        # Create notebook for different views
        notebook = ttk.Notebook(summary_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Monthly Overview Tab
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="Overview")
        self._create_monthly_overview(overview_frame)

        # Trends Tab
        trends_frame = ttk.Frame(notebook)
        notebook.add(trends_frame, text="Trends")
        self._create_trends_view(trends_frame)

    def _create_monthly_overview(self, parent):
        current_month = datetime.now().strftime("%Y-%m")
        transactions = self.transactions[current_month]

        # Summary Frame
        summary_frame = ttk.LabelFrame(parent, text="Monthly Summary")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)

        # Calculate statistics
        income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        balance = income - expenses

        # Display statistics
        ttk.Label(summary_frame, 
                 text=f"Total Income: ${income:.2f}").pack(pady=2)
        ttk.Label(summary_frame, 
                 text=f"Total Expenses: ${expenses:.2f}").pack(pady=2)
        ttk.Label(summary_frame, 
                 text=f"Net Balance: ${balance:.2f}").pack(pady=2)

        # Create pie chart for expense categories
        fig, ax = plt.subplots(figsize=(6, 4))
        self._create_expense_pie_chart(ax, transactions)
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_trends_view(self, parent):
        # Create line chart showing income vs expenses over time
        fig, ax = plt.subplots(figsize=(8, 5))
        self._create_trends_chart(ax)
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def show_category_analysis(self, parent_window):
        analysis_window = tk.Toplevel(parent_window)
        analysis_window.title("Category Analysis")
        analysis_window.geometry("800x600")

        # Create notebook for different views
        notebook = ttk.Notebook(analysis_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Category Overview Tab
        category_frame = ttk.Frame(notebook)
        notebook.add(category_frame, text="Categories")
        self._create_category_overview(category_frame)

        # Budget Goals Tab
        goals_frame = ttk.Frame(notebook)
        notebook.add(goals_frame, text="Budget Goals")
        self._create_budget_goals(goals_frame)

    def _create_category_overview(self, parent):
        current_month = datetime.now().strftime("%Y-%m")
        
        # Create category breakdown
        categories_frame = ttk.LabelFrame(parent, text="Category Breakdown")
        categories_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create treeview for categories
        columns = ('Category', 'Total Spent', 'Percentage')
        tree = ttk.Treeview(categories_frame, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Calculate and display category totals
        category_totals = defaultdict(float)
        total_expenses = 0

        for trans in self.transactions[current_month]:
            if trans['type'] == 'expense':
                category_totals[trans['category']] += trans['amount']
                total_expenses += trans['amount']

        for category, amount in category_totals.items():
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            tree.insert('', 'end', values=(
                category,
                f"${amount:.2f}",
                f"{percentage:.1f}%"
            ))

    def _create_budget_goals(self, parent):
        goals_frame = ttk.LabelFrame(parent, text="Budget Goals")
        goals_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sample budget goals (you can make this configurable)
        budget_goals = {
            "Food": 500,
            "Transportation": 200,
            "Entertainment": 150,
            "Shopping": 300
        }

        current_month = datetime.now().strftime("%Y-%m")
        
        # Create progress bars for each category
        for category, goal in budget_goals.items():
            frame = ttk.Frame(goals_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            spent = sum(t['amount'] for t in self.transactions[current_month] 
                       if t['type'] == 'expense' and t['category'] == category)
            
            percentage = min((spent / goal * 100) if goal > 0 else 0, 100)
            
            ttk.Label(frame, text=f"{category}:").pack(side=tk.LEFT)
            progress = ttk.Progressbar(frame, length=200, mode='determinate')
            progress.pack(side=tk.LEFT, padx=5)
            progress['value'] = percentage
            ttk.Label(frame, 
                     text=f"${spent:.2f} / ${goal:.2f}").pack(side=tk.LEFT)

    def _create_expense_pie_chart(self, ax, transactions):
        category_totals = defaultdict(float)
        
        for trans in transactions:
            if trans['type'] == 'expense':
                category_totals[trans['category']] += trans['amount']

        if category_totals:
            labels = list(category_totals.keys())
            sizes = list(category_totals.values())
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            ax.set_title('Expense Distribution by Category')

    def _create_trends_chart(self, ax):
        # Get last 6 months of data
        months = []
        incomes = []
        expenses = []

        for i in range(5, -1, -1):
            date = datetime.now() - timedelta(days=i*30)
            month_key = date.strftime("%Y-%m")
            months.append(calendar.month_abbr[date.month])
            
            month_transactions = self.transactions[month_key]
            month_income = sum(t['amount'] for t in month_transactions 
                             if t['type'] == 'income')
            month_expenses = sum(t['amount'] for t in month_transactions 
                               if t['type'] == 'expense')
            
            incomes.append(month_income)
            expenses.append(month_expenses)

        x = np.arange(len(months))
        width = 0.35

        ax.bar(x - width/2, incomes, width, label='Income')
        ax.bar(x + width/2, expenses, width, label='Expenses')

        ax.set_ylabel('Amount ($)')
        ax.set_title('Income vs Expenses Trend')
        ax.set_xticks(x)
        ax.set_xticklabels(months)
        ax.legend()

if __name__ == "__main__":
    # This allows testing the analysis features independently
    analysis = BudgetAnalysis()
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    analysis.show_monthly_summary(root)
    root.mainloop() 