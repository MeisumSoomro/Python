import random
import string
import re

class PasswordGenerator:
    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
    def generate_password(self, length=12, uppercase=True, numbers=True, symbols=True):
        """Generate a random password with specified characteristics"""
        # Start with lowercase letters
        characters = self.lowercase
        
        # Add other character types if requested
        if uppercase:
            characters += self.uppercase
        if numbers:
            characters += self.digits
        if symbols:
            characters += self.symbols
            
        # Generate password
        password = []
        
        # Ensure at least one character of each type if requested
        if uppercase:
            password.append(random.choice(self.uppercase))
        if numbers:
            password.append(random.choice(self.digits))
        if symbols:
            password.append(random.choice(self.symbols))
            
        # Fill the rest with random characters
        while len(password) < length:
            password.append(random.choice(characters))
            
        # Shuffle the password
        random.shuffle(password)
        return ''.join(password)
        
    def check_password_strength(self, password):
        """Check password strength and return a score and feedback"""
        score = 0
        feedback = []
        
        # Length check
        if len(password) < 8:
            feedback.append("Password is too short")
        elif len(password) >= 12:
            score += 2
            feedback.append("Good length")
        else:
            score += 1
            
        # Character type checks
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("Add uppercase letters")
            
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("Add lowercase letters")
            
        if re.search(r'\d', password):
            score += 1
        else:
            feedback.append("Add numbers")
            
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 1
        else:
            feedback.append("Add special characters")
            
        # Complexity bonus
        if score >= 4 and len(password) >= 12:
            score += 1
            feedback.append("Excellent password!")
        elif not feedback:
            feedback.append("Good password!")
            
        return {
            'score': score,
            'feedback': '\n'.join(feedback) if feedback else "Strong password!"
        } 