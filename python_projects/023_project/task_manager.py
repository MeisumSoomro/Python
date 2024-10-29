import PySimpleGUI as sg
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os

class TaskDatabase:
    def __init__(self):
        self.db_file = "tasks.db"
        self._create_database()

    def _create_database(self):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    priority TEXT,
                    category TEXT,
                    status TEXT DEFAULT 'Pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def add_task(self, title: str, description: str, due_date: str, 
                 priority: str, category: str) -> bool:
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tasks (title, description, due_date, priority, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (title, description, due_date, priority, category))
                conn.commit()
                return True
        except:
            return False

    def get_tasks(self, filter_by: Optional[Dict] = None) -> List[tuple]:
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM tasks"
                
                if filter_by:
                    conditions = []
                    values = []
                    for key, value in filter_by.items():
                        if value:
                            conditions.append(f"{key} = ?")
                            values.append(value)
                    
                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)
                    
                    cursor.execute(query, values)
                else:
                    cursor.execute(query)
                
                return cursor.fetchall()
        except:
            return []

    def update_task(self, task_id: int, **kwargs) -> bool:
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                updates = []
                values = []
                
                for key, value in kwargs.items():
                    if value is not None:
                        updates.append(f"{key} = ?")
                        values.append(value)
                
                values.append(task_id)
                query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
                
                cursor.execute(query, values)
                conn.commit()
                return True
        except:
            return False

    def delete_task(self, task_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                return True
        except:
            return False

def create_layout():
    priorities = ['High', 'Medium', 'Low']
    categories = ['Work', 'Personal', 'Shopping', 'Study', 'Other']
    
    return [
        [sg.Text("Task Management System", font=("Helvetica", 16))],
        [sg.Frame("Add Task", [
            [sg.Text("Title:"), sg.Input(key="-TITLE-", size=(30, 1))],
            [sg.Text("Description:"), sg.Multiline(key="-DESC-", size=(30, 3))],
            [sg.Text("Due Date:"), sg.Input(key="-DUE-", size=(15, 1)), 
             sg.CalendarButton("Select", target="-DUE-", format="%Y-%m-%d")],
            [sg.Text("Priority:"), sg.Combo(priorities, key="-PRIORITY-", default_value="Medium")],
            [sg.Text("Category:"), sg.Combo(categories, key="-CATEGORY-", default_value="Other")],
            [sg.Button("Add Task"), sg.Button("Clear")]
        ])],
        [sg.Frame("Tasks", [
            [sg.Table(
                values=[],
                headings=["ID", "Title", "Due Date", "Priority", "Category", "Status"],
                auto_size_columns=True,
                justification='left',
                key="-TABLE-",
                enable_events=True
            )]
        ])],
        [sg.Button("Refresh"), sg.Button("Edit"), sg.Button("Delete"), sg.Button("Exit")]
    ]

def main():
    db = TaskDatabase()
    window = sg.Window("Task Manager", create_layout(), resizable=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Exit":
            break

        if event == "Add Task":
            if values["-TITLE-"]:
                success = db.add_task(
                    values["-TITLE-"],
                    values["-DESC-"],
                    values["-DUE-"],
                    values["-PRIORITY-"],
                    values["-CATEGORY-"]
                )
                if success:
                    sg.popup("Task added successfully!")
                    # Clear inputs
                    for key in ["-TITLE-", "-DESC-", "-DUE-"]:
                        window[key].update("")
                else:
                    sg.popup("Error adding task!")

        if event == "Refresh" or event == "Add Task":
            tasks = db.get_tasks()
            window["-TABLE-"].update([
                [t[0], t[1], t[3], t[4], t[5], t[6]] for t in tasks
            ])

        if event == "Delete":
            selected_rows = values["-TABLE-"]
            if selected_rows:
                task_id = window["-TABLE-"].get()[selected_rows[0]][0]
                if sg.popup_yes_no("Are you sure you want to delete this task?") == "Yes":
                    if db.delete_task(task_id):
                        sg.popup("Task deleted!")
                        window.write_event_value("Refresh", None)

    window.close()

if __name__ == "__main__":
    main() 