import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sales_data():
    """Generate sample sales data"""
    np.random.seed(42)
    
    # Generate dates for one year
    dates = [datetime(2023, 1, 1) + timedelta(days=x) for x in range(365)]
    
    # Generate sales data
    data = {
        'Date': dates,
        'Sales': np.random.normal(1000, 200, 365),  # Daily sales with normal distribution
        'Units': np.random.randint(50, 150, 365),   # Units sold
        'Region': np.random.choice(['North', 'South', 'East', 'West'], 365),
        'Product': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], 365),
        'Customer_Satisfaction': np.random.uniform(3.5, 5.0, 365)
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some calculated columns
    df['Revenue'] = df['Sales'] * df['Units']
    df['Month'] = df['Date'].dt.month
    df['Day_of_Week'] = df['Date'].dt.day_name()
    
    # Save to CSV
    df.to_csv('sample_sales_data.csv', index=False)
    return "sample_sales_data.csv"

def generate_weather_data():
    """Generate sample weather data"""
    np.random.seed(42)
    
    # Generate dates for one year
    dates = [datetime(2023, 1, 1) + timedelta(days=x) for x in range(365)]
    
    # Generate weather data
    data = {
        'Date': dates,
        'Temperature': np.random.normal(20, 8, 365),  # Temperature in Celsius
        'Humidity': np.random.uniform(30, 90, 365),   # Humidity percentage
        'Rainfall': np.random.exponential(2, 365),    # Rainfall in mm
        'Wind_Speed': np.random.rayleigh(5, 365),     # Wind speed in km/h
        'Cloud_Cover': np.random.uniform(0, 100, 365) # Cloud cover percentage
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some calculated columns
    df['Month'] = df['Date'].dt.month
    df['Season'] = pd.cut(df['Month'], 
                         bins=[0, 3, 6, 9, 12], 
                         labels=['Winter', 'Spring', 'Summer', 'Fall'])
    
    # Save to CSV
    df.to_csv('sample_weather_data.csv', index=False)
    return "sample_weather_data.csv"

def generate_student_data():
    """Generate sample student performance data"""
    np.random.seed(42)
    
    n_students = 200
    
    data = {
        'Student_ID': range(1, n_students + 1),
        'Math_Score': np.random.normal(75, 15, n_students),
        'Science_Score': np.random.normal(72, 18, n_students),
        'English_Score': np.random.normal(70, 12, n_students),
        'Study_Hours': np.random.normal(6, 2, n_students),
        'Attendance': np.random.uniform(70, 100, n_students)
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add calculated columns
    df['Average_Score'] = df[['Math_Score', 'Science_Score', 'English_Score']].mean(axis=1)
    df['Performance_Category'] = pd.qcut(df['Average_Score'], 
                                       q=4, 
                                       labels=['Poor', 'Fair', 'Good', 'Excellent'])
    
    # Save to CSV
    df.to_csv('sample_student_data.csv', index=False)
    return "sample_student_data.csv"

def main():
    """Generate all test data files"""
    files_generated = []
    files_generated.append(generate_sales_data())
    files_generated.append(generate_weather_data())
    files_generated.append(generate_student_data())
    
    print("Generated test data files:")
    for file in files_generated:
        print(f"- {file}")

if __name__ == "__main__":
    main() 