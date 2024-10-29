from cryptography.fernet import Fernet
from typing import Dict, Optional
import json
from pathlib import Path
import base64
import hashlib
import secrets
import pyperclip
import getpass
import time
from datetime import datetime

class PasswordEncryption:
    def __init__(self, master_password: str):
        # Use master password to derive encryption key
        key = hashlib.sha256(master_password.encode()).digest()
        key_base64 = base64.urlsafe_b64encode(key)
        self.cipher_suite = Fernet(key_base64)
    
    def encrypt(self, password: str) -> bytes:
        return self.cipher_suite.encrypt(password.encode())
    
    def decrypt(self, encrypted_password: bytes) -> str:
        return self.cipher_suite.decrypt(encrypted_password).decode()

class PasswordGenerator:
    def __init__(self):
        self.lowercase = 'abcdefghijklmnopqrstuvwxyz'
        self.uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.numbers = '0123456789'
        self.symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    def generate(self, length: int = 16, use_symbols: bool = True) -> str:
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")
        
        # Always include all character types for strong passwords
        chars = self.lowercase + self.uppercase + self.numbers
        if use_symbols:
            chars += self.symbols
        
        # Ensure at least one character from each required type
        password = [
            secrets.choice(self.lowercase),
            secrets.choice(self.uppercase),
            secrets.choice(self.numbers)
        ]
        if use_symbols:
            password.append(secrets.choice(self.symbols))
        
        # Fill the rest with random characters
        while len(password) < length:
            password.append(secrets.choice(chars))
        
        # Shuffle the password
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        return ''.join(password_list)

class PasswordManager:
    def __init__(self):
        self.file_path = Path("passwords.enc")
        self.passwords: Dict[str, Dict] = {}
        self.encryption: Optional[PasswordEncryption] = None
        self.generator = PasswordGenerator()
        self.master_hash_path = Path("master.hash")
        self.master_hash: Optional[str] = None
        self.load_master_hash()
    
    def load_master_hash(self):
        if self.master_hash_path.exists():
            with open(self.master_hash_path, 'r') as f:
                self.master_hash = f.read().strip()
    
    def verify_master_password(self, password: str) -> bool:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == self.master_hash
    
    def setup_master_password(self, password: str):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with open(self.master_hash_path, 'w') as f:
            f.write(password_hash)
        self.master_hash = password_hash
    
    def initialize(self, master_password: str) -> bool:
        if self.master_hash:
            if not self.verify_master_password(master_password):
                print("Incorrect master password!")
                return False
        else:
            self.setup_master_password(master_password)
        
        self.encryption = PasswordEncryption(master_password)
        self.load_passwords()
        return True
    
    def add_password(self, service: str, username: str, password: str = None):
        if not self.encryption:
            print("Please initialize with master password first!")
            return
        
        if password is None:
            password = self.generator.generate()
        
        encrypted_password = self.encryption.encrypt(password)
        self.passwords[service] = {
            'username': username,
            'password': encrypted_password.decode(),  # Convert bytes to string for JSON storage
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_accessed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_passwords()
        print(f"Password for {service} added successfully!")
        return password
    
    def get_password(self, service: str) -> Optional[str]:
        if not self.encryption:
            print("Please initialize with master password first!")
            return None
        
        if service not in self.passwords:
            print(f"No password found for {service}")
            return None
        
        entry = self.passwords[service]
        decrypted_password = self.encryption.decrypt(entry['password'].encode())
        
        # Update last accessed time
        entry['last_accessed'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_passwords()
        
        return decrypted_password
    
    def list_services(self):
        if not self.passwords:
            print("No passwords stored!")
            return
        
        print("\nStored Passwords:")
        print("-" * 60)
        for service, data in sorted(self.passwords.items()):
            print(f"Service: {service}")
            print(f"Username: {data['username']}")
            print(f"Created: {data['created_at']}")
            print(f"Last Accessed: {data['last_accessed']}")
            print("-" * 30)
    
    def delete_password(self, service: str):
        if service in self.passwords:
            del self.passwords[service]
            self.save_passwords()
            print(f"Password for {service} deleted successfully!")
        else:
            print(f"No password found for {service}")
    
    def save_passwords(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.passwords, f, indent=4)
    
    def load_passwords(self):
        if not self.file_path.exists():
            return
        
        try:
            with open(self.file_path, 'r') as f:
                self.passwords = json.load(f)
        except json.JSONDecodeError:
            print("Error loading passwords file!")
    
    def generate_password(self, length: int = 16, use_symbols: bool = True) -> str:
        return self.generator.generate(length, use_symbols)
    
    def check_password_strength(self, password: str) -> str:
        if len(password) < 8:
            return "Weak: Too short"
        
        score = 0
        checks = [
            (any(c.islower() for c in password), "lowercase"),
            (any(c.isupper() for c in password), "uppercase"),
            (any(c.isdigit() for c in password), "numbers"),
            (any(c in self.generator.symbols for c in password), "symbols")
        ]
        
        passed_checks = [check[1] for check in checks if check[0]]
        score = len(passed_checks)
        
        if score == 4:
            return "Strong"
        elif score == 3:
            return f"Moderate: Missing {[check[1] for check in checks if not check[0]][0]}"
        else:
            return f"Weak: Missing {', '.join([check[1] for check in checks if not check[0]])}"

def main():
    manager = PasswordManager()
    
    # Initial setup or login
    for _ in range(3):  # Give 3 attempts
        master_password = getpass.getpass("Enter master password: ")
        if manager.initialize(master_password):
            break
        if _ == 2:
            print("Too many failed attempts!")
            return
    
    while True:
        print("\nPassword Manager Menu:")
        print("1. Add Password")
        print("2. Get Password")
        print("3. List Services")
        print("4. Generate Password")
        print("5. Delete Password")
        print("6. Check Password Strength")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == "1":
            service = input("Enter service name: ")
            username = input("Enter username: ")
            use_generated = input("Generate password? (y/n): ").lower() == 'y'
            
            if use_generated:
                length = int(input("Enter password length (default 16): ") or "16")
                use_symbols = input("Include symbols? (y/n): ").lower() == 'y'
                password = manager.generate_password(length, use_symbols)
                print(f"Generated password: {password}")
            else:
                password = getpass.getpass("Enter password: ")
            
            manager.add_password(service, username, password)
        
        elif choice == "2":
            service = input("Enter service name: ")
            password = manager.get_password(service)
            if password:
                pyperclip.copy(password)
                print("Password copied to clipboard!")
                print("Clipboard will be cleared in 30 seconds...")
                time.sleep(30)
                pyperclip.copy('')
        
        elif choice == "3":
            manager.list_services()
        
        elif choice == "4":
            length = int(input("Enter password length (default 16): ") or "16")
            use_symbols = input("Include symbols? (y/n): ").lower() == 'y'
            password = manager.generate_password(length, use_symbols)
            print(f"Generated password: {password}")
            if input("Copy to clipboard? (y/n): ").lower() == 'y':
                pyperclip.copy(password)
                print("Password copied to clipboard!")
        
        elif choice == "5":
            service = input("Enter service name: ")
            if input(f"Are you sure you want to delete password for {service}? (y/n): ").lower() == 'y':
                manager.delete_password(service)
        
        elif choice == "6":
            password = getpass.getpass("Enter password to check: ")
            strength = manager.check_password_strength(password)
            print(f"Password Strength: {strength}")
        
        elif choice == "7":
            print("Thank you for using Password Manager!")
            break
        
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 