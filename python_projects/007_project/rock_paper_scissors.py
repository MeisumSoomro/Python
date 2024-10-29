import random

def get_user_choice():
    while True:
        choice = input("Enter your choice (rock/paper/scissors): ").lower()
        if choice in ['rock', 'paper', 'scissors']:
            return choice
        print("Invalid choice! Please try again.")

def get_computer_choice():
    return random.choice(['rock', 'paper', 'scissors'])

def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "Tie!"
        
    winning_combinations = {
        'rock': 'scissors',
        'paper': 'rock',
        'scissors': 'paper'
    }
    
    if winning_combinations[user_choice] == computer_choice:
        return "You win!"
    return "Computer wins!"

def play_game():
    print("Welcome to Rock, Paper, Scissors!")
    
    scores = {'user': 0, 'computer': 0, 'ties': 0}
    
    while True:
        user_choice = get_user_choice()
        computer_choice = get_computer_choice()
        
        print(f"\nYou chose: {user_choice}")
        print(f"Computer chose: {computer_choice}")
        
        result = determine_winner(user_choice, computer_choice)
        print(result)
        
        if result == "You win!":
            scores['user'] += 1
        elif result == "Computer wins!":
            scores['computer'] += 1
        else:
            scores['ties'] += 1
            
        print(f"\nScores - You: {scores['user']}, Computer: {scores['computer']}, Ties: {scores['ties']}")
        
        if input("\nPlay again? (y/n): ").lower() != 'y':
            break
            
    print("\nFinal Scores:")
    print(f"You: {scores['user']}")
    print(f"Computer: {scores['computer']}")
    print(f"Ties: {scores['ties']}")

if __name__ == "__main__":
    play_game() 