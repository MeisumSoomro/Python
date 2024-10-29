from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path
import uuid

class Book:
    def __init__(self, title: str, author: str, isbn: str, copies: int = 1):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.total_copies = copies
        self.available_copies = copies
        self.borrowed_by: Dict[str, 'BorrowRecord'] = {}  # patron_id: BorrowRecord
        self.added_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.category = ""
        self.location = ""  # Physical location in library
        self.rating = 0.0
        self.reviews: List[Dict] = []

class Patron:
    def __init__(self, name: str, email: str, patron_id: str):
        self.name = name
        self.email = email
        self.patron_id = patron_id
        self.join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.borrowed_books: Dict[str, 'BorrowRecord'] = {}  # isbn: BorrowRecord
        self.history: List[Dict] = []  # Borrowing history
        self.fines = 0.0
        self.status = "Active"  # Active, Suspended, Expired

class BorrowRecord:
    def __init__(self, isbn: str, patron_id: str):
        self.isbn = isbn
        self.patron_id = patron_id
        self.borrow_date = datetime.now()
        self.due_date = self.borrow_date + timedelta(days=14)  # 2 weeks by default
        self.return_date: Optional[datetime] = None
        self.renewed_count = 0
        self.status = "Borrowed"  # Borrowed, Returned, Overdue
        self.fine = 0.0

class Library:
    def __init__(self):
        self.books: Dict[str, Book] = {}  # isbn: Book
        self.patrons: Dict[str, Patron] = {}  # patron_id: Patron
        self.daily_fine_rate = 1.0  # $1 per day
        self.max_renewals = 2
        self.file_path = Path("library_data.json")
        self.load_data()

    def add_book(self, title: str, author: str, isbn: str, copies: int = 1) -> bool:
        if isbn in self.books:
            self.books[isbn].total_copies += copies
            self.books[isbn].available_copies += copies
            print(f"Added {copies} copies to existing book '{title}'")
        else:
            self.books[isbn] = Book(title, author, isbn, copies)
            print(f"Added new book '{title}'")
        self.save_data()
        return True

    def register_patron(self, name: str, email: str) -> str:
        patron_id = str(uuid.uuid4())[:8]
        self.patrons[patron_id] = Patron(name, email, patron_id)
        self.save_data()
        print(f"Registered new patron: {name} (ID: {patron_id})")
        return patron_id

    def borrow_book(self, isbn: str, patron_id: str) -> bool:
        if isbn not in self.books or patron_id not in self.patrons:
            print("Invalid book ISBN or patron ID")
            return False

        book = self.books[isbn]
        patron = self.patrons[patron_id]

        if patron.status != "Active":
            print(f"Patron account is {patron.status}")
            return False

        if patron.fines > 0:
            print(f"Patron has unpaid fines: ${patron.fines}")
            return False

        if book.available_copies == 0:
            print("No copies available")
            return False

        if len(patron.borrowed_books) >= 5:
            print("Maximum borrowing limit reached")
            return False

        borrow_record = BorrowRecord(isbn, patron_id)
        book.borrowed_by[patron_id] = borrow_record
        patron.borrowed_books[isbn] = borrow_record
        book.available_copies -= 1

        patron.history.append({
            "action": "borrowed",
            "book_title": book.title,
            "date": borrow_record.borrow_date.strftime("%Y-%m-%d %H:%M:%S")
        })

        self.save_data()
        print(f"Book '{book.title}' borrowed successfully")
        print(f"Due date: {borrow_record.due_date.strftime('%Y-%m-%d')}")
        return True

    def return_book(self, isbn: str, patron_id: str) -> bool:
        if isbn not in self.books or patron_id not in self.patrons:
            print("Invalid book ISBN or patron ID")
            return False

        book = self.books[isbn]
        patron = self.patrons[patron_id]

        if isbn not in patron.borrowed_books:
            print("This book was not borrowed by this patron")
            return False

        borrow_record = patron.borrowed_books[isbn]
        borrow_record.return_date = datetime.now()
        borrow_record.status = "Returned"

        # Calculate any fines
        if borrow_record.return_date > borrow_record.due_date:
            days_overdue = (borrow_record.return_date - borrow_record.due_date).days
            fine = days_overdue * self.daily_fine_rate
            patron.fines += fine
            borrow_record.fine = fine
            print(f"Late return fine: ${fine}")

        book.available_copies += 1
        del patron.borrowed_books[isbn]
        del book.borrowed_by[patron_id]

        patron.history.append({
            "action": "returned",
            "book_title": book.title,
            "date": borrow_record.return_date.strftime("%Y-%m-%d %H:%M:%S")
        })

        self.save_data()
        print(f"Book '{book.title}' returned successfully")
        return True

    def renew_book(self, isbn: str, patron_id: str) -> bool:
        if isbn not in self.books or patron_id not in self.patrons:
            print("Invalid book ISBN or patron ID")
            return False

        patron = self.patrons[patron_id]
        if isbn not in patron.borrowed_books:
            print("This book was not borrowed by this patron")
            return False

        borrow_record = patron.borrowed_books[isbn]
        if borrow_record.renewed_count >= self.max_renewals:
            print("Maximum renewals reached")
            return False

        if borrow_record.due_date < datetime.now():
            print("Book is overdue and cannot be renewed")
            return False

        borrow_record.due_date += timedelta(days=14)
        borrow_record.renewed_count += 1
        
        self.save_data()
        print(f"Book renewed. New due date: {borrow_record.due_date.strftime('%Y-%m-%d')}")
        return True

    def add_review(self, isbn: str, patron_id: str, rating: float, comment: str) -> bool:
        if isbn not in self.books or patron_id not in self.patrons:
            print("Invalid book ISBN or patron ID")
            return False

        if rating < 1 or rating > 5:
            print("Rating must be between 1 and 5")
            return False

        book = self.books[isbn]
        patron = self.patrons[patron_id]

        review = {
            "patron_name": patron.name,
            "rating": rating,
            "comment": comment,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        book.reviews.append(review)
        # Update average rating
        book.rating = sum(r["rating"] for r in book.reviews) / len(book.reviews)
        
        self.save_data()
        print("Review added successfully")
        return True

    def pay_fine(self, patron_id: str, amount: float) -> bool:
        if patron_id not in self.patrons:
            print("Invalid patron ID")
            return False

        patron = self.patrons[patron_id]
        if amount > patron.fines:
            print("Payment amount exceeds outstanding fines")
            return False

        patron.fines -= amount
        patron.history.append({
            "action": "paid_fine",
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        self.save_data()
        print(f"Payment of ${amount} processed. Remaining fine: ${patron.fines}")
        return True

    def save_data(self):
        """Save library data to JSON file"""
        data = {
            "books": {isbn: self._serialize_book(book) for isbn, book in self.books.items()},
            "patrons": {pid: self._serialize_patron(patron) for pid, patron in self.patrons.items()}
        }
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        """Load library data from JSON file"""
        if not self.file_path.exists():
            return

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.books = {isbn: self._deserialize_book(bdata) for isbn, bdata in data["books"].items()}
                self.patrons = {pid: self._deserialize_patron(pdata) for pid, pdata in data["patrons"].items()}
        except json.JSONDecodeError:
            print("Error loading library data!")

    def _serialize_book(self, book: Book) -> dict:
        return {
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies,
            "borrowed_by": {pid: self._serialize_borrow_record(record) 
                          for pid, record in book.borrowed_by.items()},
            "added_date": book.added_date,
            "category": book.category,
            "location": book.location,
            "rating": book.rating,
            "reviews": book.reviews
        }

    def _serialize_patron(self, patron: Patron) -> dict:
        return {
            "name": patron.name,
            "email": patron.email,
            "patron_id": patron.patron_id,
            "join_date": patron.join_date,
            "borrowed_books": {isbn: self._serialize_borrow_record(record) 
                             for isbn, record in patron.borrowed_books.items()},
            "history": patron.history,
            "fines": patron.fines,
            "status": patron.status
        }

    def _serialize_borrow_record(self, record: BorrowRecord) -> dict:
        return {
            "isbn": record.isbn,
            "patron_id": record.patron_id,
            "borrow_date": record.borrow_date.strftime("%Y-%m-%d %H:%M:%S"),
            "due_date": record.due_date.strftime("%Y-%m-%d %H:%M:%S"),
            "return_date": record.return_date.strftime("%Y-%m-%d %H:%M:%S") if record.return_date else None,
            "renewed_count": record.renewed_count,
            "status": record.status,
            "fine": record.fine
        }

    def _deserialize_book(self, data: dict) -> Book:
        book = Book(data["title"], data["author"], data["isbn"], data["total_copies"])
        book.available_copies = data["available_copies"]
        book.borrowed_by = {pid: self._deserialize_borrow_record(record) 
                          for pid, record in data["borrowed_by"].items()}
        book.added_date = data["added_date"]
        book.category = data["category"]
        book.location = data["location"]
        book.rating = data["rating"]
        book.reviews = data["reviews"]
        return book

    def _deserialize_patron(self, data: dict) -> Patron:
        patron = Patron(data["name"], data["email"], data["patron_id"])
        patron.join_date = data["join_date"]
        patron.borrowed_books = {isbn: self._deserialize_borrow_record(record) 
                               for isbn, record in data["borrowed_books"].items()}
        patron.history = data["history"]
        patron.fines = data["fines"]
        patron.status = data["status"]
        return patron

    def _deserialize_borrow_record(self, data: dict) -> BorrowRecord:
        record = BorrowRecord(data["isbn"], data["patron_id"])
        record.borrow_date = datetime.strptime(data["borrow_date"], "%Y-%m-%d %H:%M:%S")
        record.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d %H:%M:%S")
        if data["return_date"]:
            record.return_date = datetime.strptime(data["return_date"], "%Y-%m-%d %H:%M:%S")
        record.renewed_count = data["renewed_count"]
        record.status = data["status"]
        record.fine = data["fine"]
        return record

def main():
    library = Library()
    
    while True:
        print("\nLibrary Management System")
        print("1. Add Book")
        print("2. Register Patron")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. Renew Book")
        print("6. Add Review")
        print("7. Pay Fine")
        print("8. View Book Details")
        print("9. View Patron Details")
        print("10. Exit")
        
        choice = input("\nEnter your choice (1-10): ")
        
        if choice == "1":
            title = input("Enter book title: ")
            author = input("Enter author name: ")
            isbn = input("Enter ISBN: ")
            copies = int(input("Enter number of copies: "))
            library.add_book(title, author, isbn, copies)
        
        elif choice == "2":
            name = input("Enter patron name: ")
            email = input("Enter patron email: ")
            patron_id = library.register_patron(name, email)
            print(f"Patron ID: {patron_id}")
        
        elif choice == "3":
            isbn = input("Enter book ISBN: ")
            patron_id = input("Enter patron ID: ")
            library.borrow_book(isbn, patron_id)
        
        elif choice == "4":
            isbn = input("Enter book ISBN: ")
            patron_id = input("Enter patron ID: ")
            library.return_book(isbn, patron_id)
        
        elif choice == "5":
            isbn = input("Enter book ISBN: ")
            patron_id = input("Enter patron ID: ")
            library.renew_book(isbn, patron_id)
        
        elif choice == "6":
            isbn = input("Enter book ISBN: ")
            patron_id = input("Enter patron ID: ")
            rating = float(input("Enter rating (1-5): "))
            comment = input("Enter review comment: ")
            library.add_review(isbn, patron_id, rating, comment)
        
        elif choice == "7":
            patron_id = input("Enter patron ID: ")
            amount = float(input("Enter payment amount: "))
            library.pay_fine(patron_id, amount)
        
        elif choice == "8":
            isbn = input("Enter book ISBN: ")
            if isbn in library.books:
                book = library.books[isbn]
                print(f"\nTitle: {book.title}")
                print(f"Author: {book.author}")
                print(f"ISBN: {book.isbn}")
                print(f"Total Copies: {book.total_copies}")
                print(f"Available Copies: {book.available_copies}")
                print(f"Rating: {book.rating:.1f}")
                if book.reviews:
                    print("\nReviews:")
                    for review in book.reviews:
                        print(f"- {review['patron_name']}: {review['rating']}/5")
                        print(f"  {review['comment']}")
            else:
                print("Book not found!")
        
        elif choice == "9":
            patron_id = input("Enter patron ID: ")
            if patron_id in library.patrons:
                patron = library.patrons[patron_id]
                print(f"\nName: {patron.name}")
                print(f"Email: {patron.email}")
                print(f"Status: {patron.status}")
                print(f"Outstanding Fines: ${patron.fines}")
                if patron.borrowed_books:
                    print("\nCurrently Borrowed Books:")
                    for isbn, record in patron.borrowed_books.items():
                        book = library.books[isbn]
                        print(f"- {book.title}")
                        print(f"  Due: {record.due_date.strftime('%Y-%m-%d')}")
            else:
                print("Patron not found!")
        
        elif choice == "10":
            print("Thank you for using the Library Management System!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 