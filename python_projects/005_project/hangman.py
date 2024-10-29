import random
import string

def get_word():
    words = ['python', 'programming', 'computer', 'algorithm', 'database', 'network']
    return random.choice(words)

def display_hangman(tries):
    stages = [  # final state: head, torso, both arms, and both legs
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |     / \\
                   -
                """,
                # head, torso, both arms, and one leg
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |     /
                   -
                """,
                # head, torso, and both arms
                """
                   --------
                   |      |
                   |      O
                   |     \\|/
                   |      |
                   |
                   -
                """,
                # head, torso, and one arm
                """
                   --------
                   |      |
                   |      O
                   |     \\|
                   |      |
                   |
                   -
                """,
                # head and torso
                """
                   --------
                   |      |
                   |      O
                   |      |
                   |      |
                   |
                   -
                """,
                # head
                """
                   --------
                   |      |
                   |      O
                   |
                   |
                   |
                   -
                """,
                # initial empty state
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

def play_hangman():
    word = get_word()
    word_letters = set(word)  # letters in the word
    alphabet = set(string.ascii_lowercase)
    used_letters = set()  # letters guessed by the user
    
    tries = 6  # number of tries before game over
    
    # getting user input
    while len(word_letters) > 0 and tries > 0:
        print(f'\nYou have {tries} tries left.')
        print('Used letters:', ' '.join(used_letters))
        
        # what current word is (ie W - R D)
        word_list = [letter if letter in used_letters else '-' for letter in word]
        print(display_hangman(tries))
        print('Current word:', ' '.join(word_list))
        
        guess = input('Guess a letter: ').lower()
        if guess in alphabet - used_letters:
            used_letters.add(guess)
            if guess in word_letters:
                word_letters.remove(guess)
            else:
                tries -= 1
                print('Letter is not in the word.')
                
        elif guess in used_letters:
            print('You have already used that letter. Please try again.')
            
        else:
            print('Invalid character. Please try again.')
    
    if tries == 0:
        print(display_hangman(0))
        print(f'Sorry, you died. The word was {word}')
    else:
        print(f'Congratulations! You guessed the word {word}!!')

if __name__ == '__main__':
    play_hangman() 