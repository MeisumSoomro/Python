import unittest
import os
from datetime import datetime
import tkinter as tk
from password_manager import PasswordManager
from password_crypto import PasswordCrypto
from password_generator import PasswordGenerator

class TestPasswordManager(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = PasswordManager(self.root)
        
    def tearDown(self):
        self.root.destroy()
        # Clean up test files
        test_files = ['passwords.enc', 'master_password.hash', 'crypto.salt']
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
                
    def test_password_encryption(self):
        crypto = PasswordCrypto()
        test_password = "TestPassword123!"
        
        # Test master password setup
        crypto.set_master_password(test_password)
        self.assertTrue(crypto.verify_master_password(test_password))
        self.assertFalse(crypto.verify_master_password("WrongPassword"))
        
        # Test password encryption/decryption
        encrypted = crypto.encrypt("SecretPassword")
        decrypted = crypto.decrypt(encrypted)
        self.assertEqual(decrypted, "SecretPassword")
        
    def test_password_generator(self):
        generator = PasswordGenerator()
        
        # Test password generation
        password = generator.generate_password(
            length=12,
            uppercase=True,
            numbers=True,
            symbols=True
        )
        
        self.assertEqual(len(password), 12)
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(any(not c.isalnum() for c in password))
        
        # Test password strength checker
        strength = generator.check_password_strength(password)
        self.assertGreaterEqual(strength['score'], 4)
        
if __name__ == '__main__':
    try:
        import cryptography
        unittest.main()
    except ImportError as e:
        print("Error: Missing required dependencies.")
        print("Please install required packages using:")
        print("pip install -r requirements.txt")
        exit(1) 