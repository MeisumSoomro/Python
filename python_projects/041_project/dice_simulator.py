import random
import time

def roll_dice(num_dice, sides=6):
    """Roll specified number of dice and return results"""
    if num_dice < 1:
        return []
    
    results = []
    for _ in range(num_dice):
        # Simulate rolling animation
        print("Rolling...", end="\r")
        time.sleep(0.5)
        
        # Generate random number
        roll = random.randint(1, sides)
        results.append(roll)
    
    return results

def display_dice_art(value):
    """Display ASCII art for dice values"""
    dice_art = {
        1: ["┌─────────┐",
            "│         │",
            "│    ●    │",
            "│         │",
            "└─────────┘"],
        2: ["┌─────────┐",
            "│  ●      │",
            "│         │",
            "│      ●  │",
            "└─────────┘"],
        3: ["┌─────────┐",
            "│  ●      │",
            "│    ●    │",
            "│      ●  │",
            "└─────────┘"],
        4: ["┌─────────┐",
            "│  ●   ●  │",
            "│         │",
            "│  ●   ●  │",
            "└─────────┘"],
        5: ["┌─────────┐",
            "│  ●   ●  │",
            "│    ●    │",
            "│  ●   ●  │",
            "└─────────┘"],
        6: ["┌─────────┐",
            "│  ●   ●  │",
            "│  ●   ●  │",
            "│  ●   ●  │",
            "└─────────┘"]
    }
    
    return dice_art.get(value, [])

def main():
    print("=== Dice Rolling Simulator ===")
    
    while True:
        print("\nOptions:")
        print("1. Roll Dice")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == '1':
            try:
                num_dice = int(input("\nHow many dice would you like to roll? (1-5): "))
                if 1 <= num_dice <= 5:
                    results = roll_dice(num_dice)
                    
                    print("\nResults:")
                    # Display dice art for each roll
                    for i, value in enumerate(results, 1):
                        print(f"\nDie {i}:")
                        for line in display_dice_art(value):
                            print(line)
                    
                    print(f"\nTotal: {sum(results)}")
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
                
        elif choice == '2':
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 