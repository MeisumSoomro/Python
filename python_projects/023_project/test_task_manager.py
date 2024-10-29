import unittest
import os
from datetime import datetime
import tkinter as tk
from task_manager import TaskManager
from task_database import TaskDatabase

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = TaskManager(self.root)
        
    def tearDown(self):
        self.root.destroy()
        # Clean up test database
        if os.path.exists('tasks.db'):
            os.remove('tasks.db')
            
    def test_new_task(self):
        # Test adding a new task
        task = {
            'title': 'Test Task',
            'category': 'Work',
            'priority': 'High',
            'due_date': datetime.now().strftime("%Y-%m-%d"),
            'description': 'Test description',
            'status': 'Active',
            'created_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        self.app.db.add_task(task)
        tasks = self.app.db.get_all_tasks()
        
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['title'], 'Test Task')
        self.assertEqual(tasks[0]['priority'], 'High')
        
    def test_task_filters(self):
        # Test task filtering
        tasks = [
            {
                'title': 'Work Task',
                'category': 'Work',
                'priority': 'High',
                'due_date': datetime.now().strftime("%Y-%m-%d"),
                'description': 'Test description',
                'status': 'Active',
                'created_date': datetime.now().strftime("%Y-%m-%d")
            },
            {
                'title': 'Home Task',
                'category': 'Home',
                'priority': 'Low',
                'due_date': datetime.now().strftime("%Y-%m-%d"),
                'description': 'Test description',
                'status': 'Completed',
                'created_date': datetime.now().strftime("%Y-%m-%d")
            }
        ]
        
        for task in tasks:
            self.app.db.add_task(task)
            
        # Test category filter
        work_tasks = self.app.db.get_filtered_tasks('Work', 'All')
        self.assertEqual(len(work_tasks), 1)
        self.assertEqual(work_tasks[0]['title'], 'Work Task')
        
        # Test status filter
        completed_tasks = self.app.db.get_tasks_by_status('completed')
        self.assertEqual(len(completed_tasks), 1)
        self.assertEqual(completed_tasks[0]['title'], 'Home Task')
        
if __name__ == '__main__':
    unittest.main() 