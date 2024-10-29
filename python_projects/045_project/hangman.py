import random

def get_word():
    """Return a random word"""
    words = ['python', 'programming', 'computer', 'algorithm', 'database',
             'network', 'software', 'developer', 'keyboard', 'internet']
    return random.choice(words)

def display_hangman(tries):
    """Return the hangman ASCII art based on remaining tries"""
    stages = [  # Final state: head, body, both arms, both legs
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |     / \\
                   -
                """,
                # Head, body, both arms, one leg
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |     /
                   -
                """,
                # Head, body, both arms
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |
                   -
                """,
                # Head, body, one arm
                """
                   --------
                   |      |
                   |      O
                   |     \\|
                   |      |
                   |
                   -
                """,
                # Head and body
                """
                   --------
                   |      |
                   |      O
                   |      |
                   |      |
                   |
                   -
                """,
                # Head
                """
                   --------
                   |      |
                   |      O
                   |
                   |
                   |
                   -
                """,
                # Initial empty state
                """
                   --------
                   |      |
                   |
                   |
                   |
                   |
                   -
                """
    ]
    return stages[tries]

def play_game():
    word = get_word()
    word_letters = set(word)  # letters in the word
    alphabet = set('abcdefghijklmnopqrstuvwxyz')
    used_letters = set()  # letters guessed by user

    tries = 6  # number of tries before game over

    # Game loop
    while len(word_letters) > 0 and tries > 0:
        print("\nYou have", tries, "tries left.")
        print("Used letters:", ' '.join(used_letters))

        # What current word looks like
        word_list = [letter if letter in used_letters else '_' for letter in word]
        print(display_hangman(tries))
        print("Current word:", ' '.join(word_list))

        # Getting user input
        guess = input("Guess a letter: ").lower()
        if guess in alphabet - used_letters:
            used_letters.add(guess)
            if guess in word_letters:
                word_letters.remove(guess)
            else:
                tries -= 1
                print("Letter is not in word.")
        elif guess in used_letters:
            print("You already used that letter. Try again.")
        else:
            print("Invalid character. Please enter a letter.")

    # Game ended
    if tries == 0:
        print(display_hangman(0))
        print("Sorry, you died. The word was", word)
    else:
        print("Congratulations! You guessed the word", word, "!!")

def main():
    print("=== Hangman Game ===")
    
    while True:
        play_game()
        if input("\nPlay again? (y/n): ").lower() != 'y':
            print("\nThanks for playing!")
            break

if __name__ == "__main__":
    main() 