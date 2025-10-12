import pandas as pd
import numpy as np
from scipy import stats
import streamlit as st

class DataAnalyzer:
    """Class for analyzing dataset characteristics and patterns"""
    
    def __init__(self):
        pass
    
    def analyze_missing_data(self, data):
        """Analyze missing data patterns"""
        missing_info = []
        
        for col in data.columns:
            missing_count = data[col].isnull().sum()
            missing_pct = (missing_count / len(data)) * 100
            
            missing_info.append({
                'Variable': col,
                'Missing_Count': missing_count,
                'Missing_Percentage': round(missing_pct, 2),
                'Data_Type': str(data[col].dtype),
                'Unique_Values': data[col].nunique()
            })
        
        missing_df = pd.DataFrame(missing_info)
        missing_df = missing_df.sort_values('Missing_Percentage', ascending=False)
        
        return missing_df
    
    def analyze_variable_types(self, data):
        """Categorize variables by type and characteristics"""
        variable_analysis = []
        
        for col in data.columns:
            col_data = data[col]
            
            # Determine variable type
            if col_data.dtype in ['object', 'category']:
                var_type = 'Categorical'
                unique_values = col_data.nunique()
                
                if unique_values == 2:
                    subtype = 'Binary'
                elif unique_values <= 10:
                    subtype = 'Nominal'
                else:
                    subtype = 'High Cardinality'
                    
            elif col_data.dtype in ['int64', 'float64']:
                var_type = 'Numeric'
                unique_values = col_data.nunique()
                
                if unique_values <= 10:
                    subtype = 'Discrete/Ordinal'
                else:
                    subtype = 'Continuous'
            else:
                var_type = 'Other'
                subtype = 'Unknown'
                unique_values = col_data.nunique()
            
            # Calculate basic statistics
            if var_type == 'Numeric':
                mean_val = col_data.mean()
                std_val = col_data.std()
                min_val = col_data.min()
                max_val = col_data.max()
            else:
                mean_val = std_val = min_val = max_val = None
            
            variable_analysis.append({
                'Variable': col,
                'Type': var_type,
                'Subtype': subtype,
                'Unique_Values': unique_values,
                'Missing_Count': col_data.isnull().sum(),
                'Mean': mean_val,
                'Std': std_val,
                'Min': min_val,
                'Max': max_val
            })
        
        return pd.DataFrame(variable_analysis)
    
    def detect_parkinson_relevance(self, data, data_dict=None):
        """Identify variables likely related to Parkinson's disease"""
        parkinson_keywords = [
            'parkinson', 'pd', 'motor', 'tremor', 'rigidity', 'bradykinesia',
            'dopamine', 'levodopa', 'dopa', 'updrs', 'hoehn', 'yahr',
            'gait', 'balance', 'freezing', 'dyskinesia', 'cognitive',
            'depression', 'anxiety', 'sleep', 'olfactory', 'constipation',
            'rbd', 'rem', 'substantia', 'nigra', 'alpha-synuclein'
        ]
        
        relevant_variables = []
        
        for col in data.columns:
            relevance_score = 0
            relevance_reasons = []
            
            # Check column name
            col_lower = col.lower()
            for keyword in parkinson_keywords:
                if keyword in col_lower:
                    relevance_score += 2
                    relevance_reasons.append(f"Column name contains '{keyword}'")
            
            # Check data dictionary if available
            if data_dict is not None and col in data_dict.index:
                if 'Description' in data_dict.columns:
                    desc = str(data_dict.loc[col, 'Description']).lower()
                    for keyword in parkinson_keywords:
                        if keyword in desc:
                            relevance_score += 3
                            relevance_reasons.append(f"Description contains '{keyword}'")
                
                if 'Value_Codes' in data_dict.columns:
                    codes = str(data_dict.loc[col, 'Value_Codes']).lower()
                    for keyword in parkinson_keywords:
                        if keyword in codes:
                            relevance_score += 1
                            relevance_reasons.append(f"Value codes contain '{keyword}'")
            
            # Additional heuristics based on data patterns
            if data[col].dtype in ['int64', 'float64']:
                # Check for scales commonly used in Parkinson's research
                unique_vals = sorted(data[col].dropna().unique())
                if len(unique_vals) <= 10 and min(unique_vals) >= 0:
                    if max(unique_vals) in [3, 4, 5, 7, 10]:  # Common scale ranges
                        relevance_score += 1
                        relevance_reasons.append("Appears to be a clinical scale")
            
            if relevance_score > 0:
                relevant_variables.append({
                    'Variable': col,
                    'Relevance_Score': relevance_score,
                    'Reasons': '; '.join(relevance_reasons),
                    'Data_Type': str(data[col].dtype),
                    'Unique_Values': data[col].nunique()
                })
        
        relevance_df = pd.DataFrame(relevant_variables)
        if not relevance_df.empty:
            relevance_df = relevance_df.sort_values('Relevance_Score', ascending=False)
        
        return relevance_df
    
    def calculate_correlations_with_target(self, data, target_variables=None):
        """Calculate correlations with potential target variables"""
        if target_variables is None:
            # Try to identify potential target variables
            target_variables = []
            for col in data.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in ['diagnosis', 'class', 'target', 'label', 'outcome']):
                    target_variables.append(col)
        
        numeric_data = data.select_dtypes(include=[np.number])
        correlations = {}
        
        for target in target_variables:
            if target in numeric_data.columns:
                target_corr = numeric_data.corrwith(numeric_data[target]).abs().sort_values(ascending=False)
                correlations[target] = target_corr
        
        return correlations
    
    def detect_outliers(self, data, method='iqr'):
        """Detect outliers in numeric variables"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        outlier_info = []
        
        for col in numeric_cols:
            col_data = data[col].dropna()
            
            if method == 'iqr':
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(col_data))
                outliers = col_data[z_scores > 3]
            
            outlier_info.append({
                'Variable': col,
                'Outlier_Count': len(outliers),
                'Outlier_Percentage': round((len(outliers) / len(col_data)) * 100, 2),
                'Method': method.upper()
            })
        
        return pd.DataFrame(outlier_info)
    
    def generate_data_quality_report(self, data, data_dict=None):
        """Generate comprehensive data quality report"""
        report = {}
        
        # Basic info
        report['basic_info'] = {
            'total_records': len(data),
            'total_variables': len(data.columns),
            'total_missing_values': data.isnull().sum().sum(),
            'missing_percentage': round((data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100, 2)
        }
        
        # Variable analysis
        report['variable_analysis'] = self.analyze_variable_types(data)
        
        # Missing data analysis
        report['missing_data'] = self.analyze_missing_data(data)
        
        # Parkinson's relevance
        report['parkinson_relevance'] = self.detect_parkinson_relevance(data, data_dict)
        
        # Outlier detection
        report['outliers'] = self.detect_outliers(data)
        
        return report