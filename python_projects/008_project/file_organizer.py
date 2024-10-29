import os
import shutil
from datetime import datetime

class FileOrganizer:
    def __init__(self, directory):
        self.directory = directory
        self.extensions = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.csv'],
            'Audio': ['.mp3', '.wav', '.flac'],
            'Video': ['.mp4', '.avi', '.mkv'],
            'Archives': ['.zip', '.rar', '.7z'],
            'Code': ['.py', '.java', '.cpp', '.html', '.css', '.js']
        }
        
    def create_folders(self):
        for folder in self.extensions.keys():
            folder_path = os.path.join(self.directory, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                
    def organize_files(self):
        for filename in os.listdir(self.directory):
            file_path = os.path.join(self.directory, filename)
            
            # Skip if it's a directory
            if os.path.isdir(file_path):
                continue
                
            # Get file extension
            file_ext = os.path.splitext(filename)[1].lower()
            
            # Find appropriate folder for the file
            for folder, extensions in self.extensions.items():
                if file_ext in extensions:
                    destination = os.path.join(self.directory, folder, filename)
                    try:
                        shutil.move(file_path, destination)
                        print(f"Moved {filename} to {folder}")
                    except Exception as e:
                        print(f"Error moving {filename}: {str(e)}")
                    break

def main():
    print("Welcome to File Organizer!")
    
    while True:
        directory = input("Enter directory path to organize: ")
        if os.path.exists(directory):
            organizer = FileOrganizer(directory)
            organizer.create_folders()
            organizer.organize_files()
            print("\nOrganization complete!")
        else:
            print("Directory does not exist!")
            
        if input("\nOrganize another directory? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main() 