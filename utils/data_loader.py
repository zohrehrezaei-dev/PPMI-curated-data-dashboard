import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st

class DataLoader:
    """Class to handle loading and preprocessing of Excel data with data dictionary"""
    
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.main_data = None
        self.data_dict = None
    
    def load_data(self):
        """Load main data and data dictionary from Excel file"""
        try:
            # Read Excel file and get sheet names
            excel_file = pd.ExcelFile(self.file_path)
            sheet_names = excel_file.sheet_names
            
            st.info(f"Found sheets: {', '.join(sheet_names)}")
            
            # Try to identify main data sheet and dictionary sheet
            main_sheet, dict_sheet = self._identify_sheets(sheet_names)
            
            # Load main data
            if main_sheet:
                self.main_data = pd.read_excel(self.file_path, sheet_name=main_sheet)
                st.success(f"✅ Loaded main data from sheet: {main_sheet}")
                st.info(f"Data shape: {self.main_data.shape}")
            else:
                raise ValueError("Could not identify main data sheet")
            
            # Load data dictionary if available
            if dict_sheet:
                self.data_dict = pd.read_excel(self.file_path, sheet_name=dict_sheet)
                self.data_dict = self._process_data_dictionary(self.data_dict)
                st.success(f"✅ Loaded data dictionary from sheet: {dict_sheet}")
            else:
                st.warning("⚠️ No data dictionary sheet found")
                self.data_dict = None
            
            # Basic data cleaning
            self.main_data = self._clean_data(self.main_data)
            
            return self.main_data, self.data_dict
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            raise e
    
    def _identify_sheets(self, sheet_names):
        """Identify which sheets contain main data and data dictionary"""
        main_sheet = None
        dict_sheet = None
        
        # Keywords to identify dictionary sheets
        dict_keywords = ['dictionary', 'dict', 'metadata', 'variables', 'codebook', 'legend']
        
        # First, try to find dictionary sheet
        for sheet in sheet_names:
            if any(keyword in sheet.lower() for keyword in dict_keywords):
                dict_sheet = sheet
                break
        
        # Find main data sheet (usually the largest or first non-dictionary sheet)
        for sheet in sheet_names:
            if sheet != dict_sheet:
                # Try to peek at the sheet to see if it looks like main data
                try:
                    temp_df = pd.read_excel(self.file_path, sheet_name=sheet, nrows=5)
                    if len(temp_df.columns) > 3:  # Assume main data has many columns
                        main_sheet = sheet
                        break
                except:
                    continue
        
        # If no main sheet identified, use the first sheet
        if not main_sheet and sheet_names:
            main_sheet = sheet_names[0]
            if main_sheet == dict_sheet and len(sheet_names) > 1:
                main_sheet = sheet_names[1]
        
        return main_sheet, dict_sheet
    
    def _process_data_dictionary(self, dict_df):
        """Process and standardize the data dictionary format"""
        try:
            # Standardize column names
            dict_df.columns = dict_df.columns.str.strip().str.lower()
            
            # Try to identify variable name and description columns
            var_col = None
            desc_col = None
            value_col = None
            
            for col in dict_df.columns:
                if any(keyword in col for keyword in ['variable', 'var', 'name', 'column']):
                    var_col = col
                elif any(keyword in col for keyword in ['description', 'desc', 'meaning', 'definition']):
                    desc_col = col
                elif any(keyword in col for keyword in ['value', 'code', 'category', 'level']):
                    value_col = col
            
            # Use first columns if no keywords matched
            if not var_col and len(dict_df.columns) > 0:
                var_col = dict_df.columns[0]
            if not desc_col and len(dict_df.columns) > 1:
                desc_col = dict_df.columns[1]
            if not value_col and len(dict_df.columns) > 2:
                value_col = dict_df.columns[2]
            
            # Create standardized dictionary
            processed_dict = pd.DataFrame()
            if var_col:
                processed_dict['Variable'] = dict_df[var_col]
            if desc_col:
                processed_dict['Description'] = dict_df[desc_col]
            if value_col:
                processed_dict['Value_Codes'] = dict_df[value_col]
            
            # Set variable names as index
            if 'Variable' in processed_dict.columns:
                processed_dict = processed_dict.set_index('Variable')
            
            return processed_dict
            
        except Exception as e:
            st.warning(f"Could not process data dictionary: {str(e)}")
            return dict_df
    
    def _clean_data(self, data):
        """Perform basic data cleaning"""
        # Remove completely empty rows and columns
        data = data.dropna(how='all')
        data = data.dropna(axis=1, how='all')
        
        # Clean column names
        data.columns = data.columns.astype(str).str.strip()
        
        # Convert obvious numeric columns
        for col in data.columns:
            if data[col].dtype == 'object':
                # Try to convert to numeric if possible
                numeric_data = pd.to_numeric(data[col], errors='coerce')
                if numeric_data.notna().sum() > len(data) * 0.5:  # If >50% are numeric
                    data[col] = numeric_data
        
        return data
    
    def get_data_info(self):
        """Get basic information about the loaded data"""
        if self.main_data is None:
            return None
        
        info = {
            'shape': self.main_data.shape,
            'columns': list(self.main_data.columns),
            'data_types': self.main_data.dtypes.to_dict(),
            'missing_values': self.main_data.isnull().sum().to_dict(),
            'has_dictionary': self.data_dict is not None
        }
        
        return info