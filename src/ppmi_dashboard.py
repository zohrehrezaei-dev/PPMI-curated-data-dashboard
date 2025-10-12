import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="PPMI Dataset Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Your dataset path - no upload needed!
DATASET_PATH = r"G:\Train\Parkinson PPMI\PPMI_Curated_Data_Cut_Public_20250714.xlsx"
MAIN_SHEET = "20250609"
DICT_SHEET = "Data dictionary"

@st.cache_data
def load_ppmi_data():
    """Load PPMI dataset and data dictionary"""
    try:
        # Load main data
        main_data = pd.read_excel(DATASET_PATH, sheet_name=MAIN_SHEET)
        
        # Load and process data dictionary to handle merged cells properly
        raw_dict = pd.read_excel(DATASET_PATH, sheet_name=DICT_SHEET)
        
        # Process merged cells - fill forward the merged variable information
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
        data_dict = pd.DataFrame(processed_dict)
        
        # Fix data types to prevent PyArrow serialization issues
        data_dict['Code'] = data_dict['Code'].astype(str)
        data_dict['Decode'] = data_dict['Decode'].astype(str)
        data_dict['Variable'] = data_dict['Variable'].astype(str)
        data_dict['Category'] = data_dict['Category'].astype(str)
        data_dict['Description'] = data_dict['Description'].astype(str)
        
        # Create variable summary for easier browsing
        variable_summary = []
        for variable in data_dict['Variable'].unique():
            if pd.notna(variable):
                var_data = data_dict[data_dict['Variable'] == variable]
                
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
        
        variable_summary = pd.DataFrame(variable_summary)
        
        return main_data, data_dict, variable_summary
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

def main():
    st.title("🧠 PPMI Dataset Dashboard")
    st.markdown("**Parkinson's Progression Markers Initiative - Curated Data Analysis**")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading PPMI dataset..."):
        main_data, data_dict, variable_summary = load_ppmi_data()
    
    if main_data is None or data_dict is None:
        st.error("Could not load dataset. Please check the file path.")
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.header("📊 PPMI Data Navigation")
        
        # Dataset info
        st.info(f"""
        **Dataset Info:**
        - Records: {len(main_data):,}
        - Variables: {len(variable_summary):,}
        - Total Codes: {len(data_dict):,}
        """)
        
        # Show cohort distribution if COHORT variable exists
        if 'COHORT' in main_data.columns:
            st.subheader("👥 Cohort Distribution")
            cohort_counts = main_data['COHORT'].value_counts()
            
            # Get cohort labels from data dictionary
            cohort_labels = {}
            cohort_info = data_dict[data_dict['Variable'] == 'COHORT']
            for _, row in cohort_info.iterrows():
                if pd.notna(row['Code']) and pd.notna(row['Decode']):
                    cohort_labels[row['Code']] = row['Decode']
            
            for code, count in cohort_counts.items():
                label = cohort_labels.get(code, f"Code {code}")
                st.metric(label, count)
        
        # Navigation
        page = st.selectbox(
            "Choose Analysis Page:",
            [
                "📋 Dataset Overview",
                "🏷️ Variable Categories",
                "🔍 Variable Explorer", 
                "🧠 Clinical Assessments",
                "📊 Data Quality Report",
                "🔗 Correlation Analysis",
                "📚 Data Dictionary Browser"
            ]
        )
    
    # Main content
    if page == "📋 Dataset Overview":
        show_dataset_overview(main_data, data_dict, variable_summary)
    elif page == "🏷️ Variable Categories":
        show_variable_categories(main_data, data_dict, variable_summary)
    elif page == "🔍 Variable Explorer":
        show_variable_explorer(main_data, data_dict, variable_summary)
    elif page == "🧠 Clinical Assessments":
        show_clinical_assessments(main_data, data_dict, variable_summary)
    elif page == "📊 Data Quality Report":
        show_data_quality(main_data, data_dict, variable_summary)
    elif page == "🔗 Correlation Analysis":
        show_correlation_analysis(main_data)
    elif page == "📚 Data Dictionary Browser":
        show_data_dictionary(data_dict, variable_summary)

def show_dataset_overview(data, data_dict, variable_summary):
    """Display comprehensive dataset overview"""
    st.header("📋 PPMI Dataset Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", f"{len(data):,}")
    with col2:
        st.metric("Unique Variables", f"{len(variable_summary):,}")
    with col3:
        st.metric("Total Codes", f"{len(data_dict):,}")
    with col4:
        missing_pct = (data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100
        st.metric("Data Completeness", f"{100 - missing_pct:.1f}%")
    
    # COHORT analysis
    if 'COHORT' in data.columns:
        st.subheader("👥 Cohort Distribution Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Get cohort distribution with proper labels
            cohort_counts = data['COHORT'].value_counts().sort_index()
            
            # Get cohort labels from data dictionary
            cohort_labels = {}
            cohort_info = data_dict[data_dict['Variable'] == 'COHORT']
            for _, row in cohort_info.iterrows():
                if pd.notna(row['Code']) and pd.notna(row['Decode']):
                    cohort_labels[row['Code']] = row['Decode']
            
            # Create labeled data for visualization
            labels = [cohort_labels.get(code, f"Code {code}") for code in cohort_counts.index]
            
            fig = px.pie(
                values=cohort_counts.values,
                names=labels,
                title="PPMI Cohort Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Cohort Statistics")
            for code, count in cohort_counts.items():
                label = cohort_labels.get(code, f"Code {code}")
                percentage = (count / len(data)) * 100
                st.metric(label, f"{count} ({percentage:.1f}%)")
    
    # Categories distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Variable Types Distribution")
        dtype_counts = data.dtypes.astype(str).value_counts()
        fig = px.pie(
            values=dtype_counts.values,
            names=dtype_counts.index,
            title="Data Types in PPMI Dataset"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏷️ Variable Categories")
        cat_counts = variable_summary['Category'].value_counts()
        fig = px.bar(
            x=cat_counts.values,
            y=cat_counts.index,
            orientation='h',
            title="Variables by Category"
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Data preview
    st.subheader("📈 Data Preview")
    st.dataframe(data.head(10), width='stretch')

def show_variable_categories(data, data_dict, variable_summary):
    """Browse variables by categories"""
    st.header("🏷️ Variable Categories Explorer")
    
    # Category selection
    categories = sorted(variable_summary['Category'].unique())
    selected_category = st.selectbox("Select a category to explore:", categories)
    
    if selected_category:
        # Filter variables by category
        category_vars = variable_summary[variable_summary['Category'] == selected_category]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"📊 Variables in: {selected_category}")
            
            # Show category variables with enhanced info
            display_data = category_vars[['Variable', 'Description', 'Codes_Count', 'All_Codes']].copy()
            st.dataframe(display_data, width='stretch')
        
        with col2:
            st.subheader("📋 Category Statistics")
            st.metric("Variables in Category", len(category_vars))
            
            # Check which variables exist in main data
            existing_vars = category_vars['Variable'].isin(data.columns).sum()
            st.metric("Available in Dataset", existing_vars)
            
            # Variables with codes
            vars_with_codes = len(category_vars[category_vars['Codes_Count'] > 0])
            st.metric("Variables with Codes", vars_with_codes)
            
            # Missing data for this category
            if existing_vars > 0:
                category_data = data[category_vars['Variable'][category_vars['Variable'].isin(data.columns)]]
                missing_pct = (category_data.isnull().sum().sum() / (len(category_data) * len(category_data.columns))) * 100
                st.metric("Category Completeness", f"{100 - missing_pct:.1f}%")
        
        # Variable analysis for this category
        st.subheader(f"📈 {selected_category} - Variable Analysis")
        
        available_vars = category_vars['Variable'][category_vars['Variable'].isin(data.columns)].tolist()
        
        if available_vars:
            selected_var = st.selectbox("Select variable to analyze:", available_vars)
            
            if selected_var:
                analyze_single_variable(data, selected_var, data_dict)
        else:
            st.warning("No variables from this category found in the main dataset")

def show_variable_explorer(data, data_dict, variable_summary):
    """Enhanced variable explorer"""
    st.header("🔍 Variable Explorer")
    
    # Search functionality
    search_term = st.text_input("🔍 Search variables by name or description:")
    
    if search_term:
        # Search in variable names and descriptions
        mask = (data_dict['Variable'].str.contains(search_term, case=False, na=False))
        if 'Description' in data_dict.columns:
            mask |= (data_dict['Description'].str.contains(search_term, case=False, na=False))
        
        search_results = data_dict[mask]
        
        if not search_results.empty:
            st.subheader(f"🎯 Search Results for '{search_term}'")
            st.dataframe(search_results, use_container_width=True)
            
            # Analyze first result
            if search_results.iloc[0]['Variable'] in data.columns:
                analyze_single_variable(data, search_results.iloc[0]['Variable'], data_dict)
        else:
            st.warning("No variables found matching your search")
    else:
        # Variable selection dropdown
        variable_list = sorted([col for col in data.columns if col in data_dict['Variable'].values])
        selected_var = st.selectbox("Select a variable to explore:", variable_list)
        
        if selected_var:
            analyze_single_variable(data, selected_var, data_dict)

def analyze_single_variable(data, variable, data_dict):
    """Analyze a single variable in detail with proper code/decode display"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Variable description
        var_info = data_dict[data_dict['Variable'] == variable]
        if not var_info.empty:
            st.subheader(f"📝 {variable}")
            
            # Show category and description
            category = var_info.iloc[0]['Category']
            description = var_info.iloc[0]['Description']
            st.info(f"**Category:** {category}\n\n**Description:** {description}")
            
            # Show all codes and decodes for this variable
            codes_data = var_info[['Code', 'Decode']].dropna()
            if not codes_data.empty:
                st.subheader("🔑 Codes & Meanings")
                
                # Create a nice display of codes
                for _, row in codes_data.iterrows():
                    st.write(f"**{row['Code']}**: {row['Decode']}")
        
        # Visualization based on variable type and codes
        if variable in data.columns:
            if len(codes_data) > 0:
                # This is a coded variable - show distribution with proper labels
                value_counts = data[variable].value_counts().sort_index()
                
                # Create labels using the codes dictionary
                code_labels = {}
                for _, row in codes_data.iterrows():
                    if pd.notna(row['Code']) and pd.notna(row['Decode']):
                        code_labels[row['Code']] = f"{row['Code']}: {row['Decode']}"
                
                # Create labeled data
                labels = [code_labels.get(code, f"Code {code}") for code in value_counts.index]
                
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f'Distribution of {variable}',
                    labels={'x': variable, 'y': 'Count'}
                )
                
                # Update x-axis labels
                fig.update_layout(
                    xaxis_tickmode='array',
                    xaxis_tickvals=list(value_counts.index),
                    xaxis_ticktext=labels,
                    xaxis_tickangle=45
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
            elif data[variable].dtype in ['object', 'category']:
                # Categorical variable without specific codes
                value_counts = data[variable].value_counts().head(20)
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f'Distribution of {variable}',
                    labels={'x': variable, 'y': 'Count'}
                )
                fig.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                # Numeric variable
                fig = make_subplots(rows=1, cols=2, subplot_titles=['Distribution', 'Box Plot'])
                
                fig.add_trace(
                    go.Histogram(x=data[variable].dropna(), name='Distribution'),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Box(y=data[variable].dropna(), name='Box Plot'),
                    row=1, col=2
                )
                
                fig.update_layout(title_text=f'Analysis of {variable}', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Variable Statistics")
        
        if variable in data.columns:
            # Basic stats
            if len(codes_data) > 0 or data[variable].dtype in ['object', 'category']:
                # Show value counts with proper labels if available
                value_counts = data[variable].value_counts()
                
                if len(codes_data) > 0:
                    # Add labels to value counts
                    code_labels = {}
                    for _, row in codes_data.iterrows():
                        if pd.notna(row['Code']) and pd.notna(row['Decode']):
                            code_labels[row['Code']] = row['Decode']
                    
                    st.write("**Value Distribution:**")
                    for value, count in value_counts.items():
                        label = code_labels.get(value, f"Code {value}")
                        percentage = (count / len(data)) * 100
                        st.write(f"• **{value}** ({label}): {count} ({percentage:.1f}%)")
                else:
                    st.write(value_counts.head(10))
            else:
                st.write(data[variable].describe())
            
            # Missing values
            missing_count = data[variable].isnull().sum()
            missing_pct = (missing_count / len(data)) * 100
            st.metric("Missing Values", f"{missing_count} ({missing_pct:.1f}%)")
            
            # Unique values
            st.metric("Unique Values", data[variable].nunique())
        else:
            st.warning(f"Variable '{variable}' not found in main dataset")

def show_clinical_assessments(data, data_dict, variable_summary):
    """Show clinical assessment analysis"""
    st.header("🧠 Clinical Assessments Analysis")
    
    # Identify clinical variables
    clinical_keywords = ['updrs', 'hoehn', 'yahr', 'moca', 'mmse', 'diagnosis', 'age', 'gender', 'tremor']
    
    clinical_vars = []
    for col in data.columns:
        col_lower = col.lower()
        for keyword in clinical_keywords:
            if keyword in col_lower:
                clinical_vars.append(col)
                break
    
    if not clinical_vars:
        st.warning("No clinical assessment variables detected. Try using the Variable Explorer to find specific assessments.")
        return
    
    st.subheader("🎯 Detected Clinical Variables")
    
    # Display clinical variables
    for i, var in enumerate(clinical_vars[:15], 1):
        with st.expander(f"{i}. {var}"):
            analyze_single_variable(data, var, data_dict)

def show_data_quality(data, data_dict, variable_summary):
    """Show comprehensive data quality report"""
    st.header("📊 Data Quality Assessment")
    
    # Missing data analysis
    st.subheader("❓ Missing Data Analysis")
    
    missing_data = []
    for col in data.columns:
        missing_count = data[col].isnull().sum()
        missing_pct = (missing_count / len(data)) * 100
        
        missing_data.append({
            'Variable': col,
            'Missing_Count': missing_count,
            'Missing_Percentage': missing_pct,
            'Data_Type': str(data[col].dtype),
            'Unique_Values': data[col].nunique()
        })
    
    missing_df = pd.DataFrame(missing_data)
    missing_df = missing_df.sort_values('Missing_Percentage', ascending=False)
    
    # Show variables with most missing data
    high_missing = missing_df[missing_df['Missing_Percentage'] > 50]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Missing Data Summary")
        st.dataframe(missing_df.head(20), use_container_width=True)
    
    with col2:
        if not high_missing.empty:
            st.subheader("⚠️ High Missing Data Variables")
            fig = px.bar(
                high_missing.head(15),
                x='Missing_Percentage',
                y='Variable',
                orientation='h',
                title='Variables with >50% Missing Data'
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No variables with >50% missing data!")

def show_correlation_analysis(data):
    """Show correlation analysis"""
    st.header("🔗 Correlation Analysis")
    
    numeric_data = data.select_dtypes(include=[np.number])
    
    if len(numeric_data.columns) < 2:
        st.warning("Not enough numeric variables for correlation analysis")
        return
    
    # Sample numeric variables for performance
    if len(numeric_data.columns) > 50:
        st.info("Showing correlation for first 50 numeric variables for performance")
        numeric_data = numeric_data.iloc[:, :50]
    
    corr_matrix = numeric_data.corr()
    
    fig = px.imshow(
        corr_matrix,
        title="Variable Correlation Heatmap",
        color_continuous_scale="RdBu_r",
        aspect="auto"
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

def show_data_dictionary(data_dict, variable_summary):
    """Browse the complete data dictionary"""
    st.header("📚 Data Dictionary Browser")
    
    # Search in dictionary
    search_term = st.text_input("🔍 Search in data dictionary:")
    
    if search_term:
        mask = data_dict.apply(lambda x: x.astype(str).str.contains(search_term, case=False)).any(axis=1)
        filtered_dict = data_dict[mask]
        st.subheader(f"Search Results for '{search_term}'")
        st.dataframe(filtered_dict, use_container_width=True)
    else:
        st.dataframe(data_dict, use_container_width=True)

if __name__ == "__main__":
    main()