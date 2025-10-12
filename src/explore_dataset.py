"""
Data Explorer Script for Parkinson's Dataset
This script will analyze your Excel file and help customize the dashboard
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

def explore_excel_structure(file_path):
    """Explore the structure of the Excel file"""
    print("🔍 EXPLORING EXCEL FILE STRUCTURE")
    print("=" * 50)
    
    try:
        # Read Excel file and get sheet names
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        print(f"📊 Found {len(sheet_names)} sheets:")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"  {i}. {sheet}")
        print()
        
        # Analyze each sheet
        for sheet_name in sheet_names:
            print(f"📋 SHEET: {sheet_name}")
            print("-" * 30)
            
            # Read first few rows to understand structure
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)
            
            print(f"Shape: {df.shape} (rows × columns)")
            print(f"Columns ({len(df.columns)}):")
            
            for i, col in enumerate(df.columns[:15], 1):  # Show first 15 columns
                print(f"  {i:2d}. {col}")
            
            if len(df.columns) > 15:
                print(f"     ... and {len(df.columns) - 15} more columns")
            
            print(f"\nFirst 3 rows:")
            print(df.head(3).to_string())
            print("\n" + "="*80 + "\n")
        
        return excel_file, sheet_names
        
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return None, None

def analyze_data_sheet(file_path, sheet_name):
    """Analyze the main data sheet in detail"""
    print(f"🧬 DETAILED ANALYSIS OF: {sheet_name}")
    print("=" * 50)
    
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    print(f"📊 Dataset Overview:")
    print(f"  • Total Records: {len(df):,}")
    print(f"  • Total Variables: {len(df.columns):,}")
    print(f"  • Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    print()
    
    print(f"🔍 Column Analysis:")
    print("-" * 20)
    
    # Analyze each column
    analysis = []
    for col in df.columns:
        col_data = df[col]
        
        analysis.append({
            'Column': col,
            'Type': str(col_data.dtype),
            'Non_Null': col_data.count(),
            'Missing': col_data.isnull().sum(),
            'Missing_%': round((col_data.isnull().sum() / len(df)) * 100, 1),
            'Unique': col_data.nunique(),
            'Sample_Values': str(col_data.dropna().head(3).tolist())[:100] + "..." if len(str(col_data.dropna().head(3).tolist())) > 100 else str(col_data.dropna().head(3).tolist())
        })
    
    analysis_df = pd.DataFrame(analysis)
    
    # Show columns with different characteristics
    print("📈 Numeric Variables:")
    numeric_cols = analysis_df[analysis_df['Type'].str.contains('int|float')].head(10)
    if not numeric_cols.empty:
        print(numeric_cols[['Column', 'Type', 'Missing_%', 'Unique', 'Sample_Values']].to_string(index=False))
    else:
        print("  No numeric columns found in first 10")
    
    print("\n📝 Text/Categorical Variables:")
    text_cols = analysis_df[analysis_df['Type'].str.contains('object')].head(10)
    if not text_cols.empty:
        print(text_cols[['Column', 'Type', 'Missing_%', 'Unique', 'Sample_Values']].to_string(index=False))
    else:
        print("  No text columns found in first 10")
    
    print(f"\n❓ Missing Data Summary:")
    missing_summary = analysis_df[analysis_df['Missing_%'] > 0].sort_values('Missing_%', ascending=False)
    if not missing_summary.empty:
        print(missing_summary[['Column', 'Missing_%']].head(10).to_string(index=False))
    else:
        print("  No missing data found!")
    
    return df, analysis_df

def detect_parkinson_variables(analysis_df):
    """Detect variables likely related to Parkinson's disease"""
    print(f"\n🧠 PARKINSON'S DISEASE VARIABLE DETECTION")
    print("=" * 50)
    
    parkinson_keywords = [
        'parkinson', 'pd', 'motor', 'tremor', 'rigidity', 'bradykinesia',
        'dopamine', 'levodopa', 'dopa', 'updrs', 'hoehn', 'yahr',
        'gait', 'balance', 'freezing', 'dyskinesia', 'cognitive',
        'depression', 'anxiety', 'sleep', 'olfactory', 'constipation',
        'rbd', 'rem', 'substantia', 'nigra', 'mmse', 'moca'
    ]
    
    relevant_vars = []
    
    for _, row in analysis_df.iterrows():
        col_name = str(row['Column']).lower()
        relevance_score = 0
        reasons = []
        
        for keyword in parkinson_keywords:
            if keyword in col_name:
                relevance_score += 1
                reasons.append(f"Contains '{keyword}'")
        
        if relevance_score > 0:
            relevant_vars.append({
                'Variable': row['Column'],
                'Score': relevance_score,
                'Reasons': ', '.join(reasons),
                'Type': row['Type'],
                'Missing_%': row['Missing_%']
            })
    
    if relevant_vars:
        relevant_df = pd.DataFrame(relevant_vars).sort_values('Score', ascending=False)
        print("🎯 Potential Parkinson's-related variables found:")
        print(relevant_df.to_string(index=False))
    else:
        print("🔍 No obvious Parkinson's-related variables detected in column names.")
        print("   This might be because variables use codes or abbreviations.")
    
    return relevant_vars

def suggest_dashboard_customizations(df, analysis_df, relevant_vars):
    """Suggest customizations for the dashboard"""
    print(f"\n💡 DASHBOARD CUSTOMIZATION SUGGESTIONS")
    print("=" * 50)
    
    # Data characteristics
    total_vars = len(df.columns)
    numeric_vars = len(analysis_df[analysis_df['Type'].str.contains('int|float')])
    categorical_vars = len(analysis_df[analysis_df['Type'].str.contains('object')])
    
    print(f"📊 Dataset Characteristics:")
    print(f"  • Records: {len(df):,}")
    print(f"  • Total Variables: {total_vars}")
    print(f"  • Numeric Variables: {numeric_vars}")
    print(f"  • Categorical Variables: {categorical_vars}")
    print(f"  • Potential PD Variables: {len(relevant_vars)}")
    
    print(f"\n🎨 Recommended Dashboard Pages:")
    print("  1. 📋 Dataset Overview (current)")
    print("  2. 🧠 Parkinson's Variables (custom)")
    print("  3. 🔍 Variable Explorer (enhanced)")
    print("  4. 📊 Data Quality Report (custom)")
    print("  5. 🔗 Correlation Analysis (enhanced)")
    print("  6. 📈 Statistical Summary (new)")
    
    print(f"\n⚙️ Customization Recommendations:")
    
    if len(relevant_vars) > 0:
        print("  ✅ Create dedicated Parkinson's variables page")
        print("  ✅ Add clinical scale detection")
    
    if total_vars > 50:
        print("  ✅ Add variable search and filtering")
        print("  ✅ Group variables by categories")
    
    if numeric_vars > 10:
        print("  ✅ Enhanced correlation analysis with clustering")
        print("  ✅ Distribution analysis with statistical tests")
    
    missing_vars = len(analysis_df[analysis_df['Missing_%'] > 0])
    if missing_vars > total_vars * 0.2:  # More than 20% have missing data
        print("  ⚠️  Add comprehensive missing data analysis")
        print("  ⚠️  Pattern detection for missing data")

def main():
    """Main exploration function"""
    print("🧬 PARKINSON'S DATASET EXPLORER")
    print("=" * 50)
    print("Please provide the path to your Excel file:")
    print("Example: C:/Users/YourName/Documents/parkinson_data.xlsx")
    print()
    
    # Get file path from user
    file_path = input("Enter Excel file path: ").strip().strip('"')
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"\n🔍 Analyzing: {file_path}")
    print("=" * 50)
    
    # Step 1: Explore Excel structure
    excel_file, sheet_names = explore_excel_structure(file_path)
    
    if excel_file is None:
        return
    
    # Step 2: Let user choose main data sheet
    print("Which sheet contains your main dataset?")
    for i, sheet in enumerate(sheet_names, 1):
        print(f"  {i}. {sheet}")
    
    try:
        choice = int(input("\nEnter sheet number: ")) - 1
        main_sheet = sheet_names[choice]
    except (ValueError, IndexError):
        print("Invalid choice. Using first sheet.")
        main_sheet = sheet_names[0]
    
    print(f"\n📊 Analyzing main data sheet: {main_sheet}")
    
    # Step 3: Detailed analysis
    df, analysis_df = analyze_data_sheet(file_path, main_sheet)
    
    # Step 4: Detect Parkinson's variables
    relevant_vars = detect_parkinson_variables(analysis_df)
    
    # Step 5: Suggest customizations
    suggest_dashboard_customizations(df, analysis_df, relevant_vars)
    
    print(f"\n💾 EXPORT OPTIONS")
    print("=" * 20)
    print("Would you like to save the analysis results?")
    save_choice = input("Save analysis to file? (y/n): ").lower().strip()
    
    if save_choice in ['y', 'yes']:
        output_file = "data_analysis_report.xlsx"
        with pd.ExcelWriter(output_file) as writer:
            analysis_df.to_excel(writer, sheet_name='Variable_Analysis', index=False)
            if relevant_vars:
                pd.DataFrame(relevant_vars).to_excel(writer, sheet_name='Parkinson_Variables', index=False)
        
        print(f"✅ Analysis saved to: {output_file}")
    
    print(f"\n🎯 NEXT STEPS")
    print("=" * 20)
    print("1. Share the analysis results with me")
    print("2. I'll customize the dashboard for your specific dataset")
    print("3. We'll create a direct data loading script")
    print("4. Enhanced visualizations based on your data characteristics")

if __name__ == "__main__":
    main()