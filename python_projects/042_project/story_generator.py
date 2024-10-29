import random

def get_story_elements():
    """Return dictionaries of story elements"""
    characters = [
        "a brave knight", "a clever wizard", "a mysterious traveler",
        "a young farmer", "an ancient dragon", "a wise old woman",
        "a mischievous child", "a talking animal"
    ]
    
    locations = [
        "in a dark forest", "atop a mountain", "in an ancient castle",
        "by the sea shore", "in a busy marketplace", "in a magical garden",
        "inside a cave", "on a floating island"
    ]
    
    objects = [
        "a magical sword", "an ancient book", "a mysterious map",
        "a golden key", "a crystal ball", "a magical ring",
        "a lost treasure", "an enchanted mirror"
    ]
    
    problems = [
        "had to solve a riddle", "needed to break a curse",
        "had to find a lost artifact", "needed to save a village",
        "had to defeat a monster", "needed to cross a dangerous path",
        "had to make peace between rivals", "needed to discover a secret"
    ]
    
    solutions = [
        "with the help of new friends", "using clever thinking",
        "through acts of kindness", "with ancient magic",
        "by showing great courage", "through cooperation",
        "by learning an important lesson", "with determination"
    ]
    
    return characters, locations, objects, problems, solutions

def generate_story():
    """Generate a random story from elements"""
    chars, locs, objs, probs, sols = get_story_elements()
    
    story = f"""
    Once upon a time, {random.choice(chars)} lived {random.choice(locs)}.
    One day, they discovered {random.choice(objs)} and {random.choice(probs)}.
    In the end, they succeeded {random.choice(sols)}.
    """
    return story

def generate_custom_story():
    """Generate a story with user-chosen elements"""
    chars, locs, objs, probs, sols = get_story_elements()
    
    print("\nChoose your story elements:")
    
    print("\nCharacters:")
    for i, char in enumerate(chars, 1):
        print(f"{i}. {char}")
    char_choice = chars[int(input("Choose a character (enter number): ")) - 1]
    
    print("\nLocations:")
    for i, loc in enumerate(locs, 1):
        print(f"{i}. {loc}")
    loc_choice = locs[int(input("Choose a location (enter number): ")) - 1]
    
    print("\nObjects:")
    for i, obj in enumerate(objs, 1):
        print(f"{i}. {obj}")
    obj_choice = objs[int(input("Choose an object (enter number): ")) - 1]
    
    story = f"""
    Once upon a time, {char_choice} lived {loc_choice}.
    One day, they discovered {obj_choice} and {random.choice(probs)}.
    In the end, they succeeded {random.choice(sols)}.
    """
    return story

def main():
    print("=== Story Generator ===")
    
    while True:
        print("\nOptions:")
        print("1. Generate Random Story")
        print("2. Create Custom Story")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            story = generate_story()
            print("\nYour Story:", story)
            
        elif choice == '2':
            try:
                story = generate_custom_story()
                print("\nYour Story:", story)
            except (ValueError, IndexError):
                print("Invalid input! Please enter valid numbers.")
                
        elif choice == '3':
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 