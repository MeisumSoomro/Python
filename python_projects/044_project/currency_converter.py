def get_exchange_rates():
    """Return a dictionary of fixed exchange rates (relative to USD)"""
    return {
        'USD': 1.00,    # US Dollar (base currency)
        'EUR': 0.85,    # Euro
        'GBP': 0.73,    # British Pound
        'JPY': 110.0,   # Japanese Yen
        'AUD': 1.35,    # Australian Dollar
        'CAD': 1.25,    # Canadian Dollar
        'INR': 74.5     # Indian Rupee
    }

def show_currencies(rates):
    """Display available currencies"""
    print("\nAvailable currencies:")
    for currency in rates.keys():
        print(f"- {currency}")

def convert_currency(amount, from_currency, to_currency, rates):
    """Convert amount from one currency to another"""
    if from_currency not in rates or to_currency not in rates:
        return None
        
    # Convert to USD first (if not already USD)
    usd_amount = amount / rates[from_currency]
    
    # Convert from USD to target currency
    final_amount = usd_amount * rates[to_currency]
    return round(final_amount, 2)

def main():
    print("=== Currency Converter ===")
    rates = get_exchange_rates()
    
    while True:
        print("\nOptions:")
        print("1. Convert Currency")
        print("2. Show Available Currencies")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            try:
                show_currencies(rates)
                from_currency = input("\nEnter source currency code: ").upper()
                to_currency = input("Enter target currency code: ").upper()
                amount = float(input("Enter amount: "))
                
                result = convert_currency(amount, from_currency, to_currency, rates)
                if result is not None:
                    print(f"\n{amount} {from_currency} = {result} {to_currency}")
                else:
                    print("Invalid currency codes!")
                    
            except ValueError:
                print("Invalid amount! Please enter a number.")
                
        elif choice == '2':
            show_currencies(rates)
            
        elif choice == '3':
            print("\nGoodbye!")
            break
            
        else:
            print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main() 