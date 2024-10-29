import re

class ContactValidator:
    def validate_phone(self, phone):
        """Validate phone number format."""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, phone))

    def validate_email(self, email):
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def validate_name(self, name):
        """Validate contact name."""
        return bool(name.strip()) 