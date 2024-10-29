def get_morse_dict():
    """Returns dictionary of Morse code patterns"""
    return {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
        'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
        '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
        '0': '-----', ' ': ' '
    }

def text_to_morse(text):
    """Convert text to Morse code"""
    morse_dict = get_morse_dict()
    morse = ''
    
    for char in text.upper():
        if char in morse_dict:
            morse += morse_dict[char] + ' '
        else:
            morse += char + ' '
    return morse.strip()

def morse_to_text(morse):
    """Convert Morse code to text"""
    morse_dict = {v: k for k, v in get_morse_dict().items()}
    text = ''
    
    for code in morse.split():
        if code in morse_dict:
            text += morse_dict[code]
        else:
            text += code
    return text

def main():
    print("=== Morse Code Translator ===")
    
    while True:
        print("\nOptions:")
        print("1. Text to Morse Code")
        print("2. Morse Code to Text")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            text = input("\nEnter text to convert: ")
            morse = text_to_morse(text)
            print(f"Morse Code: {morse}")
            
        elif choice == '2':
            morse = input("\nEnter Morse code (use spaces between letters): ")
            text = morse_to_text(morse)
            print(f"Text: {text}")
            
        elif choice == '3':
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 