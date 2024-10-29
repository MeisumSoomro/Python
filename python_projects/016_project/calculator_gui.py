import tkinter as tk
from tkinter import messagebox

class CalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        
        # Entry field for display
        self.display = tk.Entry(root, font=('Arial', 20), justify='right')
        self.display.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky='nsew')
        
        # Calculator buttons
        self.create_buttons()
        
        # Configure grid
        for i in range(5):
            root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            root.grid_columnconfigure(i, weight=1)
            
        # Initialize variables
        self.current_number = ''
        self.first_number = None
        self.operation = None
        self.should_clear = False
        
    def create_buttons(self):
        # Button layout
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]
        
        # Create and place buttons
        row = 1
        col = 0
        for button in buttons:
            cmd = lambda x=button: self.button_click(x)
            btn = tk.Button(self.root, text=button, font=('Arial', 15),
                          command=cmd)
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
            col += 1
            if col > 3:
                col = 0
                row += 1
                
        # Additional buttons
        tk.Button(self.root, text='C', font=('Arial', 15),
                 command=self.clear).grid(row=row, column=0, columnspan=2,
                                        padx=2, pady=2, sticky='nsew')
        tk.Button(self.root, text='←', font=('Arial', 15),
                 command=self.backspace).grid(row=row, column=2, columnspan=2,
                                            padx=2, pady=2, sticky='nsew')
        
    def button_click(self, char):
        if char.isdigit() or char == '.':
            if self.should_clear:
                self.display.delete(0, tk.END)
                self.should_clear = False
            self.display.insert(tk.END, char)
            
        elif char in ['+', '-', '*', '/']:
            try:
                self.first_number = float(self.display.get())
                self.operation = char
                self.should_clear = True
            except ValueError:
                messagebox.showerror("Error", "Invalid number")
                
        elif char == '=':
            try:
                second_number = float(self.display.get())
                if self.operation and self.first_number is not None:
                    result = self.calculate(self.first_number,
                                         second_number,
                                         self.operation)
                    self.display.delete(0, tk.END)
                    self.display.insert(0, str(result))
                    self.first_number = None
                    self.operation = None
                    self.should_clear = True
            except ValueError:
                messagebox.showerror("Error", "Invalid number")
            except ZeroDivisionError:
                messagebox.showerror("Error", "Cannot divide by zero")
                
    def calculate(self, n1, n2, op):
        if op == '+':
            return n1 + n2
        elif op == '-':
            return n1 - n2
        elif op == '*':
            return n1 * n2
        elif op == '/':
            if n2 == 0:
                raise ZeroDivisionError
            return n1 / n2
            
    def clear(self):
        self.display.delete(0, tk.END)
        self.first_number = None
        self.operation = None
        self.should_clear = False
        
    def backspace(self):
        current = self.display.get()
        self.display.delete(len(current)-1, tk.END)

def main():
    root = tk.Tk()
    root.geometry("300x400")
    app = CalculatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 