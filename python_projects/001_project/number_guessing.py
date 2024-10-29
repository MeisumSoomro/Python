import random

def number_guessing_game():
    # Generate a random number between 1 and 100
    number = random.randint(1, 100)
    attempts = 0
    max_attempts = 10
    
    print("Welcome to the Number Guessing Game!")
    print(f"I'm thinking of a number between 1 and 100. You have {max_attempts} attempts.")
    
    while attempts < max_attempts:
        try:
            # Get the player's guess
            guess = int(input("Enter your guess: "))
            attempts += 1
            
            # Check the guess
            if guess < number:
                print("Too low!")
            elif guess > number:
                print("Too high!")
            else:
                print(f"Congratulations! You guessed the number in {attempts} attempts!")
                return
                
            # Inform player of remaining attempts
            print(f"Attempts remaining: {max_attempts - attempts}")
            
        except ValueError:
            print("Please enter a valid number!")
            
    print(f"Game Over! The number was {number}")

if __name__ == "__main__":
    number_guessing_game() 