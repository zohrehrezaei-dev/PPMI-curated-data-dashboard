"""
Data Dictionary Processor - Handle merged cells properly
This script will process the PPMI data dictionary with merged cells and create a proper structure
"""

import pandas as pd
import numpy as np

def process_merged_data_dictionary(file_path):
    """Process data dictionary with merged cells to create proper variable-code mapping"""
    
    print("🔧 PROCESSING MERGED DATA DICTIONARY")
    print("=" * 50)
    
    try:
        # Load the raw data dictionary
        raw_dict = pd.read_excel(file_path, sheet_name='Data dictionary')
        
        print(f"📊 Raw dictionary shape: {raw_dict.shape}")
        print(f"Columns: {list(raw_dict.columns)}")
        
        # Show sample of raw data to understand structure
        print("\n📋 Sample of raw dictionary:")
        print(raw_dict.head(15).to_string())
        
        # Process merged cells
        processed_dict = []
        current_variable = None
        current_category = None
        current_description = None
        
        for idx, row in raw_dict.iterrows():
            # Check if this row has a new variable (not NaN in Variable column)
            if pd.notna(row['Variable']):
                current_variable = row['Variable']
                current_category = row['Category'] if pd.notna(row['Category']) else current_category
                current_description = row['Description'] if pd.notna(row['Description']) else current_description
            
            # For each row (whether it's a new variable or continuation), record the code/decode
            if pd.notna(row.get('Code', None)) or pd.notna(row.get('Decode', None)):
                processed_dict.append({
                    'Variable': current_variable,
                    'Category': current_category,
                    'Description': current_description,
                    'Code': row.get('Code', None),
                    'Decode': row.get('Decode', None)
                })
        
        # Convert to DataFrame
        processed_df = pd.DataFrame(processed_dict)
        
        print(f"\n✅ Processed dictionary shape: {processed_df.shape}")
        print("\n📊 Sample of processed dictionary:")
        print(processed_df.head(15).to_string(index=False))
        
        # Create variable summary (one row per variable with all codes combined)
        variable_summary = []
        for variable in processed_df['Variable'].unique():
            if pd.notna(variable):
                var_data = processed_df[processed_df['Variable'] == variable]
                
                # Combine all codes and decodes for this variable
                codes_list = []
                for _, row in var_data.iterrows():
                    if pd.notna(row['Code']) and pd.notna(row['Decode']):
                        codes_list.append(f"{row['Code']}: {row['Decode']}")
                
                variable_summary.append({
                    'Variable': variable,
                    'Category': var_data.iloc[0]['Category'],
                    'Description': var_data.iloc[0]['Description'],
                    'Codes_Count': len(codes_list),
                    'All_Codes': ' | '.join(codes_list) if codes_list else 'No codes'
                })
        
        summary_df = pd.DataFrame(variable_summary)
        
        print(f"\n📈 Variable Summary:")
        print(f"Total unique variables: {len(summary_df)}")
        print(f"Variables with codes: {len(summary_df[summary_df['Codes_Count'] > 0])}")
        
        # Show categories
        print(f"\n🏷️ Categories found:")
        category_counts = summary_df['Category'].value_counts()
        for cat, count in category_counts.items():
            print(f"  • {cat}: {count} variables")
        
        # Show example of COHORT variable
        cohort_example = processed_df[processed_df['Variable'] == 'COHORT']
        if not cohort_example.empty:
            print(f"\n🎯 COHORT Variable Example (Properly Processed):")
            print(cohort_example.to_string(index=False))
        
        return processed_df, summary_df
        
    except Exception as e:
        print(f"❌ Error processing dictionary: {str(e)}")
        return None, None

def analyze_variable_codes(processed_dict, variable_name):
    """Analyze codes for a specific variable"""
    var_data = processed_dict[processed_dict['Variable'] == variable_name]
    
    if var_data.empty:
        print(f"Variable '{variable_name}' not found")
        return
    
    print(f"\n🔍 Analysis of Variable: {variable_name}")
    print("-" * 40)
    print(f"Category: {var_data.iloc[0]['Category']}")
    print(f"Description: {var_data.iloc[0]['Description']}")
    print(f"Number of codes: {len(var_data)}")
    print("\nCodes and Meanings:")
    
    for _, row in var_data.iterrows():
        if pd.notna(row['Code']) and pd.notna(row['Decode']):
            print(f"  {row['Code']}: {row['Decode']}")

def save_processed_dictionary(processed_dict, summary_df, output_file):
    """Save the processed dictionary to Excel file"""
    with pd.ExcelWriter(output_file) as writer:
        processed_dict.to_excel(writer, sheet_name='Processed_Dictionary', index=False)
        summary_df.to_excel(writer, sheet_name='Variable_Summary', index=False)
    
    print(f"✅ Processed dictionary saved to: {output_file}")

if __name__ == "__main__":
    # Your dataset path
    file_path = r"G:\Train\Parkinson PPMI\PPMI_Curated_Data_Cut_Public_20250714.xlsx"
    
    # Process the dictionary
    processed_dict, summary_df = process_merged_data_dictionary(file_path)
    
    if processed_dict is not None:
        # Analyze some example variables
        print(f"\n" + "="*60)
        analyze_variable_codes(processed_dict, 'COHORT')
        
        # Look for other interesting variables
        for var in ['APPRDX', 'GENDER', 'HANDED']:  # Common PPMI variables
            if var in processed_dict['Variable'].values:
                analyze_variable_codes(processed_dict, var)
        
        # Save processed dictionary
        output_file = "processed_data_dictionary.xlsx"
        save_processed_dictionary(processed_dict, summary_df, output_file)
        
        print(f"\n🚀 NEXT STEPS:")
        print("1. Review the processed dictionary")
        print("2. I'll update the dashboard to use this proper structure")
        print("3. Much better analysis with correct variable-code relationships")
    else:
        print("❌ Failed to process data dictionary")