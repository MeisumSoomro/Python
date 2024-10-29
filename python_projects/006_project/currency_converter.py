import requests
from datetime import datetime

class CurrencyConverter:
    def __init__(self):
        self.rates = {}
        self.update_rates()
        
    def update_rates(self):
        try:
            # Using exchangerate-api.com (you should replace with your API key)
            response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
            self.rates = response.json()['rates']
            self.rates['USD'] = 1.0
        except:
            print("Error updating rates. Using default USD rate.")
            self.rates = {'USD': 1.0}
            
    def convert(self, amount, from_currency, to_currency):
        if from_currency not in self.rates or to_currency not in self.rates:
            return None
            
        # Convert to USD first (base currency)
        usd_amount = amount / self.rates[from_currency]
        # Convert from USD to target currency
        final_amount = usd_amount * self.rates[to_currency]
        
        return round(final_amount, 2)

def main():
    converter = CurrencyConverter()
    
    print("Welcome to Currency Converter!")
    print("\nAvailable currencies:", ', '.join(converter.rates.keys()))
    
    while True:
        try:
            amount = float(input("\nEnter amount: "))
            from_currency = input("From Currency (e.g., USD): ").upper()
            to_currency = input("To Currency (e.g., EUR): ").upper()
            
            result = converter.convert(amount, from_currency, to_currency)
            
            if result is not None:
                print(f"\n{amount} {from_currency} = {result} {to_currency}")
            else:
                print("Invalid currency codes!")
                
            if input("\nConvert another amount? (y/n): ").lower() != 'y':
                break
                
        except ValueError:
            print("Please enter a valid number for the amount!")

if __name__ == "__main__":
    main() 