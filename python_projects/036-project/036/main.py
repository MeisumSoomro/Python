from models.contact_book import ContactBook

def main():
    contact_book = ContactBook()
    
    while True:
        print("\n=== Contact Book Menu ===")
        print("1. Add Contact")
        print("2. View All Contacts")
        print("3. View Contacts by Category")
        print("4. Search Contact")
        print("5. Edit Contact")
        print("6. Delete Contact")
        print("7. Export Contacts to CSV")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == '1':
            contact_book.add_contact()
        elif choice == '2':
            contact_book.view_contacts()
        elif choice == '3':
            category = input("Enter category to filter: ")
            contact_book.view_contacts(category)
        elif choice == '4':
            contact_book.search_contact()
        elif choice == '5':
            contact_book.edit_contact()
        elif choice == '6':
            contact_book.delete_contact()
        elif choice == '7':
            contact_book.export_contacts()
        elif choice == '8':
            print("\nThank you for using Contact Book!")
            break
        else:
            print("\nInvalid choice! Please try again.")

if __name__ == "__main__":
    main() 