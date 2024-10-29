import unittest
from datetime import datetime
from budget_tracker import BudgetTracker
from budget_analysis import BudgetAnalysis
import tkinter as tk
import os
import json

class TestBudgetTracker(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = BudgetTracker(self.root)
        
    def tearDown(self):
        self.root.destroy()
        # Clean up test data file if it exists
        if os.path.exists('budget_data.json'):
            os.remove('budget_data.json')
            
    def test_new_transaction(self):
        # Test adding a new transaction
        current_month = datetime.now().strftime("%Y-%m")
        transaction = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'type': 'expense',
            'category': 'Food',
            'amount': 50.0,
            'description': 'Test transaction'
        }
        
        self.app.transactions[current_month].append(transaction)
        self.app.save_transactions()
        
        # Verify transaction was saved
        with open('budget_data.json', 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(len(saved_data[current_month]), 1)
        self.assertEqual(saved_data[current_month][0]['amount'], 50.0)
        
    def test_budget_analysis(self):
        # Test analysis functionality
        analysis = BudgetAnalysis()
        self.assertIsNotNone(analysis)
        
if __name__ == '__main__':
    try:
        import matplotlib
        import numpy
        unittest.main()
    except ImportError as e:
        print("Error: Missing required dependencies.")
        print("Please install required packages using:")
        print("pip install -r requirements.txt")
        exit(1) 