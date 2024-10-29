from models.contact import Contact
from utils.validators import ContactValidator
from utils.file_handlers import FileHandler

class ContactBook:
    def __init__(self):
        self.contacts = []
        self.file_handler = FileHandler()
        self.validator = ContactValidator()
        self.load_contacts()

    def add_contact(self):
        print("\nAdd Contact:")
        while True:
            name = input("Enter name: ").strip()
            if self.validator.validate_name(name):
                break
            print("Name cannot be empty!")

        while True:
            phone = input("Enter phone number: ").strip()
            if self.validator.validate_phone(phone):
                break
            print("Invalid phone number! Please use format: +1234567890 or 1234567890")

        while True:
            email = input("Enter email: ").strip()
            if self.validator.validate_email(email):
                break
            print("Invalid email address!")

        address = input("Enter address: ").strip()
        print("\nAvailable categories: General, Family, Friend, Work, Other")
        category = input("Enter category (press Enter for General): ").strip() or "General"

        contact = Contact(name, phone, email, address, category)
        self.contacts.append(contact)
        self.save_contacts()
        print("\nContact added successfully!")

    def view_contacts(self, category=None):
        if not self.contacts:
            print("\nNo contacts found!")
            return

        filtered_contacts = self.contacts
        if category:
            filtered_contacts = [c for c in self.contacts if c.category.lower() == category.lower()]

        print("\nContact List:")
        for i, contact in enumerate(filtered_contacts, 1):
            self._display_contact(i, contact)

    def _display_contact(self, index, contact):
        print(f"\nContact {index}:")
        print(f"Name: {contact.name}")
        print(f"Phone: {contact.phone}")
        print(f"Email: {contact.email}")
        print(f"Address: {contact.address}")
        print(f"Category: {contact.category}")
        print(f"Created: {contact.created_at}")

    def search_contact(self):
        if not self.contacts:
            print("\nNo contacts found!")
            return
        
        search_term = input("\nEnter name or phone number to search: ").lower()
        found_contacts = [
            contact for contact in self.contacts
            if search_term in contact.name.lower() or search_term in contact.phone
        ]
        
        if found_contacts:
            print("\nSearch Results:")
            for i, contact in enumerate(found_contacts, 1):
                self._display_contact(i, contact)
        else:
            print("\nNo matching contacts found!")

    def edit_contact(self):
        if not self.contacts:
            print("\nNo contacts found!")
            return

        self.view_contacts()
        try:
            index = int(input("\nEnter the contact number to edit: ")) - 1
            if 0 <= index < len(self.contacts):
                self._edit_contact_details(self.contacts[index])
            else:
                print("\nInvalid contact number!")
        except ValueError:
            print("\nPlease enter a valid number!")

    def _edit_contact_details(self, contact):
        print("\nLeave field empty to keep current value")
        
        name = input(f"Enter new name ({contact.name}): ").strip()
        phone = input(f"Enter new phone ({contact.phone}): ").strip()
        email = input(f"Enter new email ({contact.email}): ").strip()
        address = input(f"Enter new address ({contact.address}): ").strip()
        category = input(f"Enter new category ({contact.category}): ").strip()

        if name and self.validator.validate_name(name): 
            contact.name = name
        if phone and self.validator.validate_phone(phone): 
            contact.phone = phone
        if email and self.validator.validate_email(email): 
            contact.email = email
        if address: 
            contact.address = address
        if category: 
            contact.category = category

        self.save_contacts()
        print("\nContact updated successfully!")

    def delete_contact(self):
        if not self.contacts:
            print("\nNo contacts found!")
            return
        
        self.view_contacts()
        try:
            index = int(input("\nEnter the contact number to delete: ")) - 1
            if 0 <= index < len(self.contacts):
                deleted_contact = self.contacts.pop(index)
                self.save_contacts()
                print(f"\nContact '{deleted_contact.name}' deleted successfully!")
            else:
                print("\nInvalid contact number!")
        except ValueError:
            print("\nPlease enter a valid number!")

    def export_contacts(self):
        if not self.contacts:
            print("\nNo contacts to export!")
            return

        filename = self.file_handler.export_to_csv(self.contacts)
        print(f"\nContacts exported to {filename}")

    def save_contacts(self):
        self.file_handler.save_contacts(self.contacts)

    def load_contacts(self):
        contacts_data = self.file_handler.load_contacts()
        self.contacts = [Contact.from_dict(data) for data in contacts_data] 