import shutil
import os
from pathlib import Path
from datetime import datetime
import json
import hashlib
from typing import Dict, List, Set, Optional
import logging
import schedule
import time
import threading
from queue import Queue
import zipfile

class BackupType:
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"

class BackupJob:
    def __init__(self, source: str, destination: str, name: str, backup_type: str = BackupType.FULL):
        self.source = Path(source)
        self.destination = Path(destination)
        self.name = name
        self.backup_type = backup_type
        self.schedule = ""
        self.compress = True
        self.exclude_patterns: List[str] = []
        self.last_backup: Optional[str] = None
        self.file_hashes: Dict[str, str] = {}

    def to_dict(self) -> dict:
        return {
            "source": str(self.source),
            "destination": str(self.destination),
            "name": self.name,
            "backup_type": self.backup_type,
            "schedule": self.schedule,
            "compress": self.compress,
            "exclude_patterns": self.exclude_patterns,
            "last_backup": self.last_backup,
            "file_hashes": self.file_hashes
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'BackupJob':
        job = cls(data["source"], data["destination"], data["name"], data["backup_type"])
        job.schedule = data["schedule"]
        job.compress = data["compress"]
        job.exclude_patterns = data["exclude_patterns"]
        job.last_backup = data["last_backup"]
        job.file_hashes = data["file_hashes"]
        return job

class BackupManager:
    def __init__(self):
        self.jobs: Dict[str, BackupJob] = {}
        self.config_file = Path("backup_config.json")
        self.log_file = Path("backup.log")
        self.setup_logging()
        self.load_config()
        self.running = True
        self.backup_queue = Queue()
        self.worker_thread = threading.Thread(target=self._process_backup_queue)
        self.worker_thread.start()

    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def load_config(self):
        """Load backup configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.jobs = {
                        name: BackupJob.from_dict(job_data)
                        for name, job_data in data.items()
                    }
            except json.JSONDecodeError:
                logging.error("Error loading config file")

    def save_config(self):
        """Save backup configuration to file"""
        data = {name: job.to_dict() for name, job in self.jobs.items()}
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=4)

    def add_job(self, source: str, destination: str, name: str,
                backup_type: str = BackupType.FULL) -> bool:
        """Add a new backup job"""
        if name in self.jobs:
            logging.error(f"Job {name} already exists")
            return False

        if not Path(source).exists():
            logging.error(f"Source path {source} does not exist")
            return False

        job = BackupJob(source, destination, name, backup_type)
        self.jobs[name] = job
        self.save_config()
        logging.info(f"Added backup job: {name}")
        return True

    def remove_job(self, name: str) -> bool:
        """Remove a backup job"""
        if name not in self.jobs:
            logging.error(f"Job {name} not found")
            return False

        del self.jobs[name]
        self.save_config()
        logging.info(f"Removed backup job: {name}")
        return True

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _should_backup_file(self, file_path: str, job: BackupJob) -> bool:
        """Check if file should be backed up based on exclusion patterns"""
        return not any(pattern in file_path for pattern in job.exclude_patterns)

    def _create_backup_name(self, job: BackupJob) -> str:
        """Create backup directory/file name with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{job.name}_{timestamp}"

    def _process_backup_queue(self):
        """Process backup jobs from the queue"""
        while self.running:
            try:
                job = self.backup_queue.get(timeout=1)
                self._execute_backup(job)
                self.backup_queue.task_done()
            except:
                continue

    def _execute_backup(self, job: BackupJob):
        """Execute a backup job"""
        try:
            backup_name = self._create_backup_name(job)
            backup_path = job.destination / backup_name

            if job.backup_type == BackupType.FULL:
                self._full_backup(job, backup_path)
            elif job.backup_type == BackupType.INCREMENTAL:
                self._incremental_backup(job, backup_path)
            elif job.backup_type == BackupType.DIFFERENTIAL:
                self._differential_backup(job, backup_path)

            job.last_backup = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_config()
            logging.info(f"Backup completed: {job.name}")

        except Exception as e:
            logging.error(f"Backup failed for {job.name}: {e}")

    def _full_backup(self, job: BackupJob, backup_path: Path):
        """Perform full backup"""
        if job.compress:
            with zipfile.ZipFile(str(backup_path) + '.zip', 'w',
                               zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(job.source):
                    for file in files:
                        file_path = Path(root) / file
                        if self._should_backup_file(str(file_path), job):
                            rel_path = file_path.relative_to(job.source)
                            zipf.write(file_path, rel_path)
                            job.file_hashes[str(rel_path)] = self._calculate_file_hash(file_path)
        else:
            shutil.copytree(job.source, backup_path)
            for root, _, files in os.walk(job.source):
                for file in files:
                    file_path = Path(root) / file
                    if self._should_backup_file(str(file_path), job):
                        rel_path = file_path.relative_to(job.source)
                        job.file_hashes[str(rel_path)] = self._calculate_file_hash(file_path)

    def _incremental_backup(self, job: BackupJob, backup_path: Path):
        """Perform incremental backup"""
        changed_files = []
        
        for root, _, files in os.walk(job.source):
            for file in files:
                file_path = Path(root) / file
                if not self._should_backup_file(str(file_path), job):
                    continue
                    
                rel_path = str(file_path.relative_to(job.source))
                current_hash = self._calculate_file_hash(file_path)
                
                if rel_path not in job.file_hashes or job.file_hashes[rel_path] != current_hash:
                    changed_files.append((file_path, rel_path))
                    job.file_hashes[rel_path] = current_hash

        if changed_files:
            if job.compress:
                with zipfile.ZipFile(str(backup_path) + '.zip', 'w',
                                   zipfile.ZIP_DEFLATED) as zipf:
                    for file_path, rel_path in changed_files:
                        zipf.write(file_path, rel_path)
            else:
                backup_path.mkdir(parents=True)
                for file_path, rel_path in changed_files:
                    dest_path = backup_path / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)

    def _differential_backup(self, job: BackupJob, backup_path: Path):
        """Perform differential backup"""
        changed_files = []
        
        for root, _, files in os.walk(job.source):
            for file in files:
                file_path = Path(root) / file
                if not self._should_backup_file(str(file_path), job):
                    continue
                    
                rel_path = str(file_path.relative_to(job.source))
                current_hash = self._calculate_file_hash(file_path)
                
                if rel_path not in job.file_hashes or job.file_hashes[rel_path] != current_hash:
                    changed_files.append((file_path, rel_path))

        if changed_files:
            if job.compress:
                with zipfile.ZipFile(str(backup_path) + '.zip', 'w',
                                   zipfile.ZIP_DEFLATED) as zipf:
                    for file_path, rel_path in changed_files:
                        zipf.write(file_path, rel_path)
            else:
                backup_path.mkdir(parents=True)
                for file_path, rel_path in changed_files:
                    dest_path = backup_path / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)

    def run_backup(self, job_name: str) -> bool:
        """Queue a backup job for execution"""
        if job_name not in self.jobs:
            logging.error(f"Job {job_name} not found")
            return False

        self.backup_queue.put(self.jobs[job_name])
        return True

    def set_schedule(self, job_name: str, schedule_str: str) -> bool:
        """Set backup schedule for a job"""
        if job_name not in self.jobs:
            logging.error(f"Job {job_name} not found")
            return False

        job = self.jobs[job_name]
        job.schedule = schedule_str
        self.save_config()
        
        # Schedule the backup
        if schedule_str == "daily":
            schedule.every().day.at("00:00").do(self.run_backup, job_name)
        elif schedule_str == "weekly":
            schedule.every().week.do(self.run_backup, job_name)
        elif schedule_str == "monthly":
            schedule.every(30).days.do(self.run_backup, job_name)
            
        logging.info(f"Schedule set for job {job_name}: {schedule_str}")
        return True

    def set_compression(self, job_name: str, compress: bool) -> bool:
        """Set compression option for a job"""
        if job_name not in self.jobs:
            logging.error(f"Job {job_name} not found")
            return False

        self.jobs[job_name].compress = compress
        self.save_config()
        logging.info(f"Compression {'enabled' if compress else 'disabled'} for job {job_name}")
        return True

    def add_exclude_pattern(self, job_name: str, pattern: str) -> bool:
        """Add file exclusion pattern to a job"""
        if job_name not in self.jobs:
            logging.error(f"Job {job_name} not found")
            return False

        if pattern not in self.jobs[job_name].exclude_patterns:
            self.jobs[job_name].exclude_patterns.append(pattern)
            self.save_config()
            logging.info(f"Added exclusion pattern '{pattern}' to job {job_name}")
        return True

    def remove_exclude_pattern(self, job_name: str, pattern: str) -> bool:
        """Remove file exclusion pattern from a job"""
        if job_name not in self.jobs:
            logging.error(f"Job {job_name} not found")
            return False

        if pattern in self.jobs[job_name].exclude_patterns:
            self.jobs[job_name].exclude_patterns.remove(pattern)
            self.save_config()
            logging.info(f"Removed exclusion pattern '{pattern}' from job {job_name}")
        return True

    def shutdown(self):
        """Shutdown the backup manager"""
        self.running = False
        self.worker_thread.join()
        self.save_config()
        logging.info("Backup manager shutdown")

def main():
    manager = BackupManager()
    
    try:
        while True:
            print("\nBackup Manager")
            print("1. Add Backup Job")
            print("2. Remove Backup Job")
            print("3. List Jobs")
            print("4. Run Backup")
            print("5. Set Schedule")
            print("6. Set Compression")
            print("7. Manage Exclusions")
            print("8. Exit")
            
            choice = input("\nEnter your choice (1-8): ")
            
            if choice == "1":
                name = input("Enter job name: ")
                source = input("Enter source path: ")
                destination = input("Enter destination path: ")
                print("\nBackup types:")
                print("1. Full")
                print("2. Incremental")
                print("3. Differential")
                backup_type = input("Choose backup type (1-3): ")
                
                backup_types = {
                    "1": BackupType.FULL,
                    "2": BackupType.INCREMENTAL,
                    "3": BackupType.DIFFERENTIAL
                }
                
                if manager.add_job(source, destination, name,
                                 backup_types.get(backup_type, BackupType.FULL)):
                    print("Backup job added successfully!")
                else:
                    print("Failed to add backup job!")
            
            elif choice == "2":
                name = input("Enter job name: ")
                if input(f"Are you sure you want to remove job {name}? (y/n): ").lower() == 'y':
                    if manager.remove_job(name):
                        print("Job removed successfully!")
                    else:
                        print("Failed to remove job!")
            
            elif choice == "3":
                if not manager.jobs:
                    print("No backup jobs found!")
                    continue
                    
                print("\nBackup Jobs:")
                print("-" * 60)
                for name, job in manager.jobs.items():
                    print(f"Name: {name}")
                    print(f"Source: {job.source}")
                    print(f"Destination: {job.destination}")
                    print(f"Type: {job.backup_type}")
                    print(f"Schedule: {job.schedule}")
                    print(f"Compression: {'Enabled' if job.compress else 'Disabled'}")
                    print(f"Last backup: {job.last_backup or 'Never'}")
                    if job.exclude_patterns:
                        print(f"Exclusions: {', '.join(job.exclude_patterns)}")
                    print("-" * 30)
            
            elif choice == "4":
                name = input("Enter job name: ")
                if manager.run_backup(name):
                    print("Backup started!")
                else:
                    print("Failed to start backup!")
            
            elif choice == "5":
                name = input("Enter job name: ")
                print("\nSchedule options:")
                print("1. Daily")
                print("2. Weekly")
                print("3. Monthly")
                print("4. Custom")
                
                schedule_choice = input("Choose schedule (1-4): ")
                schedules = {
                    "1": "daily",
                    "2": "weekly",
                    "3": "monthly",
                    "4": input("Enter custom schedule: ")
                }
                
                if manager.set_schedule(name, schedules.get(schedule_choice, "")):
                    print("Schedule set successfully!")
                else:
                    print("Failed to set schedule!")
            
            elif choice == "6":
                name = input("Enter job name: ")
                compress = input("Enable compression? (y/n): ").lower() == 'y'
                if manager.set_compression(name, compress):
                    print("Compression setting updated!")
                else:
                    print("Failed to update compression setting!")
            
            elif choice == "7":
                name = input("Enter job name: ")
                if name not in manager.jobs:
                    print("Job not found!")
                    continue
                
                print("\n1. Add exclusion pattern")
                print("2. Remove exclusion pattern")
                print("3. List exclusion patterns")
                
                sub_choice = input("Enter choice (1-3): ")
                
                if sub_choice == "1":
                    pattern = input("Enter exclusion pattern: ")
                    if manager.add_exclude_pattern(name, pattern):
                        print("Pattern added successfully!")
                    else:
                        print("Failed to add pattern!")
                
                elif sub_choice == "2":
                    pattern = input("Enter pattern to remove: ")
                    if manager.remove_exclude_pattern(name, pattern):
                        print("Pattern removed successfully!")
                    else:
                        print("Failed to remove pattern!")
                
                elif sub_choice == "3":
                    patterns = manager.jobs[name].exclude_patterns
                    if patterns:
                        print("\nExclusion patterns:")
                        for pattern in patterns:
                            print(f"- {pattern}")
                    else:
                        print("No exclusion patterns found!")
            
            elif choice == "8":
                print("Thank you for using Backup Manager!")
                manager.shutdown()
                break
            
            else:
                print("Invalid choice! Please try again.")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        manager.shutdown()

if __name__ == "__main__":
    main() 