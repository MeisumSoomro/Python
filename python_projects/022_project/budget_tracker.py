import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from collections import defaultdict
from budget_analysis import BudgetAnalysis

class BudgetTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker")
        
        # Initialize variables
        self.transactions = defaultdict(list)
        self.categories = ["Salary", "Food", "Transportation", "Utilities", 
                         "Entertainment", "Shopping", "Healthcare", "Other"]
        
        # Create GUI elements
        self.create_menu()
        self.create_main_layout()
        
        # Load existing transactions
        self.load_transactions()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Transaction", command=self.new_transaction)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Monthly Summary", command=self.show_monthly_summary)
        view_menu.add_command(label="Category Analysis", command=self.show_category_analysis)
        
    def create_main_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel with summary
        left_frame = ttk.LabelFrame(main_frame, text="Summary")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Summary labels
        self.balance_label = ttk.Label(left_frame, text="Current Balance: $0.00")
        self.balance_label.pack(pady=5)
        
        self.income_label = ttk.Label(left_frame, text="Total Income: $0.00")
        self.income_label.pack(pady=5)
        
        self.expense_label = ttk.Label(left_frame, text="Total Expenses: $0.00")
        self.expense_label.pack(pady=5)
        
        # Quick add transaction
        ttk.Button(left_frame, text="Add Transaction", 
                  command=self.new_transaction).pack(fill=tk.X, pady=5)
        
        # Right panel with transactions
        right_frame = ttk.LabelFrame(main_frame, text="Recent Transactions")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Transactions treeview
        columns = ('Date', 'Type', 'Category', 'Amount', 'Description')
        self.trans_tree = ttk.Treeview(right_frame, columns=columns, show='headings')
        for col in columns:
            self.trans_tree.heading(col, text=col)
            self.trans_tree.column(col, width=100)
        
        self.trans_tree.pack(fill=tk.BOTH, expand=True)
        self.trans_tree.bind('<Double-1>', self.edit_transaction)
        
        # Scrollbar for transactions
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, 
                                command=self.trans_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.trans_tree.configure(yscrollcommand=scrollbar.set)
        
    def new_transaction(self):
        trans_window = tk.Toplevel(self.root)
        trans_window.title("New Transaction")
        trans_window.geometry("400x350")
        
        # Transaction details
        ttk.Label(trans_window, text="Type:").pack(padx=5, pady=2)
        type_var = tk.StringVar(value="expense")
        ttk.Radiobutton(trans_window, text="Expense", variable=type_var, 
                       value="expense").pack()
        ttk.Radiobutton(trans_window, text="Income", variable=type_var, 
                       value="income").pack()
        
        ttk.Label(trans_window, text="Category:").pack(padx=5, pady=2)
        category_combo = ttk.Combobox(trans_window, values=self.categories)
        category_combo.pack(fill=tk.X, padx=5)
        
        ttk.Label(trans_window, text="Amount:").pack(padx=5, pady=2)
        amount_entry = ttk.Entry(trans_window)
        amount_entry.pack(fill=tk.X, padx=5)
        
        ttk.Label(trans_window, text="Description:").pack(padx=5, pady=2)
        desc_text = tk.Text(trans_window, height=4)
        desc_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        def save_transaction():
            try:
                amount = float(amount_entry.get().strip())
                category = category_combo.get().strip()
                desc = desc_text.get(1.0, tk.END).strip()
                trans_type = type_var.get()
                
                if not all([amount, category]):
                    messagebox.showwarning("Warning", "Please fill in all required fields")
                    return
                
                transaction = {
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'type': trans_type,
                    'category': category,
                    'amount': amount,
                    'description': desc
                }
                
                current_month = datetime.now().strftime("%Y-%m")
                self.transactions[current_month].append(transaction)
                self.save_transactions()
                self.update_transactions_list()
                self.update_summary()
                trans_window.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
        
        ttk.Button(trans_window, text="Save", command=save_transaction).pack(pady=10)
    
    def edit_transaction(self, event=None):
        selection = self.trans_tree.selection()
        if not selection:
            return
            
        item = self.trans_tree.item(selection[0])
        values = item['values']
        
        # Find transaction in list
        current_month = datetime.now().strftime("%Y-%m")
        trans_list = self.transactions[current_month]
        trans_index = next((i for i, t in enumerate(trans_list) 
                          if t['date'] == values[0] and 
                          t['amount'] == float(values[3].replace('$', ''))), None)
        
        if trans_index is None:
            return
            
        trans_window = tk.Toplevel(self.root)
        trans_window.title("Edit Transaction")
        trans_window.geometry("400x350")
        
        # Pre-fill form with existing data
        ttk.Label(trans_window, text="Type:").pack(padx=5, pady=2)
        type_var = tk.StringVar(value=values[1])
        ttk.Radiobutton(trans_window, text="Expense", variable=type_var, 
                       value="expense").pack()
        ttk.Radiobutton(trans_window, text="Income", variable=type_var, 
                       value="income").pack()
        
        ttk.Label(trans_window, text="Category:").pack(padx=5, pady=2)
        category_combo = ttk.Combobox(trans_window, values=self.categories)
        category_combo.set(values[2])
        category_combo.pack(fill=tk.X, padx=5)
        
        ttk.Label(trans_window, text="Amount:").pack(padx=5, pady=2)
        amount_entry = ttk.Entry(trans_window)
        amount_entry.insert(0, values[3].replace('$', ''))
        amount_entry.pack(fill=tk.X, padx=5)
        
        ttk.Label(trans_window, text="Description:").pack(padx=5, pady=2)
        desc_text = tk.Text(trans_window, height=4)
        desc_text.insert(1.0, values[4])
        desc_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        def update_transaction():
            try:
                amount = float(amount_entry.get().strip())
                category = category_combo.get().strip()
                desc = desc_text.get(1.0, tk.END).strip()
                trans_type = type_var.get()
                
                if not all([amount, category]):
                    messagebox.showwarning("Warning", "Please fill in all required fields")
                    return
                
                trans_list[trans_index].update({
                    'type': trans_type,
                    'category': category,
                    'amount': amount,
                    'description': desc
                })
                
                self.save_transactions()
                self.update_transactions_list()
                self.update_summary()
                trans_window.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
        
        def delete_transaction():
            if messagebox.askyesno("Confirm Delete", 
                                 "Are you sure you want to delete this transaction?"):
                trans_list.pop(trans_index)
                self.save_transactions()
                self.update_transactions_list()
                self.update_summary()
                trans_window.destroy()
        
        button_frame = ttk.Frame(trans_window)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Update", 
                  command=update_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", 
                  command=delete_transaction).pack(side=tk.LEFT, padx=5)
    
    def update_transactions_list(self):
        self.trans_tree.delete(*self.trans_tree.get_children())
        current_month = datetime.now().strftime("%Y-%m")
        
        for trans in reversed(self.transactions[current_month]):
            self.trans_tree.insert('', 'end', values=(
                trans['date'],
                trans['type'],
                trans['category'],
                f"${trans['amount']:.2f}",
                trans['description']
            ))
    
    def update_summary(self):
        current_month = datetime.now().strftime("%Y-%m")
        transactions = self.transactions[current_month]
        
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        current_balance = total_income - total_expenses
        
        self.balance_label.config(text=f"Current Balance: ${current_balance:.2f}")
        self.income_label.config(text=f"Total Income: ${total_income:.2f}")
        self.expense_label.config(text=f"Total Expenses: ${total_expenses:.2f}")
    
    def show_monthly_summary(self):
        analysis = BudgetAnalysis(self.transactions)
        analysis.show_monthly_summary(self.root)
    
    def show_category_analysis(self):
        analysis = BudgetAnalysis(self.transactions)
        analysis.show_category_analysis(self.root)
    
    def export_data(self):
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(dict(self.transactions), f)
                messagebox.showinfo("Success", "Data exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export data: {str(e)}")
    
    def save_transactions(self):
        try:
            with open('budget_data.json', 'w') as f:
                json.dump(dict(self.transactions), f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save data: {str(e)}")
    
    def load_transactions(self):
        try:
            if os.path.exists('budget_data.json'):
                with open('budget_data.json', 'r') as f:
                    self.transactions = defaultdict(list, json.load(f))
                self.update_transactions_list()
                self.update_summary()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load data: {str(e)}")
    
    def on_closing(self):
        self.save_transactions()
        self.root.destroy()

def main():
    root = tk.Tk()
    root.geometry("800x600")
    app = BudgetTracker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 