import random
import string

def generate_password(length=12, use_letters=True, use_numbers=True, use_symbols=True):
    # Define character sets
    letters = string.ascii_letters if use_letters else ''
    numbers = string.digits if use_numbers else ''
    symbols = string.punctuation if use_symbols else ''
    
    # Combine all allowed characters
    all_characters = letters + numbers + symbols
    
    if not all_characters:
        return "Error: At least one character type must be selected"
    
    # Generate password
    password = ''.join(random.choice(all_characters) for _ in range(length))
    return password

def main():
    print("Welcome to Password Generator!")
    
    while True:
        try:
            length = int(input("Enter password length (8-50): "))
            if not 8 <= length <= 50:
                print("Password length must be between 8 and 50")
                continue
                
            use_letters = input("Include letters? (y/n): ").lower() == 'y'
            use_numbers = input("Include numbers? (y/n): ").lower() == 'y'
            use_symbols = input("Include symbols? (y/n): ").lower() == 'y'
            
            password = generate_password(length, use_letters, use_numbers, use_symbols)
            print(f"\nGenerated Password: {password}")
            
            if input("\nGenerate another password? (y/n): ").lower() != 'y':
                break
                
        except ValueError:
            print("Please enter valid numbers!")

if __name__ == "__main__":
    main() 