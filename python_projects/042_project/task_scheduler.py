import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import json
from pathlib import Path
import subprocess
import threading
import logging
from enum import Enum
import sys
import signal

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class TaskFrequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class Task:
    def __init__(self, name: str, command: str, priority: TaskPriority = TaskPriority.MEDIUM):
        self.name = name
        self.command = command
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.frequency = TaskFrequency.ONCE
        self.custom_schedule = ""
        self.dependencies: Set[str] = set()  # Task names this task depends on
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.created_at = datetime.now()
        self.error_message = ""
        self.retry_count = 0
        self.max_retries = 3

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "command": self.command,
            "priority": self.priority.value,
            "status": self.status.value,
            "frequency": self.frequency.value,
            "custom_schedule": self.custom_schedule,
            "dependencies": list(self.dependencies),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "created_at": self.created_at.isoformat(),
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        task = cls(data["name"], data["command"], TaskPriority(data["priority"]))
        task.status = TaskStatus(data["status"])
        task.frequency = TaskFrequency(data["frequency"])
        task.custom_schedule = data["custom_schedule"]
        task.dependencies = set(data["dependencies"])
        task.last_run = datetime.fromisoformat(data["last_run"]) if data["last_run"] else None
        task.next_run = datetime.fromisoformat(data["next_run"]) if data["next_run"] else None
        task.created_at = datetime.fromisoformat(data["created_at"])
        task.error_message = data["error_message"]
        task.retry_count = data["retry_count"]
        task.max_retries = data["max_retries"]
        return task

class TaskScheduler:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: Set[str] = set()
        self.file_path = Path("tasks.json")
        self.log_file = Path("scheduler.log")
        self.setup_logging()
        self.load_tasks()
        self.running = True
        signal.signal(signal.SIGINT, self.handle_shutdown)

    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def handle_shutdown(self, signum, frame):
        self.running = False
        logging.info("Shutting down scheduler...")
        self.save_tasks()
        sys.exit(0)

    def add_task(self, name: str, command: str, priority: TaskPriority = TaskPriority.MEDIUM) -> bool:
        if name in self.tasks:
            logging.error(f"Task {name} already exists")
            return False

        task = Task(name, command, priority)
        self.tasks[name] = task
        self.save_tasks()
        logging.info(f"Added task: {name}")
        return True

    def set_task_schedule(self, name: str, frequency: TaskFrequency, custom_schedule: str = "") -> bool:
        if name not in self.tasks:
            logging.error(f"Task {name} not found")
            return False

        task = self.tasks[name]
        task.frequency = frequency
        task.custom_schedule = custom_schedule
        self.calculate_next_run(task)
        self.save_tasks()
        logging.info(f"Updated schedule for task: {name}")
        return True

    def add_dependency(self, task_name: str, dependency_name: str) -> bool:
        if task_name not in self.tasks or dependency_name not in self.tasks:
            logging.error(f"Task or dependency not found")
            return False

        if task_name == dependency_name:
            logging.error(f"Task cannot depend on itself")
            return False

        # Check for circular dependencies
        if self.would_create_cycle(task_name, dependency_name):
            logging.error(f"Adding dependency would create a cycle")
            return False

        self.tasks[task_name].dependencies.add(dependency_name)
        self.save_tasks()
        logging.info(f"Added dependency {dependency_name} to task {task_name}")
        return True

    def would_create_cycle(self, task_name: str, new_dependency: str) -> bool:
        visited = set()
        
        def has_cycle(current: str) -> bool:
            if current in visited:
                return True
            if current not in self.tasks:
                return False
            
            visited.add(current)
            deps = self.tasks[current].dependencies
            if new_dependency == task_name and current == new_dependency:
                deps = deps | {task_name}
            
            for dep in deps:
                if has_cycle(dep):
                    return True
            visited.remove(current)
            return False
        
        return has_cycle(task_name)

    def calculate_next_run(self, task: Task):
        now = datetime.now()
        if task.frequency == TaskFrequency.ONCE:
            if not task.next_run:
                task.next_run = now + timedelta(minutes=1)
        elif task.frequency == TaskFrequency.DAILY:
            if not task.next_run or task.next_run < now:
                task.next_run = now + timedelta(days=1)
        elif task.frequency == TaskFrequency.WEEKLY:
            if not task.next_run or task.next_run < now:
                task.next_run = now + timedelta(weeks=1)
        elif task.frequency == TaskFrequency.MONTHLY:
            if not task.next_run or task.next_run < now:
                task.next_run = now + timedelta(days=30)
        elif task.frequency == TaskFrequency.CUSTOM:
            # Custom schedule should be in cron-like format
            # Not implemented in this basic version
            pass

    def execute_task(self, task: Task):
        if task.name in self.running_tasks:
            return

        # Check dependencies
        for dep in task.dependencies:
            if dep not in self.tasks:
                continue
            if self.tasks[dep].status != TaskStatus.COMPLETED:
                task.status = TaskStatus.BLOCKED
                return

        self.running_tasks.add(task.name)
        task.status = TaskStatus.RUNNING
        task.last_run = datetime.now()

        try:
            process = subprocess.run(
                task.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if process.returncode == 0:
                task.status = TaskStatus.COMPLETED
                task.error_message = ""
                task.retry_count = 0
                logging.info(f"Task {task.name} completed successfully")
            else:
                task.status = TaskStatus.FAILED
                task.error_message = process.stderr
                task.retry_count += 1
                logging.error(f"Task {task.name} failed: {task.error_message}")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.retry_count += 1
            logging.error(f"Error executing task {task.name}: {e}")

        finally:
            self.running_tasks.remove(task.name)
            self.calculate_next_run(task)
            self.save_tasks()

    def run_scheduler(self):
        while self.running:
            now = datetime.now()
            
            # Sort tasks by priority
            pending_tasks = sorted(
                [task for task in self.tasks.values() if task.next_run and task.next_run <= now],
                key=lambda x: x.priority.value,
                reverse=True
            )

            for task in pending_tasks:
                if task.retry_count >= task.max_retries:
                    continue
                
                thread = threading.Thread(target=self.execute_task, args=(task,))
                thread.start()

            time.sleep(1)

    def save_tasks(self):
        data = {name: task.to_dict() for name, task in self.tasks.items()}
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def load_tasks(self):
        if not self.file_path.exists():
            return

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.tasks = {name: Task.from_dict(task_data) 
                            for name, task_data in data.items()}
        except json.JSONDecodeError:
            logging.error("Error loading tasks file")

def main():
    scheduler = TaskScheduler()
    
    while True:
        print("\nTask Scheduler Menu:")
        print("1. Add Task")
        print("2. Set Task Schedule")
        print("3. Add Task Dependency")
        print("4. List Tasks")
        print("5. View Task Details")
        print("6. Start Scheduler")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == "1":
            name = input("Enter task name: ")
            command = input("Enter command to execute: ")
            print("\nPriority levels:")
            print("1. Low")
            print("2. Medium")
            print("3. High")
            priority = int(input("Choose priority (1-3): "))
            priority = TaskPriority(priority)
            
            if scheduler.add_task(name, command, priority):
                print("Task added successfully!")
            else:
                print("Failed to add task!")
        
        elif choice == "2":
            name = input("Enter task name: ")
            print("\nFrequency options:")
            print("1. Once")
            print("2. Daily")
            print("3. Weekly")
            print("4. Monthly")
            print("5. Custom")
            
            freq_choice = int(input("Choose frequency (1-5): "))
            frequency = TaskFrequency(list(TaskFrequency)[freq_choice-1].value)
            
            custom_schedule = ""
            if frequency == TaskFrequency.CUSTOM:
                custom_schedule = input("Enter custom schedule: ")
            
            if scheduler.set_task_schedule(name, frequency, custom_schedule):
                print("Schedule set successfully!")
            else:
                print("Failed to set schedule!")
        
        elif choice == "3":
            task_name = input("Enter task name: ")
            dependency = input("Enter dependency task name: ")
            
            if scheduler.add_dependency(task_name, dependency):
                print("Dependency added successfully!")
            else:
                print("Failed to add dependency!")
        
        elif choice == "4":
            if not scheduler.tasks:
                print("No tasks found!")
                continue
                
            print("\nTasks:")
            print("-" * 60)
            for name, task in scheduler.tasks.items():
                print(f"Name: {name}")
                print(f"Status: {task.status.value}")
                print(f"Priority: {task.priority.name}")
                print(f"Next run: {task.next_run}")
                print("-" * 30)
        
        elif choice == "5":
            name = input("Enter task name: ")
            if name in scheduler.tasks:
                task = scheduler.tasks[name]
                print(f"\nTask Details for {name}:")
                print(f"Command: {task.command}")
                print(f"Status: {task.status.value}")
                print(f"Priority: {task.priority.name}")
                print(f"Frequency: {task.frequency.value}")
                print(f"Dependencies: {', '.join(task.dependencies) if task.dependencies else 'None'}")
                print(f"Last run: {task.last_run}")
                print(f"Next run: {task.next_run}")
                print(f"Created: {task.created_at}")
                if task.error_message:
                    print(f"Last error: {task.error_message}")
            else:
                print("Task not found!")
        
        elif choice == "6":
            print("Starting scheduler... (Press Ctrl+C to stop)")
            try:
                scheduler.run_scheduler()
            except KeyboardInterrupt:
                print("\nStopping scheduler...")
        
        elif choice == "7":
            print("Thank you for using Task Scheduler!")
            scheduler.save_tasks()
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 