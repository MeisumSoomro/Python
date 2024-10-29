import random
import string

def generate_password(length=12, use_letters=True, use_numbers=True, use_symbols=True):
    """Generate a random password based on user preferences"""
    # Define character sets
    letters = string.ascii_letters
    numbers = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Create the character pool based on user preferences
    char_pool = ""
    if use_letters:
        char_pool += letters
    if use_numbers:
        char_pool += numbers
    if use_symbols:
        char_pool += symbols
    
    # Ensure at least one option is selected
    if not char_pool:
        print("Error: At least one character type must be selected!")
        return None
    
    # Generate password
    password = ''.join(random.choice(char_pool) for _ in range(length))
    return password

def main():
    print("=== Password Generator ===")
    
    while True:
        print("\nOptions:")
        print("1. Generate Password")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == "1":
            # Get user preferences
            length = input("Enter password length (default is 12): ").strip()
            length = int(length) if length.isdigit() else 12
            
            use_letters = input("Include letters? (y/n): ").lower() == 'y'
            use_numbers = input("Include numbers? (y/n): ").lower() == 'y'
            use_symbols = input("Include symbols? (y/n): ").lower() == 'y'
            
            # Generate and display password
            password = generate_password(length, use_letters, use_numbers, use_symbols)
            if password:
                print(f"\nGenerated Password: {password}")
            
        elif choice == "2":
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 