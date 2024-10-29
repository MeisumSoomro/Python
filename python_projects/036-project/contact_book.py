from utils.validators import validate_phone, validate_email, validate_name
from utils.file_handlers import FileHandler
from datetime import datetime

# Update the ContactBook class to use the new utilities
class ContactBook:
    def __init__(self):
        self.contacts = []
        self.file_handler = FileHandler()
        self.load_contacts()

    def add_contact(self):
        print("\nAdd Contact:")
        while True:
            name = input("Enter name: ").strip()
            if validate_name(name):
                break
            print("Name cannot be empty!")

        while True:
            phone = input("Enter phone number: ").strip()
            if validate_phone(phone):
                break
            print("Invalid phone number! Please use format: +1234567890 or 1234567890")

        while True:
            email = input("Enter email: ").strip()
            if validate_email(email):
                break
            print("Invalid email address!")

        # ... rest of the method remains the same ...

    def save_contacts(self):
        self.file_handler.save_contacts(self.contacts)

    def load_contacts(self):
        contacts_data = self.file_handler.load_contacts()
        self.contacts = [Contact.from_dict(data) for data in contacts_data]

    def export_contacts(self):
        if not self.contacts:
            print("\nNo contacts to export!")
            return

        filename = self.file_handler.export_to_csv(self.contacts)
        print(f"\nContacts exported to {filename}")

    # ... rest of the class remains the same ... 