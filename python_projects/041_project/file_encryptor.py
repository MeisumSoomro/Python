def encrypt_text(text, shift=3):
    """Simple Caesar cipher encryption"""
    encrypted = ""
    for char in text:
        if char.isalpha():
            # Determine the case and base ASCII value
            ascii_base = ord('A') if char.isupper() else ord('a')
            # Shift the character and wrap around if necessary
            shifted = (ord(char) - ascii_base + shift) % 26
            encrypted += chr(ascii_base + shifted)
        else:
            encrypted += char
    return encrypted

def decrypt_text(text, shift=3):
    """Decrypt by shifting in opposite direction"""
    return encrypt_text(text, shift=-shift)

def process_file(input_file, output_file, encrypt=True):
    """Process the input file and write to output file"""
    try:
        with open(input_file, 'r') as file:
            text = file.read()
        
        # Perform encryption or decryption
        processed_text = encrypt_text(text) if encrypt else decrypt_text(text)
        
        with open(output_file, 'w') as file:
            file.write(processed_text)
        return True
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found!")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

def main():
    print("=== File Encryptor/Decryptor ===")
    
    while True:
        print("\nOptions:")
        print("1. Encrypt a file")
        print("2. Decrypt a file")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice in ['1', '2']:
            input_file = input("Enter input file path: ")
            output_file = input("Enter output file path: ")
            
            if choice == '1':
                if process_file(input_file, output_file, encrypt=True):
                    print("File encrypted successfully!")
            else:
                if process_file(input_file, output_file, encrypt=False):
                    print("File decrypted successfully!")
                    
        elif choice == '3':
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 