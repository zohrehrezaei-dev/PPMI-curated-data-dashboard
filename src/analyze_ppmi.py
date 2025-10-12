"""
PPMI Dataset Explorer - Customized for your specific dataset
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_ppmi_dataset():
    """Analyze the PPMI dataset structure"""
    
    # Your dataset path
    file_path = r"G:\Train\Parkinson PPMI\PPMI_Curated_Data_Cut_Public_20250714.xlsx"
    
    print("🧠 PPMI DATASET ANALYSIS")
    print("=" * 50)
    
    try:
        # Load the main data sheet
        print("📊 Loading main data sheet: '20250609'...")
        main_data = pd.read_excel(file_path, sheet_name='20250609')
        
        print(f"✅ Main Dataset Loaded:")
        print(f"  • Records (patients/visits): {len(main_data):,}")
        print(f"  • Variables: {len(main_data.columns):,}")
        print(f"  • Memory usage: {main_data.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        
        # Load data dictionary
        print("\n📚 Loading data dictionary...")
        data_dict = pd.read_excel(file_path, sheet_name='Data dictionary')
        
        print(f"✅ Data Dictionary Loaded:")
        print(f"  • Dictionary entries: {len(data_dict):,}")
        print(f"  • Categories available: {data_dict['Category'].nunique() if 'Category' in data_dict.columns else 'N/A'}")
        
        print(f"\n📋 Data Dictionary Structure:")
        dict_columns = data_dict.columns[:5].tolist()  # First 5 columns as requested
        for i, col in enumerate(dict_columns, 1):
            print(f"  {i}. {col}")
        
        # Sample of data dictionary
        print(f"\n📖 Data Dictionary Sample:")
        print(data_dict[dict_columns].head(10).to_string(index=False))
        
        # Analyze categories
        if 'Category' in data_dict.columns:
            print(f"\n🏷️ Variable Categories:")
            categories = data_dict['Category'].value_counts()
            for cat, count in categories.head(15).items():
                print(f"  • {cat}: {count} variables")
            
            if len(categories) > 15:
                print(f"  ... and {len(categories) - 15} more categories")
        
        # Sample main data columns
        print(f"\n📊 Main Data Sample Columns:")
        sample_cols = main_data.columns[:20].tolist()
        for i, col in enumerate(sample_cols, 1):
            print(f"  {i:2d}. {col}")
        
        if len(main_data.columns) > 20:
            print(f"     ... and {len(main_data.columns) - 20} more columns")
        
        # Data types analysis
        print(f"\n🔍 Data Types Overview:")
        dtype_counts = main_data.dtypes.astype(str).value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  • {dtype}: {count} variables")
        
        # Missing data overview
        print(f"\n❓ Missing Data Overview:")
        missing_pct = (main_data.isnull().sum() / len(main_data) * 100)
        high_missing = missing_pct[missing_pct > 50].sort_values(ascending=False)
        
        if not high_missing.empty:
            print(f"Variables with >50% missing data:")
            for var, pct in high_missing.head(10).items():
                print(f"  • {var}: {pct:.1f}% missing")
        else:
            print("✅ No variables with >50% missing data")
        
        # Try to identify key variables
        print(f"\n🎯 Key PPMI Variables Detection:")
        ppmi_keywords = [
            'patno', 'patient', 'subjid', 'visit', 'age', 'gender', 'sex',
            'updrs', 'hoehn', 'yahr', 'moca', 'mmse', 'tremor', 'bradykinesia',
            'rigidity', 'postural', 'diagnosis', 'group', 'cohort'
        ]
        
        key_vars = []
        for col in main_data.columns:
            col_lower = col.lower()
            for keyword in ppmi_keywords:
                if keyword in col_lower:
                    key_vars.append((col, keyword))
                    break
        
        if key_vars:
            print("Potential key variables found:")
            for var, keyword in key_vars[:15]:
                print(f"  • {var} (matches: {keyword})")
        else:
            print("Using column name analysis...")
            
        return main_data, data_dict, True
        
    except Exception as e:
        print(f"❌ Error analyzing dataset: {str(e)}")
        return None, None, False

def suggest_ppmi_dashboard():
    """Suggest customizations for PPMI dashboard"""
    print(f"\n💡 CUSTOMIZED PPMI DASHBOARD SUGGESTIONS")
    print("=" * 50)
    
    print("🎨 Recommended Dashboard Pages:")
    print("  1. 📋 PPMI Dataset Overview")
    print("     • Patient demographics and visit statistics")
    print("     • Cohort distribution (HC, PD, SWEDD, etc.)")
    print("     • Data completeness by category")
    
    print("  2. 🧠 Clinical Assessments")
    print("     • UPDRS scores analysis")
    print("     • Cognitive assessments (MoCA, MMSE)")
    print("     • Motor vs Non-motor symptoms")
    
    print("  3. 🏷️ Variable Categories Explorer")
    print("     • Browse by data dictionary categories")
    print("     • Interactive variable search")
    print("     • Category-specific analysis")
    
    print("  4. 📊 Longitudinal Analysis")
    print("     • Visit progression patterns")
    print("     • Timeline visualizations")
    print("     • Change over time analysis")
    
    print("  5. 🔍 Data Quality Assessment")
    print("     • Missing data patterns by category")
    print("     • Data completeness by visit")
    print("     • Quality control metrics")
    
    print("  6. 📈 Statistical Summary")
    print("     • Distribution analysis by category")
    print("     • Correlation networks")
    print("     • Group comparisons")

if __name__ == "__main__":
    main_data, data_dict, success = analyze_ppmi_dataset()
    
    if success:
        suggest_ppmi_dashboard()
        
        print(f"\n🚀 NEXT STEPS")
        print("=" * 20)
        print("1. I'll create a customized PPMI dashboard")
        print("2. Direct data loading from your Excel file")
        print("3. Category-based variable exploration")
        print("4. PPMI-specific clinical analysis tools")
        print("5. Enhanced visualizations for longitudinal data")
    else:
        print("\n❌ Could not analyze the dataset.")
        print("Please check the file path and sheet names.")