def decimal_to_binary(decimal_num):
    """Convert decimal to binary"""
    if decimal_num == 0:
        return "0"
    binary = ""
    num = abs(decimal_num)
    while num > 0:
        binary = str(num % 2) + binary
        num //= 2
    if decimal_num < 0:
        binary = "-" + binary
    return binary

def decimal_to_hex(decimal_num):
    """Convert decimal to hexadecimal"""
    hex_chars = "0123456789ABCDEF"
    if decimal_num == 0:
        return "0"
    hex_num = ""
    num = abs(decimal_num)
    while num > 0:
        hex_num = hex_chars[num % 16] + hex_num
        num //= 16
    if decimal_num < 0:
        hex_num = "-" + hex_num
    return hex_num

def binary_to_decimal(binary_str):
    """Convert binary to decimal"""
    try:
        # Handle negative numbers
        if binary_str.startswith('-'):
            return -int(binary_str[1:], 2)
        return int(binary_str, 2)
    except ValueError:
        return None

def hex_to_decimal(hex_str):
    """Convert hexadecimal to decimal"""
    try:
        # Handle negative numbers
        if hex_str.startswith('-'):
            return -int(hex_str[1:], 16)
        return int(hex_str, 16)
    except ValueError:
        return None

def main():
    print("=== Number System Converter ===")
    
    while True:
        print("\nOptions:")
        print("1. Decimal to Binary")
        print("2. Decimal to Hexadecimal")
        print("3. Binary to Decimal")
        print("4. Hexadecimal to Decimal")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            try:
                num = int(input("\nEnter decimal number: "))
                print(f"Binary: {decimal_to_binary(num)}")
            except ValueError:
                print("Invalid input! Please enter a valid decimal number.")
                
        elif choice == '2':
            try:
                num = int(input("\nEnter decimal number: "))
                print(f"Hexadecimal: {decimal_to_hex(num)}")
            except ValueError:
                print("Invalid input! Please enter a valid decimal number.")
                
        elif choice == '3':
            binary = input("\nEnter binary number: ")
            result = binary_to_decimal(binary)
            if result is not None:
                print(f"Decimal: {result}")
            else:
                print("Invalid binary number!")
                
        elif choice == '4':
            hex_num = input("\nEnter hexadecimal number: ")
            result = hex_to_decimal(hex_num)
            if result is not None:
                print(f"Decimal: {result}")
            else:
                print("Invalid hexadecimal number!")
                
        elif choice == '5':
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 