"""
Simple Dataset Explorer - Just provide your file path and we'll analyze it
"""

import pandas as pd
import os

def quick_explore(file_path):
    """Quick exploration of Excel file"""
    print(f"🔍 Analyzing: {os.path.basename(file_path)}")
    print("=" * 50)
    
    try:
        # Get sheet names
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        print(f"📊 Found {len(sheet_names)} sheets:")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"  {i}. {sheet}")
        
        # Analyze each sheet briefly
        for sheet_name in sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=5)
            print(f"\n📋 {sheet_name}: {df.shape[0]}+ rows × {df.shape[1]} columns")
            print(f"Columns: {list(df.columns[:10])}")
            if df.shape[1] > 10:
                print(f"... and {df.shape[1] - 10} more columns")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# You can modify this path to point to your Excel file
file_path = r"YOUR_FILE_PATH_HERE"

# Example paths (uncomment and modify one):
# file_path = r"C:\Users\YourName\Documents\parkinson_data.xlsx"
# file_path = r"G:\Train\Parkinson PPMI\your_dataset.xlsx"

if os.path.exists(file_path) and file_path != "YOUR_FILE_PATH_HERE":
    quick_explore(file_path)
else:
    print("📁 Please edit this script and set your file path:")
    print("   1. Open src/quick_explore.py")
    print("   2. Replace 'YOUR_FILE_PATH_HERE' with your actual Excel file path")
    print("   3. Run the script again")
    print("\nExample:")
    print('   file_path = r"C:\\Users\\YourName\\Documents\\parkinson_data.xlsx"')