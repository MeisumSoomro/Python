def calculator():
    print("Simple Calculator")
    print("Operations: +, -, *, /")
    
    while True:
        try:
            # Get input from user
            num1 = float(input("Enter first number: "))
            operator = input("Enter operator: ")
            num2 = float(input("Enter second number: "))
            
            # Perform calculation based on operator
            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*':
                result = num1 * num2
            elif operator == '/':
                if num2 == 0:
                    print("Error: Division by zero!")
                    continue
                result = num1 / num2
            else:
                print("Invalid operator!")
                continue
                
            print(f"Result: {result}")
            
            # Ask if user wants to continue
            if input("Calculate again? (y/n): ").lower() != 'y':
                break
                
        except ValueError:
            print("Please enter valid numbers!")
            
if __name__ == "__main__":
    calculator() 