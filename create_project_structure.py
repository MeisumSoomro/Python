import os

def create_project_structure():
    project_number = "032"
    project_name = "system_monitor"
    
    base_path = f"python_projects/{project_number}_project"
    
    # Create main project directory
    os.makedirs(base_path, exist_ok=True)
    
    # Create the main Python file
    with open(f"{base_path}/system_monitor.py", "w") as f:
        f.write("# System Monitor Application\n\n")
    
    # Create requirements.txt
    with open(f"{base_path}/requirements.txt", "w") as f:
        f.write("psutil\n")
        f.write("PySimpleGUI\n")
        f.write("matplotlib\n")
        f.write("pandas\n")
    
    # Create README.md
    with open(f"{base_path}/README.md", "w") as f:
        f.write("# System Monitor\n\n")
        f.write("A real-time system monitoring tool with GUI interface.\n\n")
        f.write("## Features\n")
        f.write("- CPU usage monitoring\n")
        f.write("- Memory usage tracking\n")
        f.write("- Disk space analysis\n")
        f.write("- Network statistics\n")
        f.write("- Process management\n")
        f.write("- Performance alerts\n\n")
        f.write("## Requirements\n")
        f.write("- Python 3.x\n")
        f.write("- psutil\n")
        f.write("- PySimpleGUI\n")
        f.write("- matplotlib\n")
        f.write("- pandas\n")

if __name__ == "__main__":
    create_project_structure() 