def slice_email(email):
    """Extract username and domain from email address"""
    try:
        # Remove any leading/trailing spaces
        email = email.strip()
        
        # Check for @ symbol
        if '@' not in email:
            return None, None
        
        # Split the email into username and domain
        username, domain = email.split('@')
        
        # Validate username and domain
        if not username or not domain or '.' not in domain:
            return None, None
            
        return username, domain
        
    except Exception:
        return None, None

def validate_email(email):
    """Basic email validation"""
    if not email:
        return False
        
    # Check basic email format
    if not '@' in email or not '.' in email:
        return False
        
    # Check for common invalid characters
    invalid_chars = ' !#$%^&*()=+{}[]|\\/:;"\'<>,?'
    if any(char in email for char in invalid_chars):
        return False
        
    return True

def main():
    print("=== Email Slicer ===")
    
    while True:
        print("\nOptions:")
        print("1. Slice Email")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == '1':
            email = input("\nEnter an email address: ")
            
            if validate_email(email):
                username, domain = slice_email(email)
                if username and domain:
                    print("\nEmail Details:")
                    print(f"Username: {username}")
                    print(f"Domain: {domain}")
                    
                    # Additional domain info
                    domain_parts = domain.split('.')
                    print(f"Domain Name: {domain_parts[0]}")
                    print(f"Top-Level Domain: {'.'.join(domain_parts[1:])}")
                else:
                    print("Invalid email format!")
            else:
                print("Invalid email address!")
                
        elif choice == '2':
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 