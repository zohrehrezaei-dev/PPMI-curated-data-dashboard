import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Simplified version without Streamlit for now
print("🧠 Parkinson's Disease Dataset Dashboard - Basic Version")
print("=" * 50)

def load_excel_data(file_path):
    """Simple function to load Excel data"""
    try:
        # Read Excel file and get sheet names
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        print(f"Found sheets: {', '.join(sheet_names)}")
        
        # Load first sheet as main data
        main_data = pd.read_excel(file_path, sheet_name=sheet_names[0])
        print(f"✅ Loaded data from sheet: {sheet_names[0]}")
        print(f"Data shape: {main_data.shape}")
        
        return main_data
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return None

def analyze_data(data):
    """Basic data analysis"""
    if data is None:
        return
    
    print(f"\n📊 Dataset Overview:")
    print(f"- Total Records: {len(data)}")
    print(f"- Total Variables: {len(data.columns)}")
    print(f"- Missing Values: {data.isnull().sum().sum()}")
    
    print(f"\n📋 Column Names:")
    for i, col in enumerate(data.columns[:10], 1):  # Show first 10 columns
        print(f"  {i}. {col}")
    if len(data.columns) > 10:
        print(f"  ... and {len(data.columns) - 10} more columns")
    
    print(f"\n📈 Data Types:")
    print(data.dtypes.value_counts())
    
    # Look for Parkinson's related variables
    parkinson_keywords = ['parkinson', 'pd', 'motor', 'tremor', 'updrs', 'hoehn', 'yahr']
    relevant_cols = []
    
    for col in data.columns:
        col_lower = col.lower()
        for keyword in parkinson_keywords:
            if keyword in col_lower:
                relevant_cols.append(col)
                break
    
    if relevant_cols:
        print(f"\n🧠 Potential Parkinson's-related variables found:")
        for col in relevant_cols:
            print(f"  - {col}")
    else:
        print(f"\n🧠 No obvious Parkinson's-related variables found in column names")

if __name__ == "__main__":
    print("This is a basic version of the dashboard.")
    print("To use the full web interface, you need to install Streamlit.")
    print("\nTo test with your data, modify this script to point to your Excel file.")
    
    # Example usage (uncomment and modify path):
    # data = load_excel_data("path/to/your/dataset.xlsx")
    # analyze_data(data)