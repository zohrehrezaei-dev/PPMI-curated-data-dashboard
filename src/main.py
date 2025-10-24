import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys
import tempfile
import os

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

try:
    from data_loader import DataLoader
    from data_analyzer import DataAnalyzer
    from visualization_utils import VisualizationUtils
except ImportError:
    # Fallback if utils not available
    DataLoader = None
    DataAnalyzer = None
    VisualizationUtils = None

# Page configuration
st.set_page_config(
    page_title="PPMI Dataset Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_ppmi_data_from_upload(file_path, main_sheet="20250609", dict_sheet="Data dictionary"):
    """Load PPMI dataset and data dictionary from uploaded file"""
    try:
        # Load main data
        main_data = pd.read_excel(file_path, sheet_name=main_sheet)
        
        # Load and process data dictionary to handle merged cells properly
        raw_dict = pd.read_excel(file_path, sheet_name=dict_sheet)
        
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

# Page configuration
st.set_page_config(
    page_title="Parkinson's Disease Dataset Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🧠 PPMI Dataset Dashboard")
    st.markdown("**Parkinson's Progression Markers Initiative - Curated Data Analysis**")
    st.markdown("---")
    
    # Sidebar for file upload and navigation only
    with st.sidebar:
        st.header("📁 Data Upload")
        st.info("Upload your PPMI Excel file with data dictionary to begin analysis")
        
        uploaded_file = st.file_uploader(
            "Upload PPMI Excel file (.xlsx)", 
            type=['xlsx'],
            help="Upload your PPMI dataset with data dictionary sheet"
        )
        
        # Initialize session state for data
        if 'main_data' not in st.session_state:
            st.session_state.main_data = None
            st.session_state.data_dict = None
            st.session_state.variable_summary = None
        
        if uploaded_file is not None:
            # Save uploaded file temporarily (cloud-compatible)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                data_path = tmp_file.name
            
            st.success("✅ File uploaded successfully!")
            
            # Load data
            try:
                with st.spinner("Loading PPMI dataset..."):
                    main_data, data_dict, variable_summary = load_ppmi_data_from_upload(data_path)
                
                if main_data is None or data_dict is None:
                    st.error("Could not load dataset. Please check the file format.")
                else:
                    # Store in session state
                    st.session_state.main_data = main_data
                    st.session_state.data_dict = data_dict
                    st.session_state.variable_summary = variable_summary
                    
                    # Dataset info in sidebar
                    st.info(f"""
                    **Dataset Info:**
                    - Records: {len(main_data):,}
                    - Variables: {len(variable_summary):,}
                    - Total Codes: {len(data_dict):,}
                    """)
                    
                    # Show cohort distribution in sidebar if COHORT variable exists
                    if 'COHORT' in main_data.columns:
                        st.subheader("👥 Cohort Distribution")
                        cohort_counts = main_data['COHORT'].value_counts()
                        
                        # Get cohort labels from data dictionary
                        cohort_labels = {}
                        cohort_info = data_dict[data_dict['Variable'] == 'COHORT']
                        for _, row in cohort_info.iterrows():
                            if pd.notna(row['Code']) and pd.notna(row['Decode']):
                                # Handle both string and numeric codes
                                code_key = str(row['Code']).strip()
                                try:
                                    # Try to convert to int if it's a number
                                    if code_key.replace('.', '').isdigit():
                                        code_key = int(float(code_key))
                                except:
                                    pass
                                cohort_labels[code_key] = row['Decode']
                        
                        # Also map string versions of numeric codes
                        for key, value in list(cohort_labels.items()):
                            if isinstance(key, int):
                                cohort_labels[str(key)] = value
                            elif isinstance(key, str) and key.isdigit():
                                cohort_labels[int(key)] = value
                        
                        for code, count in cohort_counts.items():
                            label = cohort_labels.get(code, cohort_labels.get(str(code), f"Code {code}"))
                            st.metric(label, count)
                            
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
                st.info("Please ensure your Excel file has the correct format with data and dictionary sheets.")
            finally:
                # Clean up temporary file
                if 'data_path' in locals() and os.path.exists(data_path):
                    try:
                        os.unlink(data_path)
                    except:
                        pass  # Ignore cleanup errors
        
        # Navigation in sidebar
        if st.session_state.main_data is not None:
            st.header("📊 PPMI Data Navigation")
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
        else:
            # Show expected data structure
            with st.expander("📋 Expected PPMI Data Format"):
                st.markdown("""
                **Your PPMI Excel file should contain:**
                1. **Main Data Sheet** (default: "20250609"): Patient records with variables
                2. **Data Dictionary Sheet** (default: "Data dictionary"): Variable descriptions and codes
                
                **Data Dictionary Format:**
                - Variable: Variable names
                - Category: Variable categories
                - Description: Variable descriptions  
                - Code: Value codes
                - Decode: Code meanings
                """)
            page = None
    
    # Main content area (outside sidebar)
    if st.session_state.main_data is not None:
        main_data = st.session_state.main_data
        data_dict = st.session_state.data_dict
        variable_summary = st.session_state.variable_summary
        
        # Display the selected page content in main area
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
    else:
        # Welcome message in main area when no data is loaded
        st.info("👆 Please upload your PPMI Excel dataset using the sidebar to begin analysis")
        
        # Show some information about the dashboard
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📋 Dataset Overview")
            st.write("Comprehensive metrics and cohort analysis")
        
        with col2:
            st.subheader("� Variable Explorer")
            st.write("Search and analyze individual variables")
        
        with col3:
            st.subheader("🧠 Clinical Assessments")
            st.write("Explore clinical variables and assessments")

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
                
                # Create labels using the codes dictionary with robust type handling
                code_labels = {}
                for _, row in codes_data.iterrows():
                    if pd.notna(row['Code']) and pd.notna(row['Decode']):
                        # Handle both string and numeric codes
                        code_key = str(row['Code']).strip()
                        try:
                            # Try to convert to int if it's a number
                            if code_key.replace('.', '').isdigit():
                                code_key = int(float(code_key))
                        except:
                            pass
                        
                        # For COHORT and other important variables, use just the decode name
                        if variable == 'COHORT':
                            code_labels[code_key] = row['Decode']
                        else:
                            code_labels[code_key] = f"{row['Code']}: {row['Decode']}"
                
                # Also map string versions of numeric codes
                for key, value in list(code_labels.items()):
                    if isinstance(key, int):
                        code_labels[str(key)] = value
                    elif isinstance(key, str) and key.isdigit():
                        code_labels[int(key)] = value
                
                # Create labeled data
                labels = []
                for code in value_counts.index:
                    label = code_labels.get(code, code_labels.get(str(code), f"Code {code}"))
                    labels.append(label)
                
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
                
                fig.update_layout(title=f'{variable} - Distribution Analysis')
                st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Summary Statistics")
        if variable in data.columns:
            if data[variable].dtype in ['object', 'category']:
                st.write(data[variable].value_counts().head(10))
            else:
                st.write(data[variable].describe())
            
            # Missing values
            missing_count = data[variable].isnull().sum()
            missing_pct = (missing_count / len(data)) * 100
            st.metric("Missing Values", f"{missing_count} ({missing_pct:.1f}%)")
        else:
            st.warning("Variable not found in dataset")

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
                    # Handle both string and numeric codes
                    code_key = str(row['Code']).strip()
                    try:
                        # Try to convert to int if it's a number
                        if code_key.replace('.', '').isdigit():
                            code_key = int(float(code_key))
                    except:
                        pass
                    cohort_labels[code_key] = row['Decode']
            
            # Also map string versions of numeric codes
            for key, value in list(cohort_labels.items()):
                if isinstance(key, int):
                    cohort_labels[str(key)] = value
                elif isinstance(key, str) and key.isdigit():
                    cohort_labels[int(key)] = value
            
            # Create labeled data for visualization
            labels = []
            for code in cohort_counts.index:
                label = cohort_labels.get(code, cohort_labels.get(str(code), f"Code {code}"))
                labels.append(label)
            
            fig = px.pie(
                values=cohort_counts.values,
                names=labels,
                title="PPMI Cohort Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Cohort Statistics")
            for code, count in cohort_counts.items():
                label = cohort_labels.get(code, cohort_labels.get(str(code), f"Code {code}"))
                percentage = (count / len(data)) * 100
                st.metric(label, f"{count} ({percentage:.1f}%)")
    
    # Categories distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Variable Categories")
        category_counts = variable_summary['Category'].value_counts().head(10)
        fig = px.bar(
            x=category_counts.values,
            y=category_counts.index,
            orientation='h',
            title="Top Variable Categories",
            labels={'x': 'Count', 'y': 'Category'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Data Preview")
        st.dataframe(data.head(10), use_container_width=True)

def show_variable_categories(data, data_dict, variable_summary):
    """Browse variables by categories"""
    st.header("🏷️ Variable Categories Explorer")
    
    try:
        # Category selection
        categories = sorted(variable_summary['Category'].unique())
        selected_category = st.selectbox("Select a category to explore:", categories)
        
        if selected_category:
            # Filter variables by category
            category_vars = variable_summary[variable_summary['Category'] == selected_category]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader(f"📊 Variables in: {selected_category}")
                
                # Show ONLY essential info to avoid browser freeze
                # Remove the problematic All_Codes column that can be huge
                essential_display = category_vars[['Variable', 'Description', 'Codes_Count']].copy()
                
                # Truncate long descriptions to prevent display issues
                essential_display['Description'] = essential_display['Description'].str.slice(0, 100)
                essential_display.loc[essential_display['Description'].str.len() >= 100, 'Description'] += '...'
                
                st.dataframe(essential_display, use_container_width=True)
                
                # Show count info
                st.info(f"Showing {len(essential_display)} variables. Select one below for detailed analysis.")
            
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
                    try:
                        available_category_vars = category_vars['Variable'][category_vars['Variable'].isin(data.columns)]
                        if len(available_category_vars) > 0:
                            category_data = data[available_category_vars.tolist()[:5]]  # Limit to first 5 to avoid overload
                            missing_pct = (category_data.isnull().sum().sum() / (len(category_data) * len(category_data.columns))) * 100
                            st.metric("Category Completeness", f"{100 - missing_pct:.1f}%")
                    except Exception:
                        st.metric("Category Completeness", "Calculating...")
            
            # Variable analysis for this category
            st.subheader(f"📈 {selected_category} - Single Variable Analysis")
            
            available_vars = category_vars['Variable'][category_vars['Variable'].isin(data.columns)].tolist()
            
            if available_vars:
                # Limit options to prevent overload
                var_options = available_vars[:20]  # Show max 20 variables
                
                selected_var = st.selectbox(
                    "Select variable to analyze:", 
                    options=["--- Select a variable ---"] + var_options
                )
                
                if selected_var != "--- Select a variable ---":
                    st.markdown("---")
                    with st.spinner(f"Analyzing {selected_var}..."):
                        try:
                            analyze_single_variable(data, selected_var, data_dict)
                        except Exception as e:
                            st.error(f"Error analyzing {selected_var}: {str(e)}")
            else:
                st.warning(f"No variables from '{selected_category}' category found in the main dataset.")
    
    except Exception as e:
        st.error(f"Error in variable categories: {str(e)}")

def show_variable_explorer(data, data_dict, variable_summary):
    """Explore individual variables with descriptions"""
    st.header("🔍 Variable Explorer")
    
    # Search functionality
    search_term = st.text_input("🔍 Search variables by name or description:")
    
    if search_term:
        # Filter variables based on search
        filtered_vars = variable_summary[
            variable_summary['Variable'].str.contains(search_term, case=False, na=False) |
            variable_summary['Description'].str.contains(search_term, case=False, na=False)
        ]
        
        if not filtered_vars.empty:
            st.subheader(f"Search Results ({len(filtered_vars)} found)")
            available_vars = filtered_vars['Variable'][filtered_vars['Variable'].isin(data.columns)].tolist()
        else:
            st.warning("No variables found matching your search.")
            available_vars = []
    else:
        # Show all variables available in dataset
        available_vars = variable_summary['Variable'][variable_summary['Variable'].isin(data.columns)].tolist()
    
    if available_vars:
        # Variable selection
        selected_var = st.selectbox("Select a variable to explore:", 
                                  options=["--- Select a variable ---"] + available_vars[:50])  # Limit to 50
        
        if selected_var != "--- Select a variable ---":
            st.markdown("---")
            with st.spinner(f"Analyzing {selected_var}..."):
                try:
                    analyze_single_variable(data, selected_var, data_dict)
                except Exception as e:
                    st.error(f"Error analyzing {selected_var}: {str(e)}")
    else:
        st.info("No variables available. Please upload a dataset first.")

def show_clinical_assessments(data, data_dict, variable_summary):
    """Show clinical assessment analysis"""
    st.header("🧠 Clinical Assessments Analysis")
    
    # Very simple and safe approach
    st.info("This section analyzes clinical assessment variables from the PPMI dataset.")
    
    try:
        # Use a keyword-based approach which is more reliable
        clinical_keywords = ['updrs', 'hoehn', 'yahr', 'moca', 'mmse', 'diagnosis', 'age', 'gender', 'tremor', 'motor', 'cognitive']
        
        st.subheader("🔍 Clinical Variable Search")
        st.write("Available clinical keywords:", ", ".join(clinical_keywords))
        
        # Let user search by keyword
        search_keyword = st.selectbox(
            "Select a clinical assessment type to explore:",
            options=["--- Select keyword ---"] + clinical_keywords
        )
        
        if search_keyword != "--- Select keyword ---":
            # Find matching variables
            matching_vars = []
            for col in data.columns:
                if search_keyword.lower() in col.lower():
                    matching_vars.append(col)
            
            if matching_vars:
                st.subheader(f"📊 Variables containing '{search_keyword}'")
                st.write(f"Found {len(matching_vars)} variables:")
                
                # Show first 10 variables as simple list
                for i, var in enumerate(matching_vars[:10], 1):
                    st.write(f"{i}. `{var}`")
                
                if len(matching_vars) > 10:
                    st.write(f"... and {len(matching_vars) - 10} more")
                
                # Single variable selection for detailed analysis
                selected_var = st.selectbox(
                    f"Select a {search_keyword} variable to analyze in detail:",
                    options=["--- Select variable ---"] + matching_vars[:10]
                )
                
                if selected_var != "--- Select variable ---":
                    st.markdown("---")
                    with st.spinner(f"Analyzing {selected_var}..."):
                        try:
                            analyze_single_variable(data, selected_var, data_dict)
                        except Exception as e:
                            st.error(f"Error analyzing {selected_var}: {str(e)}")
            else:
                st.warning(f"No variables found containing '{search_keyword}'")
                st.info("Try a different keyword or use the Variable Explorer for more options.")
    
    except Exception as e:
        st.error(f"Error in clinical assessments: {str(e)}")
        st.info("Use the Variable Explorer to search for clinical variables manually.")

def show_data_quality(data, data_dict, variable_summary):
    """Show data quality analysis"""
    st.header("📊 Data Quality Report")
    
    # Missing data analysis
    st.subheader("❓ Missing Data Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Calculate missing data statistics
        missing_stats = []
        for col in data.columns:
            missing_count = data[col].isnull().sum()
            missing_pct = (missing_count / len(data)) * 100
            missing_stats.append({
                'Variable': col,
                'Missing_Count': missing_count,
                'Missing_Percentage': missing_pct
            })
        
        missing_df = pd.DataFrame(missing_stats)
        missing_df = missing_df.sort_values('Missing_Percentage', ascending=False)
        
        # Show top 20 variables with most missing data
        st.subheader("🔝 Variables with Most Missing Data")
        top_missing = missing_df.head(20)
        st.dataframe(top_missing, use_container_width=True)
    
    with col2:
        # Missing data visualization
        if len(missing_df) > 0:
            # Plot missing data percentages
            fig = px.histogram(
                missing_df, 
                x='Missing_Percentage',
                title='Distribution of Missing Data Percentages',
                labels={'Missing_Percentage': 'Missing Data %', 'count': 'Number of Variables'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            st.subheader("📈 Summary Statistics")
            total_vars = len(data.columns)
            complete_vars = len(missing_df[missing_df['Missing_Percentage'] == 0])
            high_missing_vars = len(missing_df[missing_df['Missing_Percentage'] > 50])
            
            st.metric("Total Variables", total_vars)
            st.metric("Complete Variables", f"{complete_vars} ({100*complete_vars/total_vars:.1f}%)")
            st.metric("High Missing (>50%)", f"{high_missing_vars} ({100*high_missing_vars/total_vars:.1f}%)")

def show_correlation_analysis(data):
    """Show correlation analysis between variables"""
    st.header("🔗 Correlation Analysis")
    
    # Select numeric columns
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) > 1:
        # Limit to first 50 numeric columns to avoid performance issues
        if len(numeric_cols) > 50:
            st.warning(f"Dataset has {len(numeric_cols)} numeric variables. Showing correlations for first 50 variables.")
            numeric_cols = numeric_cols[:50]
        
        # Correlation matrix
        with st.spinner("Calculating correlations..."):
            corr_matrix = data[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            title="Variable Correlation Heatmap",
            color_continuous_scale="RdBu_r",
            aspect="auto"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top correlations
        st.subheader("🔝 Strongest Correlations")
        corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_pairs.append({
                    'Variable 1': corr_matrix.columns[i],
                    'Variable 2': corr_matrix.columns[j],
                    'Correlation': corr_matrix.iloc[i, j]
                })
        
        corr_df = pd.DataFrame(corr_pairs)
        corr_df = corr_df.reindex(corr_df['Correlation'].abs().sort_values(ascending=False).index)
        st.dataframe(corr_df.head(20), use_container_width=True)
    else:
        st.warning("Not enough numeric variables for correlation analysis.")

def show_data_dictionary(data_dict, variable_summary):
    """Display the complete data dictionary"""
    st.header("📚 Data Dictionary Browser")
    
    if data_dict is not None and not data_dict.empty:
        # Variable summary view
        st.subheader("📋 Variable Summary")
        
        # Show summary with limited columns to prevent display issues
        display_summary = variable_summary[['Variable', 'Category', 'Description', 'Codes_Count']].copy()
        
        # Truncate long descriptions
        display_summary['Description'] = display_summary['Description'].str.slice(0, 150)
        display_summary.loc[display_summary['Description'].str.len() >= 150, 'Description'] += '...'
        
        st.dataframe(display_summary, use_container_width=True)
        
        # Search functionality
        st.subheader("🔍 Search Data Dictionary")
        search_term = st.text_input("Search variables, categories, or descriptions:")
        
        if search_term:
            # Search in variable summary first
            filtered_summary = variable_summary[
                variable_summary.apply(lambda x: x.astype(str).str.contains(search_term, case=False)).any(axis=1)
            ]
            
            if not filtered_summary.empty:
                st.subheader("Search Results")
                display_filtered = filtered_summary[['Variable', 'Category', 'Description', 'Codes_Count']].copy()
                display_filtered['Description'] = display_filtered['Description'].str.slice(0, 150)
                st.dataframe(display_filtered, use_container_width=True)
            else:
                st.warning("No results found for your search term.")
        
        # Detailed variable lookup
        st.subheader("🔍 Detailed Variable Lookup")
        all_variables = sorted(variable_summary['Variable'].unique())
        selected_var = st.selectbox(
            "Select variable for detailed codes:",
            options=["--- Select variable ---"] + all_variables[:100]  # Limit to 100
        )
        
        if selected_var != "--- Select variable ---":
            var_codes = data_dict[data_dict['Variable'] == selected_var]
            if not var_codes.empty:
                st.subheader(f"📝 Details for: {selected_var}")
                
                # Show basic info
                var_info = variable_summary[variable_summary['Variable'] == selected_var].iloc[0]
                st.info(f"**Category:** {var_info['Category']}\n\n**Description:** {var_info['Description']}")
                
                # Show codes
                codes_display = var_codes[['Code', 'Decode']].dropna()
                if not codes_display.empty:
                    st.subheader("🔑 Value Codes")
                    st.dataframe(codes_display, use_container_width=True)
                else:
                    st.info("No value codes available for this variable.")
    else:
        st.warning("No data dictionary found in the uploaded file.")

if __name__ == "__main__":
    main()