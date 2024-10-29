import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contact_book import Contact, ContactBook

class TestContact(unittest.TestCase):
    def setUp(self):
        self.contact = Contact("John Doe", "+1234567890", "john@example.com", "123 Main St")

    def test_contact_creation(self):
        self.assertEqual(self.contact.name, "John Doe")
        self.assertEqual(self.contact.phone, "+1234567890")
        self.assertEqual(self.contact.email, "john@example.com")
        self.assertEqual(self.contact.address, "123 Main St")

class TestContactBook(unittest.TestCase):
    def setUp(self):
        self.contact_book = ContactBook()

    def test_validate_phone(self):
        self.assertTrue(self.contact_book.validate_phone("+1234567890"))
        self.assertTrue(self.contact_book.validate_phone("1234567890"))
        self.assertFalse(self.contact_book.validate_phone("123"))
        self.assertFalse(self.contact_book.validate_phone("abc"))

    def test_validate_email(self):
        self.assertTrue(self.contact_book.validate_email("test@example.com"))
        self.assertFalse(self.contact_book.validate_email("invalid_email"))

if __name__ == '__main__':
    unittest.main() 