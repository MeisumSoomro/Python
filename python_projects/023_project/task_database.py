import sqlite3
from datetime import datetime

class TaskDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                due_date TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                created_date TEXT NOT NULL
            )
        ''')
        self.conn.commit()
        
    def add_task(self, task):
        self.cursor.execute('''
            INSERT INTO tasks (title, category, priority, due_date, 
                             description, status, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            task['title'],
            task['category'],
            task['priority'],
            task['due_date'],
            task['description'],
            task['status'],
            task['created_date']
        ))
        self.conn.commit()
        
    def update_task(self, task):
        self.cursor.execute('''
            UPDATE tasks
            SET title = ?, category = ?, priority = ?, due_date = ?,
                description = ?, status = ?
            WHERE id = ?
        ''', (
            task['title'],
            task['category'],
            task['priority'],
            task['due_date'],
            task['description'],
            task['status'],
            task['id']
        ))
        self.conn.commit()
        
    def delete_task(self, task_id):
        self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        
    def get_task(self, task_id):
        self.cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = self.cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None
        
    def get_all_tasks(self):
        self.cursor.execute('SELECT * FROM tasks ORDER BY due_date')
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
        
    def get_filtered_tasks(self, category, priority):
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []
        
        if category != "All":
            query += ' AND category = ?'
            params.append(category)
            
        if priority != "All":
            query += ' AND priority = ?'
            params.append(priority)
            
        query += ' ORDER BY due_date'
        
        self.cursor.execute(query, params)
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
        
    def get_tasks_by_status(self, status):
        if status.lower() == "all":
            return self.get_all_tasks()
            
        self.cursor.execute(
            'SELECT * FROM tasks WHERE LOWER(status) = ? ORDER BY due_date',
            (status.lower(),)
        )
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
        
    def _row_to_dict(self, row):
        return {
            'id': row[0],
            'title': row[1],
            'category': row[2],
            'priority': row[3],
            'due_date': row[4],
            'description': row[5],
            'status': row[6],
            'created_date': row[7]
        }
        
    def close(self):
        self.conn.close() 