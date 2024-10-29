import json
import csv
from datetime import datetime
import os

def ensure_directory(directory):
    """Ensure that a directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)

class FileHandler:
    @staticmethod
    def save_contacts(contacts, filename='contacts.json'):
        """Save contacts to JSON file."""
        with open(filename, 'w') as file:
            contacts_data = [contact.to_dict() for contact in contacts]
            json.dump(contacts_data, file, indent=2)

    @staticmethod
    def load_contacts(filename='contacts.json'):
        """Load contacts from JSON file."""
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    @staticmethod
    def export_to_csv(contacts):
        """Export contacts to CSV file."""
        ensure_directory('exports')
        filename = f"exports/contacts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Phone', 'Email', 'Address', 'Category', 'Created At'])
            for contact in contacts:
                writer.writerow([
                    contact.name,
                    contact.phone,
                    contact.email,
                    contact.address,
                    contact.category,
                    contact.created_at
                ])
        return filename 