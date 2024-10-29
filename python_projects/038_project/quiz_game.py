def load_questions():
    """Returns a dictionary of questions and their answers"""
    return {
        "What is the capital of France?": "Paris",
        "Which planet is known as the Red Planet?": "Mars",
        "What is 2 + 2?": "4",
        "Who painted the Mona Lisa?": "Leonardo da Vinci",
        "What is the largest mammal in the world?": "Blue Whale"
    }

def play_quiz():
    """Main quiz game function"""
    questions = load_questions()
    score = 0
    total_questions = len(questions)
    
    print("\nWelcome to the Quiz Game!")
    print("Type your answer for each question.\n")
    
    for question, correct_answer in questions.items():
        print(question)
        user_answer = input("Your answer: ").strip()
        
        if user_answer.lower() == correct_answer.lower():
            print("Correct!")
            score += 1
        else:
            print(f"Sorry, the correct answer was: {correct_answer}")
        print()  # Empty line for readability
    
    print(f"Game Over! You scored {score} out of {total_questions}")
    percentage = (score / total_questions) * 100
    print(f"Percentage: {percentage}%")

def main():
    while True:
        play_quiz()
        play_again = input("\nWould you like to play again? (yes/no): ").lower()
        if play_again != 'yes':
            print("Thanks for playing! Goodbye!")
            break

if __name__ == "__main__":
    main() 