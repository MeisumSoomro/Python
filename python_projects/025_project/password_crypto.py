from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class PasswordCrypto:
    def __init__(self):
        self.salt = self._load_or_create_salt()
        self.key = None
        self.cipher_suite = None
        
    def _load_or_create_salt(self):
        """Load existing salt or create a new one"""
        if os.path.exists('crypto.salt'):
            with open('crypto.salt', 'rb') as f:
                return f.read()
        else:
            salt = os.urandom(16)
            with open('crypto.salt', 'wb') as f:
                f.write(salt)
            return salt
            
    def _derive_key(self, password):
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
        
    def set_master_password(self, password):
        """Set up master password and save its hash"""
        self.key = self._derive_key(password)
        self.cipher_suite = Fernet(self.key)
        
        # Save password hash
        password_hash = self.encrypt(password)
        with open('master_password.hash', 'wb') as f:
            f.write(password_hash)
            
    def verify_master_password(self, password):
        """Verify if the entered password matches the master password"""
        try:
            self.key = self._derive_key(password)
            self.cipher_suite = Fernet(self.key)
            
            with open('master_password.hash', 'rb') as f:
                stored_hash = f.read()
                
            decrypted = self.decrypt(stored_hash)
            return decrypted == password
        except Exception:
            return False
            
    def change_master_password(self, new_password):
        """Change master password and re-encrypt all passwords"""
        # TODO: Implement re-encryption of all stored passwords
        self.set_master_password(new_password)
        
    def encrypt(self, text):
        """Encrypt a string"""
        if not self.cipher_suite:
            raise Exception("Encryption key not initialized")
        return self.cipher_suite.encrypt(text.encode())
        
    def decrypt(self, encrypted_data):
        """Decrypt encrypted data"""
        if not self.cipher_suite:
            raise Exception("Encryption key not initialized")
        return self.cipher_suite.decrypt(encrypted_data).decode() 