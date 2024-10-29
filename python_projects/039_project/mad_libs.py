def get_word(word_type):
    """Get input word from user"""
    return input(f"Enter a {word_type}: ")

def story1():
    """Create a funny story with user inputs"""
    # Get words from user
    adjective1 = get_word("adjective")
    noun1 = get_word("noun")
    verb_past = get_word("verb (past tense)")
    adverb = get_word("adverb")
    adjective2 = get_word("adjective")
    noun2 = get_word("noun")
    verb = get_word("verb")
    
    # Create the story
    story = f"""
    The {adjective1} {noun1} {verb_past} {adverb} through the forest.
    Suddenly, a {adjective2} {noun2} appeared and started to {verb}!
    """
    return story

def story2():
    """Create another funny story with different inputs"""
    # Get words from user
    name = get_word("name")
    place = get_word("place")
    verb = get_word("verb")
    food = get_word("food")
    adjective = get_word("adjective")
    
    # Create the story
    story = f"""
    Once upon a time, {name} went to {place} to {verb}.
    While there, they found a magical {food} that made them feel {adjective}!
    """
    return story

def main():
    print("=== Mad Libs Generator ===")
    
    while True:
        print("\nOptions:")
        print("1. Forest Adventure Story")
        print("2. Magical Journey Story")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            print("\nLet's create a forest adventure!")
            story = story1()
            print("\nHere's your story:", story)
            
        elif choice == '2':
            print("\nLet's create a magical journey!")
            story = story2()
            print("\nHere's your story:", story)
            
        elif choice == '3':
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 