import os
import shutil
from pathlib import Path

def get_extension(filename):
    """Get the extension of a file (lowercase)"""
    return os.path.splitext(filename)[1][1:].lower()

def create_folder(directory, folder_name):
    """Create a folder if it doesn't exist"""
    folder_path = os.path.join(directory, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def organize_files(directory):
    """Organize files in the given directory by their extensions"""
    try:
        # Count total files
        total_files = 0
        organized_files = 0
        
        # Common file type categories
        categories = {
            'Images': ['jpg', 'jpeg', 'png', 'gif', 'bmp'],
            'Documents': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'],
            'Audio': ['mp3', 'wav', 'flac', 'm4a'],
            'Video': ['mp4', 'avi', 'mkv', 'mov'],
            'Archives': ['zip', 'rar', '7z', 'tar', 'gz'],
            'Code': ['py', 'java', 'cpp', 'html', 'css', 'js']
        }
        
        # Count files first
        for filename in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, filename)):
                total_files += 1
        
        if total_files == 0:
            print("No files found in the directory!")
            return
        
        # Organize files
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Skip if it's not a file
            if not os.path.isfile(file_path):
                continue
                
            # Get the extension
            extension = get_extension(filename)
            if not extension:
                continue
                
            # Determine category
            category = 'Others'
            for cat, extensions in categories.items():
                if extension in extensions:
                    category = cat
                    break
            
            # Create category folder and move file
            category_path = create_folder(directory, category)
            destination = os.path.join(category_path, filename)
            
            # Move file if it's not already in the destination
            if file_path != destination:
                shutil.move(file_path, destination)
                organized_files += 1
                print(f"Moved: {filename} -> {category}")
        
        print(f"\nOrganization complete!")
        print(f"Total files: {total_files}")
        print(f"Files organized: {organized_files}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    print("=== File Organizer ===")
    
    while True:
        print("\nOptions:")
        print("1. Organize a directory")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == '1':
            directory = input("Enter directory path to organize: ").strip()
            
            if os.path.exists(directory):
                print(f"\nOrganizing files in: {directory}")
                organize_files(directory)
            else:
                print("Directory not found!")
                
        elif choice == '2':
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 