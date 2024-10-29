import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class DataAnalyzer:
    def __init__(self):
        self.data = None
        
    def load_data(self, file_path):
        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                self.data = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")
            return True
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
            
    def show_basic_info(self):
        if self.data is None:
            return "No data loaded"
            
        info = {
            "Number of rows": len(self.data),
            "Number of columns": len(self.data.columns),
            "Column names": list(self.data.columns),
            "Data types": self.data.dtypes.to_dict(),
            "Missing values": self.data.isnull().sum().to_dict()
        }
        return info
        
    def generate_summary_stats(self):
        if self.data is None:
            return "No data loaded"
            
        return self.data.describe()
        
    def plot_histogram(self, column):
        if self.data is None:
            return "No data loaded"
            
        plt.figure(figsize=(10, 6))
        plt.hist(self.data[column].dropna(), bins=30)
        plt.title(f'Histogram of {column}')
        plt.xlabel(column)
        plt.ylabel('Frequency')
        plt.show()
        
    def plot_correlation_matrix(self):
        if self.data is None:
            return "No data loaded"
            
        numeric_data = self.data.select_dtypes(include=['float64', 'int64'])
        plt.figure(figsize=(12, 8))
        sns.heatmap(numeric_data.corr(), annot=True, cmap='coolwarm')
        plt.title('Correlation Matrix')
        plt.show()

def main():
    analyzer = DataAnalyzer()
    
    print("Welcome to Data Analyzer!")
    print("\nThis program can analyze CSV and Excel files.")
    
    while True:
        file_path = input("\nEnter path to data file (CSV or Excel): ")
        if analyzer.load_data(file_path):
            while True:
                print("\n1. Show basic information")
                print("2. Generate summary statistics")
                print("3. Plot histogram")
                print("4. Plot correlation matrix")
                print("5. Load different file")
                print("6. Exit")
                
                choice = input("\nEnter your choice (1-6): ")
                
                if choice == '1':
                    print("\nBasic Information:")
                    print(analyzer.show_basic_info())
                elif choice == '2':
                    print("\nSummary Statistics:")
                    print(analyzer.generate_summary_stats())
                elif choice == '3':
                    column = input("Enter column name for histogram: ")
                    if column in analyzer.data.columns:
                        analyzer.plot_histogram(column)
                    else:
                        print("Column not found!")
                elif choice == '4':
                    analyzer.plot_correlation_matrix()
                elif choice == '5':
                    break
                elif choice == '6':
                    return
                else:
                    print("Invalid choice!")
        
        if input("\nAnalyze another file? (y/n): ").lower() != 'y':
            break

if __name__ == "__main__":
    main() 