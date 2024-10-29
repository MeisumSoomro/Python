import json
from pathlib import Path
from datetime import datetime
import re
from datetime import date
import csv
import sqlite3
from collections import defaultdict
import logging
from typing import List, Optional
import os

class Contact:
    def __init__(self, name, phone, email="", address="", birthday="", notes=""):
        self.name = name
        self.phone = self._format_phone(phone)
        self.email = email
        self.address = address
        self.birthday = birthday
        self.notes = notes
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _format_phone(self, phone):
        # Remove any non-digit characters
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone
    
    def to_dict(self):
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "birthday": self.birthday,
            "notes": self.notes,
            "created_at": self.created_at
        }
    
    def validate_email(self, email):
        if not email:
            return True
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_birthday(self, birthday):
        if not birthday:
            return True
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def get_age(self):
        if not self.birthday:
            return None
        try:
            birth_date = datetime.strptime(self.birthday, "%Y-%m-%d").date()
            today = date.today()
            age = today.year - birth_date.year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            return age
        except ValueError:
            return None

class ContactGroup:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.contacts: List[Contact] = []

class ContactBookLogger:
    def __init__(self):
        logging.basicConfig(
            filename='contact_book.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('ContactBook')

    def log_action(self, action: str, details: str):
        self.logger.info(f"{action}: {details}")

class ContactBook:
    def __init__(self):
        self.contacts = []
        self.file_path = Path("contacts.json")
        self.load_contacts()
        self.groups: dict[str, ContactGroup] = {}
        self.logger = ContactBookLogger()
        self.setup_database()
    
    def setup_database(self):
        """Initialize SQLite database for contact history"""
        conn = sqlite3.connect('contact_history.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS contact_history
                    (timestamp TEXT, action TEXT, contact_name TEXT, details TEXT)''')
        conn.commit()
        conn.close()
    
    def add_contact(self, name, phone, email="", address="", birthday="", notes=""):
        # Check for duplicate phone numbers
        if self._phone_exists(phone):
            print(f"A contact with phone number {phone} already exists!")
            return
        
        contact = Contact(name, phone, email, address, birthday, notes)
        self.contacts.append(contact)
        self.save_contacts()
        print(f"Contact {name} added successfully!")
    
    def _phone_exists(self, phone):
        digits = ''.join(filter(str.isdigit, phone))
        for contact in self.contacts:
            if ''.join(filter(str.isdigit, contact.phone)) == digits:
                return True
        return False
    
    def remove_contact(self, name):
        original_length = len(self.contacts)
        self.contacts = [c for c in self.contacts if c.name.lower() != name.lower()]
        
        if len(self.contacts) < original_length:
            self.save_contacts()
            print(f"Contact {name} removed successfully!")
        else:
            print(f"Contact {name} not found!")
    
    def search_contact(self, query):
        matches = []
        query = query.lower()
        for contact in self.contacts:
            if (query in contact.name.lower() or 
                query in contact.phone or 
                query in contact.email.lower() or 
                query in contact.address.lower()):
                matches.append(contact)
        return matches
    
    def edit_contact(self, name):
        contact = next((c for c in self.contacts if c.name.lower() == name.lower()), None)
        if not contact:
            print(f"Contact {name} not found!")
            return
        
        print("\nLeave field empty to keep current value")
        new_phone = input(f"Phone ({contact.phone}): ").strip()
        new_email = input(f"Email ({contact.email}): ").strip()
        new_address = input(f"Address ({contact.address}): ").strip()
        new_birthday = input(f"Birthday ({contact.birthday}): ").strip()
        new_notes = input(f"Notes ({contact.notes}): ").strip()
        
        if new_phone and new_phone != contact.phone:
            contact.phone = contact._format_phone(new_phone)
        if new_email:
            contact.email = new_email
        if new_address:
            contact.address = new_address
        if new_birthday:
            contact.birthday = new_birthday
        if new_notes:
            contact.notes = new_notes
            
        self.save_contacts()
        print(f"Contact {name} updated successfully!")
    
    def display_contacts(self):
        if not self.contacts:
            print("No contacts found!")
            return
        
        # Sort contacts by name
        sorted_contacts = sorted(self.contacts, key=lambda x: x.name.lower())
        
        print("\nContact List:")
        print("-" * 60)
        for contact in sorted_contacts:
            print(f"Name: {contact.name}")
            print(f"Phone: {contact.phone}")
            if contact.email:
                print(f"Email: {contact.email}")
            if contact.address:
                print(f"Address: {contact.address}")
            if contact.birthday:
                print(f"Birthday: {contact.birthday}")
            if contact.notes:
                print(f"Notes: {contact.notes}")
            print(f"Added: {contact.created_at}")
            print("-" * 60)
    
    def save_contacts(self):
        contacts_data = [contact.to_dict() for contact in self.contacts]
        with open(self.file_path, 'w') as f:
            json.dump(contacts_data, f, indent=4)
    
    def load_contacts(self):
        if not self.file_path.exists():
            return
        
        try:
            with open(self.file_path, 'r') as f:
                contacts_data = json.load(f)
                for data in contacts_data:
                    contact = Contact(**data)
                    self.contacts.append(contact)
        except json.JSONDecodeError:
            print("Error loading contacts file!")
    
    def export_to_csv(self, filename="contacts_export.csv"):
        if not self.contacts:
            print("No contacts to export!")
            return
        
        fields = ["name", "phone", "email", "address", "birthday", "notes", "created_at"]
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for contact in self.contacts:
                    writer.writerow(contact.to_dict())
            print(f"Contacts exported successfully to {filename}")
        except Exception as e:
            print(f"Error exporting contacts: {e}")
    
    def import_from_csv(self, filename="contacts_import.csv"):
        try:
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                imported = 0
                skipped = 0
                for row in reader:
                    if not self._phone_exists(row['phone']):
                        contact = Contact(**row)
                        self.contacts.append(contact)
                        imported += 1
                    else:
                        skipped += 1
                self.save_contacts()
                print(f"Imported {imported} contacts, skipped {skipped} duplicates")
        except FileNotFoundError:
            print(f"File {filename} not found!")
        except Exception as e:
            print(f"Error importing contacts: {e}")
    
    def get_birthdays_this_month(self):
        current_month = datetime.now().month
        birthday_contacts = []
        
        for contact in self.contacts:
            if contact.birthday:
                try:
                    birthday = datetime.strptime(contact.birthday, "%Y-%m-%d")
                    if birthday.month == current_month:
                        birthday_contacts.append(contact)
                except ValueError:
                    continue
        
        return birthday_contacts
    
    def backup_contacts(self):
        backup_path = self.file_path.with_name(f"contacts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        try:
            with open(backup_path, 'w') as f:
                json.dump([c.to_dict() for c in self.contacts], f, indent=4)
            print(f"Backup created successfully: {backup_path}")
        except Exception as e:
            print(f"Error creating backup: {e}")
    
    def create_group(self, name: str, description: str = ""):
        """Create a new contact group"""
        if name in self.groups:
            print(f"Group '{name}' already exists!")
            return
        self.groups[name] = ContactGroup(name, description)
        print(f"Group '{name}' created successfully!")
        self.logger.log_action("Create Group", f"Group {name} created")
    
    def add_to_group(self, contact_name: str, group_name: str):
        """Add a contact to a group"""
        contact = self.search_contact(contact_name)
        if not contact:
            print(f"Contact '{contact_name}' not found!")
            return
        
        if group_name not in self.groups:
            print(f"Group '{group_name}' not found!")
            return
        
        self.groups[group_name].contacts.append(contact[0])
        print(f"Added {contact_name} to group {group_name}")
        self.logger.log_action("Add to Group", f"Contact {contact_name} added to group {group_name}")
    
    def display_group(self, group_name: str):
        """Display all contacts in a group"""
        if group_name not in self.groups:
            print(f"Group '{group_name}' not found!")
            return
        
        group = self.groups[group_name]
        print(f"\nGroup: {group.name}")
        print(f"Description: {group.description}")
        print("-" * 60)
        
        if not group.contacts:
            print("No contacts in this group")
            return
        
        for contact in group.contacts:
            print(f"Name: {contact.name}")
            print(f"Phone: {contact.phone}")
            print("-" * 30)
    
    def generate_report(self):
        """Generate a detailed report of contacts"""
        if not self.contacts:
            print("No contacts to generate report!")
            return
        
        report = defaultdict(int)
        report['total_contacts'] = len(self.contacts)
        
        # Count contacts by domain
        for contact in self.contacts:
            if contact.email:
                domain = contact.email.split('@')[-1]
                report[f'domain_{domain}'] += 1
        
        # Count contacts with birthdays this month
        birthday_contacts = self.get_birthdays_this_month()
        report['birthdays_this_month'] = len(birthday_contacts)
        
        print("\nContact Book Report")
        print("-" * 60)
        print(f"Total Contacts: {report['total_contacts']}")
        print("\nEmail Domains:")
        for key, value in report.items():
            if key.startswith('domain_'):
                print(f"  {key[7:]}: {value}")
        print(f"\nBirthdays this month: {report['birthdays_this_month']}")
    
    def log_history(self, action: str, contact_name: str, details: str):
        """Log contact history to SQLite database"""
        conn = sqlite3.connect('contact_history.db')
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO contact_history VALUES (?, ?, ?, ?)",
                 (timestamp, action, contact_name, details))
        conn.commit()
        conn.close()
    
    def view_history(self, contact_name: Optional[str] = None):
        """View contact history"""
        conn = sqlite3.connect('contact_history.db')
        c = conn.cursor()
        
        if contact_name:
            c.execute("SELECT * FROM contact_history WHERE contact_name = ?", (contact_name,))
        else:
            c.execute("SELECT * FROM contact_history")
        
        history = c.fetchall()
        conn.close()
        
        if not history:
            print("No history found!")
            return
        
        print("\nContact History:")
        print("-" * 60)
        for entry in history:
            print(f"Time: {entry[0]}")
            print(f"Action: {entry[1]}")
            print(f"Contact: {entry[2]}")
            print(f"Details: {entry[3]}")
            print("-" * 30)

def main():
    contact_book = ContactBook()
    
    while True:
        print("\nContact Book Menu:")
        print("1. Add Contact")
        print("2. Remove Contact")
        print("3. Search Contacts")
        print("4. Display All Contacts")
        print("5. Edit Contact")
        print("6. Export to CSV")
        print("7. Import from CSV")
        print("8. Show Birthdays This Month")
        print("9. Backup Contacts")
        print("10. Create Group")
        print("11. Add Contact to Group")
        print("12. Display Group")
        print("13. Generate Report")
        print("14. View History")
        print("15. Exit")
        
        choice = input("\nEnter your choice (1-15): ")
        
        if choice == "1":
            name = input("Enter name: ")
            phone = input("Enter phone number: ")
            email = input("Enter email (optional): ")
            address = input("Enter address (optional): ")
            birthday = input("Enter birthday (optional): ")
            notes = input("Enter notes (optional): ")
            contact_book.add_contact(name, phone, email, address, birthday, notes)
        
        elif choice == "2":
            name = input("Enter name to remove: ")
            contact_book.remove_contact(name)
        
        elif choice == "3":
            query = input("Enter search term (name/phone/email/address): ")
            matches = contact_book.search_contact(query)
            if matches:
                print(f"\nFound {len(matches)} matching contacts:")
                for contact in matches:
                    print(f"\nName: {contact.name}")
                    print(f"Phone: {contact.phone}")
                    if contact.email:
                        print(f"Email: {contact.email}")
                    if contact.address:
                        print(f"Address: {contact.address}")
            else:
                print("No matching contacts found!")
        
        elif choice == "4":
            contact_book.display_contacts()
        
        elif choice == "5":
            name = input("Enter name of contact to edit: ")
            contact_book.edit_contact(name)
        
        elif choice == "6":
            filename = input("Enter export filename (default: contacts_export.csv): ").strip()
            contact_book.export_to_csv(filename if filename else "contacts_export.csv")
        
        elif choice == "7":
            filename = input("Enter import filename (default: contacts_import.csv): ").strip()
            contact_book.import_from_csv(filename if filename else "contacts_import.csv")
        
        elif choice == "8":
            birthday_contacts = contact_book.get_birthdays_this_month()
            if birthday_contacts:
                print("\nContacts with birthdays this month:")
                for contact in birthday_contacts:
                    age = contact.get_age()
                    print(f"\nName: {contact.name}")
                    print(f"Birthday: {contact.birthday}")
                    if age:
                        print(f"Turning Age: {age + 1}")
            else:
                print("No birthdays this month!")
        
        elif choice == "9":
            contact_book.backup_contacts()
        
        elif choice == "10":
            name = input("Enter group name: ")
            description = input("Enter group description (optional): ")
            contact_book.create_group(name, description)
        
        elif choice == "11":
            contact_name = input("Enter contact name: ")
            group_name = input("Enter group name: ")
            contact_book.add_to_group(contact_name, group_name)
        
        elif choice == "12":
            group_name = input("Enter group name: ")
            contact_book.display_group(group_name)
        
        elif choice == "13":
            contact_book.generate_report()
        
        elif choice == "14":
            name = input("Enter contact name (or press Enter for all history): ").strip()
            contact_book.view_history(name if name else None)
        
        elif choice == "15":
            print("Thank you for using Contact Book!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 