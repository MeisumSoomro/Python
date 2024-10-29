import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from password_crypto import PasswordCrypto
from password_generator import PasswordGenerator

class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        
        # Initialize crypto and generator
        self.crypto = PasswordCrypto()
        self.generator = PasswordGenerator()
        
        # Password categories
        self.categories = ["Email", "Social Media", "Banking", "Shopping", 
                         "Work", "Entertainment", "Other"]
        
        # Store for decrypted passwords (temporary, in-memory only)
        self.password_store = {}
        
        # Create GUI elements
        self.create_menu()
        self.create_main_layout()
        
        # Check master password
        self.check_master_password()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Password", command=self.new_password)
        file_menu.add_command(label="Export Passwords", command=self.export_passwords)
        file_menu.add_separator()
        file_menu.add_command(label="Change Master Password", 
                            command=self.change_master_password)
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Password Generator", 
                             command=self.show_password_generator)
        tools_menu.add_command(label="Password Strength Checker", 
                             command=self.check_password_strength)
        
    def create_main_layout(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel with filters and quick add
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Quick add password
        ttk.Button(left_frame, text="Add Password", 
                  command=self.new_password).pack(fill=tk.X, pady=5)
        
        # Category filter
        filter_frame = ttk.LabelFrame(left_frame, text="Filter")
        filter_frame.pack(fill=tk.X, pady=5)
        
        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(filter_frame, 
                                    values=["All"] + self.categories,
                                    textvariable=self.category_var)
        category_combo.pack(fill=tk.X, padx=5, pady=5)
        category_combo.bind('<<ComboboxSelected>>', self.filter_passwords)
        
        # Search
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_passwords())
        ttk.Entry(search_frame, textvariable=self.search_var).pack(fill=tk.X)
        
        # Right panel with passwords
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Passwords treeview
        columns = ('Title', 'Username', 'Category', 'Last Modified')
        self.password_tree = ttk.Treeview(right_frame, columns=columns, 
                                        show='headings')
        
        for col in columns:
            self.password_tree.heading(col, text=col)
            self.password_tree.column(col, width=100)
        
        self.password_tree.pack(fill=tk.BOTH, expand=True)
        self.password_tree.bind('<Double-1>', self.view_password)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, 
                                command=self.password_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.password_tree.configure(yscrollcommand=scrollbar.set)
        
    def check_master_password(self):
        if not os.path.exists('master_password.hash'):
            self.set_master_password()
        else:
            self.verify_master_password()
            
    def set_master_password(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Master Password")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        
        ttk.Label(dialog, text="Enter Master Password:").pack(pady=5)
        pass1 = ttk.Entry(dialog, show="*")
        pass1.pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="Confirm Master Password:").pack(pady=5)
        pass2 = ttk.Entry(dialog, show="*")
        pass2.pack(fill=tk.X, padx=5)
        
        def save_master():
            if pass1.get() == pass2.get():
                if len(pass1.get()) < 8:
                    messagebox.showwarning(
                        "Warning", 
                        "Master password should be at least 8 characters long"
                    )
                    return
                self.crypto.set_master_password(pass1.get())
                dialog.destroy()
                self.load_passwords()
            else:
                messagebox.showerror("Error", "Passwords do not match")
                
        ttk.Button(dialog, text="Save", command=save_master).pack(pady=10)
        
        dialog.grab_set()
        
    def verify_master_password(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter Master Password")
        dialog.geometry("300x120")
        dialog.transient(self.root)
        
        ttk.Label(dialog, text="Enter Master Password:").pack(pady=5)
        password = ttk.Entry(dialog, show="*")
        password.pack(fill=tk.X, padx=5)
        
        def verify():
            if self.crypto.verify_master_password(password.get()):
                dialog.destroy()
                self.load_passwords()
            else:
                messagebox.showerror("Error", "Incorrect password")
                
        ttk.Button(dialog, text="Unlock", command=verify).pack(pady=10)
        
        dialog.grab_set()
        
    def new_password(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("New Password")
        dialog.geometry("400x400")
        
        # Entry details
        ttk.Label(dialog, text="Title:").pack(padx=5, pady=2)
        title_entry = ttk.Entry(dialog)
        title_entry.pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="Username:").pack(padx=5, pady=2)
        username_entry = ttk.Entry(dialog)
        username_entry.pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="Password:").pack(padx=5, pady=2)
        password_frame = ttk.Frame(dialog)
        password_frame.pack(fill=tk.X, padx=5)
        
        password_entry = ttk.Entry(password_frame, show="*")
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def generate():
            password = self.generator.generate_password()
            password_entry.delete(0, tk.END)
            password_entry.insert(0, password)
            
        ttk.Button(password_frame, text="Generate", 
                  command=generate).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(dialog, text="Category:").pack(padx=5, pady=2)
        category_combo = ttk.Combobox(dialog, values=self.categories)
        category_combo.pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="Notes:").pack(padx=5, pady=2)
        notes_text = tk.Text(dialog, height=4)
        notes_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        def save():
            title = title_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            category = category_combo.get().strip()
            notes = notes_text.get(1.0, tk.END).strip()
            
            if not all([title, username, password, category]):
                messagebox.showwarning("Warning", "Please fill in all required fields")
                return
                
            entry = {
                'title': title,
                'username': username,
                'password': self.crypto.encrypt(password),
                'category': category,
                'notes': notes,
                'modified': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
            self.password_store[title] = entry
            self.save_passwords()
            self.update_password_list()
            dialog.destroy()
            
        ttk.Button(dialog, text="Save", command=save).pack(pady=10)
        
    def view_password(self, event=None):
        selection = self.password_tree.selection()
        if not selection:
            return
            
        item = self.password_tree.item(selection[0])
        title = item['values'][0]
        entry = self.password_store.get(title)
        
        if not entry:
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("View Password")
        dialog.geometry("400x400")
        
        # Show details
        ttk.Label(dialog, text="Title:").pack(padx=5, pady=2)
        title_var = tk.StringVar(value=entry['title'])
        ttk.Entry(dialog, textvariable=title_var, state='readonly').pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="Username:").pack(padx=5, pady=2)
        username_var = tk.StringVar(value=entry['username'])
        username_frame = ttk.Frame(dialog)
        username_frame.pack(fill=tk.X, padx=5)
        ttk.Entry(username_frame, textvariable=username_var, 
                 state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(username_frame, text="Copy", 
                  command=lambda: self.copy_to_clipboard(entry['username'])
                  ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(dialog, text="Password:").pack(padx=5, pady=2)
        password_frame = ttk.Frame(dialog)
        password_frame.pack(fill=tk.X, padx=5)
        password_var = tk.StringVar(value="********")
        password_entry = ttk.Entry(password_frame, textvariable=password_var, 
                                 state='readonly')
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def toggle_password():
            if password_var.get() == "********":
                password_var.set(self.crypto.decrypt(entry['password']))
            else:
                password_var.set("********")
                
        ttk.Button(password_frame, text="Show/Hide", 
                  command=toggle_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(password_frame, text="Copy", 
                  command=lambda: self.copy_to_clipboard(
                      self.crypto.decrypt(entry['password']))
                  ).pack(side=tk.LEFT)
        
        ttk.Label(dialog, text="Category:").pack(padx=5, pady=2)
        category_var = tk.StringVar(value=entry['category'])
        ttk.Entry(dialog, textvariable=category_var, 
                 state='readonly').pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="Notes:").pack(padx=5, pady=2)
        notes_text = tk.Text(dialog, height=4)
        notes_text.insert(1.0, entry['notes'])
        notes_text.config(state='disabled')
        notes_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        def edit():
            dialog.destroy()
            self.edit_password(entry)
            
        def delete():
            if messagebox.askyesno("Confirm Delete", 
                                 "Are you sure you want to delete this password?"):
                del self.password_store[title]
                self.save_passwords()
                self.update_password_list()
                dialog.destroy()
                
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Edit", 
                  command=edit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", 
                  command=delete).pack(side=tk.LEFT, padx=5)
        
    def edit_password(self, entry):
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Password")
        dialog.geometry("400x400")
        
        # Pre-fill form with existing data
        ttk.Label(dialog, text="Title:").pack(padx=5, pady=2)
        title_entry = ttk.Entry(dialog)
        title_entry.insert(0, entry['title'])
        title_entry.pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="Username:").pack(padx=5, pady=2)
        username_entry = ttk.Entry(dialog)
        username_entry.insert(0, entry['username'])
        username_entry.pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="Password:").pack(padx=5, pady=2)
        password_frame = ttk.Frame(dialog)
        password_frame.pack(fill=tk.X, padx=5)
        
        password_entry = ttk.Entry(password_frame, show="*")
        password_entry.insert(0, self.crypto.decrypt(entry['password']))
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def generate():
            password = self.generator.generate_password()
            password_entry.delete(0, tk.END)
            password_entry.insert(0, password)
            
        ttk.Button(password_frame, text="Generate", 
                  command=generate).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(dialog, text="Category:").pack(padx=5, pady=2)
        category_combo = ttk.Combobox(dialog, values=self.categories)
        category_combo.set(entry['category'])
        category_combo.pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="Notes:").pack(padx=5, pady=2)
        notes_text = tk.Text(dialog, height=4)
        notes_text.insert(1.0, entry['notes'])
        notes_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        def update():
            old_title = entry['title']
            title = title_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            category = category_combo.get().strip()
            notes = notes_text.get(1.0, tk.END).strip()
            
            if not all([title, username, password, category]):
                messagebox.showwarning("Warning", "Please fill in all required fields")
                return
                
            # Delete old entry if title changed
            if old_title != title:
                del self.password_store[old_title]
                
            self.password_store[title] = {
                'title': title,
                'username': username,
                'password': self.crypto.encrypt(password),
                'category': category,
                'notes': notes,
                'modified': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
            self.save_passwords()
            self.update_password_list()
            dialog.destroy()
            
        ttk.Button(dialog, text="Update", command=update).pack(pady=10)
        
    def filter_passwords(self, event=None):
        category = self.category_var.get()
        search = self.search_var.get().lower()
        
        self.password_tree.delete(*self.password_tree.get_children())
        
        for entry in self.password_store.values():
            if (category == "All" or entry['category'] == category) and \
               (not search or search in entry['title'].lower() or \
                search in entry['username'].lower()):
                self.password_tree.insert('', 'end', values=(
                    entry['title'],
                    entry['username'],
                    entry['category'],
                    entry['modified']
                ))
                
    def update_password_list(self):
        self.password_tree.delete(*self.password_tree.get_children())
        
        for entry in self.password_store.values():
            self.password_tree.insert('', 'end', values=(
                entry['title'],
                entry['username'],
                entry['category'],
                entry['modified']
            ))
            
    def show_password_generator(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Password Generator")
        dialog.geometry("400x300")
        
        # Generator options
        options_frame = ttk.LabelFrame(dialog, text="Options")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        length_var = tk.IntVar(value=12)
        ttk.Label(options_frame, text="Length:").pack()
        ttk.Scale(options_frame, from_=8, to=32, variable=length_var, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        uppercase_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Uppercase letters", 
                       variable=uppercase_var).pack()
        
        numbers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Numbers", 
                       variable=numbers_var).pack()
        
        symbols_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Special characters", 
                       variable=symbols_var).pack()
        
        # Generated password
        result_frame = ttk.LabelFrame(dialog, text="Generated Password")
        result_frame.pack(fill=tk.X, padx=5, pady=5)
        
        password_var = tk.StringVar()
        password_entry = ttk.Entry(result_frame, textvariable=password_var, 
                                 state='readonly')
        password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        def generate():
            password = self.generator.generate_password(
                length=length_var.get(),
                uppercase=uppercase_var.get(),
                numbers=numbers_var.get(),
                symbols=symbols_var.get()
            )
            password_var.set(password)
            
        def copy():
            if password_var.get():
                self.copy_to_clipboard(password_var.get())
                
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Generate", 
                  command=generate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Copy", 
                  command=copy).pack(side=tk.LEFT, padx=5)
        
    def check_password_strength(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Password Strength Checker")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Enter password to check:").pack(pady=5)
        password_entry = ttk.Entry(dialog, show="*")
        password_entry.pack(fill=tk.X, padx=5)
        
        result_label = ttk.Label(dialog, text="")
        result_label.pack(pady=10)
        
        def check():
            password = password_entry.get()
            strength = self.generator.check_password_strength(password)
            result_label.config(
                text=f"Strength: {strength['score']}/5\n{strength['feedback']}"
            )
            
        ttk.Button(dialog, text="Check", command=check).pack()
        
    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        
    def change_master_password(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Master Password")
        dialog.geometry("300x200")
        
        ttk.Label(dialog, text="Current Password:").pack(pady=5)
        current_pass = ttk.Entry(dialog, show="*")
        current_pass.pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="New Password:").pack(pady=5)
        new_pass1 = ttk.Entry(dialog, show="*")
        new_pass1.pack(fill=tk.X, padx=5)
        
        ttk.Label(dialog, text="Confirm New Password:").pack(pady=5)
        new_pass2 = ttk.Entry(dialog, show="*")
        new_pass2.pack(fill=tk.X, padx=5)
        
        def change():
            if not self.crypto.verify_master_password(current_pass.get()):
                messagebox.showerror("Error", "Current password is incorrect")
                return
                
            if new_pass1.get() != new_pass2.get():
                messagebox.showerror("Error", "New passwords do not match")
                return
                
            if len(new_pass1.get()) < 8:
                messagebox.showwarning(
                    "Warning", 
                    "Master password should be at least 8 characters long"
                )
                return
                
            self.crypto.change_master_password(new_pass1.get())
            messagebox.showinfo("Success", "Master password changed successfully")
            dialog.destroy()
            
        ttk.Button(dialog, text="Change", command=change).pack(pady=10)
        
    def export_passwords(self):
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.password_store, f, indent=2)
                messagebox.showinfo("Success", "Passwords exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export passwords: {str(e)}")
                
    def save_passwords(self):
        try:
            with open('passwords.enc', 'w') as f:
                json.dump(self.password_store, f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save passwords: {str(e)}")
            
    def load_passwords(self):
        try:
            if os.path.exists('passwords.enc'):
                with open('passwords.enc', 'r') as f:
                    self.password_store = json.load(f)
                self.update_password_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load passwords: {str(e)}")
            
    def on_closing(self):
        self.save_passwords()
        self.root.destroy()

def main():
    root = tk.Tk()
    root.geometry("800x600")
    app = PasswordManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 