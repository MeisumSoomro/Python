from typing import Dict, List, Set
import json
from pathlib import Path
from datetime import datetime
import copy

class AddressBook:
    def __init__(self, name: str):
        self.name = name
        self.contacts = {}  # Dictionary with contact_id as key
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_modified = self.created_at
    
    def add_contact(self, contact_id: str, contact_data: dict) -> bool:
        if contact_id in self.contacts:
            return False
        self.contacts[contact_id] = contact_data
        self.last_modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True
    
    def remove_contact(self, contact_id: str) -> bool:
        if contact_id not in self.contacts:
            return False
        del self.contacts[contact_id]
        self.last_modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True
    
    def get_contact_count(self) -> int:
        return len(self.contacts)

class AddressBookManager:
    def __init__(self):
        self.address_books: Dict[str, AddressBook] = {}
        self.file_path = Path("address_books.json")
        self.load_address_books()
    
    def create_address_book(self, name: str) -> bool:
        if name in self.address_books:
            print(f"Address book '{name}' already exists!")
            return False
        
        self.address_books[name] = AddressBook(name)
        self.save_address_books()
        print(f"Address book '{name}' created successfully!")
        return True
    
    def merge_address_books(self, book1_name: str, book2_name: str, merged_name: str) -> bool:
        """Merge two address books into a new one"""
        if book1_name not in self.address_books or book2_name not in self.address_books:
            print("One or both address books not found!")
            return False
        
        if merged_name in self.address_books:
            print(f"Address book '{merged_name}' already exists!")
            return False
        
        merged_book = AddressBook(merged_name)
        book1 = self.address_books[book1_name]
        book2 = self.address_books[book2_name]
        
        # Merge contacts from both books
        for contact_id, contact_data in book1.contacts.items():
            merged_book.add_contact(contact_id, copy.deepcopy(contact_data))
        
        for contact_id, contact_data in book2.contacts.items():
            if contact_id not in merged_book.contacts:
                merged_book.add_contact(contact_id, copy.deepcopy(contact_data))
            else:
                # Handle duplicate contacts by keeping the most recently modified one
                if contact_data.get('last_modified', '') > merged_book.contacts[contact_id].get('last_modified', ''):
                    merged_book.contacts[contact_id] = copy.deepcopy(contact_data)
        
        self.address_books[merged_name] = merged_book
        self.save_address_books()
        print(f"Address books merged successfully into '{merged_name}'!")
        return True
    
    def find_duplicates(self, book_name: str) -> List[List[str]]:
        """Find duplicate contacts within an address book"""
        if book_name not in self.address_books:
            print(f"Address book '{book_name}' not found!")
            return []
        
        book = self.address_books[book_name]
        duplicates = []
        seen_phones = {}
        seen_emails = {}
        
        for contact_id, contact_data in book.contacts.items():
            phone = contact_data.get('phone', '')
            email = contact_data.get('email', '')
            
            if phone:
                if phone in seen_phones:
                    duplicates.append([seen_phones[phone], contact_id])
                else:
                    seen_phones[phone] = contact_id
            
            if email:
                if email in seen_emails:
                    duplicates.append([seen_emails[email], contact_id])
                else:
                    seen_emails[email] = contact_id
        
        return duplicates
    
    def compare_address_books(self, book1_name: str, book2_name: str) -> Dict[str, Set[str]]:
        """Compare two address books and return differences"""
        if book1_name not in self.address_books or book2_name not in self.address_books:
            print("One or both address books not found!")
            return {}
        
        book1 = self.address_books[book1_name]
        book2 = self.address_books[book2_name]
        
        book1_contacts = set(book1.contacts.keys())
        book2_contacts = set(book2.contacts.keys())
        
        return {
            'only_in_first': book1_contacts - book2_contacts,
            'only_in_second': book2_contacts - book1_contacts,
            'common': book1_contacts & book2_contacts
        }
    
    def save_address_books(self):
        """Save all address books to JSON file"""
        data = {}
        for name, book in self.address_books.items():
            data[name] = {
                'name': book.name,
                'contacts': book.contacts,
                'created_at': book.created_at,
                'last_modified': book.last_modified
            }
        
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_address_books(self):
        """Load address books from JSON file"""
        if not self.file_path.exists():
            return
        
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for name, book_data in data.items():
                    book = AddressBook(name)
                    book.contacts = book_data['contacts']
                    book.created_at = book_data['created_at']
                    book.last_modified = book_data['last_modified']
                    self.address_books[name] = book
        except json.JSONDecodeError:
            print("Error loading address books file!")

def main():
    manager = AddressBookManager()
    
    while True:
        print("\nAddress Book Manager Menu:")
        print("1. Create New Address Book")
        print("2. List Address Books")
        print("3. Add Contact to Address Book")
        print("4. Merge Address Books")
        print("5. Find Duplicates in Address Book")
        print("6. Compare Address Books")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == "1":
            name = input("Enter address book name: ")
            manager.create_address_book(name)
        
        elif choice == "2":
            if not manager.address_books:
                print("No address books found!")
            else:
                print("\nAddress Books:")
                for name, book in manager.address_books.items():
                    print(f"\nName: {name}")
                    print(f"Contacts: {book.get_contact_count()}")
                    print(f"Created: {book.created_at}")
                    print(f"Last Modified: {book.last_modified}")
        
        elif choice == "3":
            book_name = input("Enter address book name: ")
            if book_name not in manager.address_books:
                print(f"Address book '{book_name}' not found!")
                continue
            
            contact_id = input("Enter contact ID: ")
            name = input("Enter contact name: ")
            phone = input("Enter contact phone: ")
            email = input("Enter contact email (optional): ")
            
            contact_data = {
                'name': name,
                'phone': phone,
                'email': email,
                'last_modified': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if manager.address_books[book_name].add_contact(contact_id, contact_data):
                manager.save_address_books()
                print("Contact added successfully!")
            else:
                print("Contact ID already exists!")
        
        elif choice == "4":
            book1 = input("Enter first address book name: ")
            book2 = input("Enter second address book name: ")
            merged = input("Enter name for merged address book: ")
            manager.merge_address_books(book1, book2, merged)
        
        elif choice == "5":
            book_name = input("Enter address book name: ")
            duplicates = manager.find_duplicates(book_name)
            if duplicates:
                print("\nDuplicate contacts found:")
                for dup in duplicates:
                    print(f"Contact IDs: {dup[0]} and {dup[1]}")
            else:
                print("No duplicates found!")
        
        elif choice == "6":
            book1 = input("Enter first address book name: ")
            book2 = input("Enter second address book name: ")
            diff = manager.compare_address_books(book1, book2)
            if diff:
                print(f"\nContacts only in '{book1}': {len(diff['only_in_first'])}")
                print(f"Contacts only in '{book2}': {len(diff['only_in_second'])}")
                print(f"Common contacts: {len(diff['common'])}")
        
        elif choice == "7":
            print("Thank you for using Address Book Manager!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 