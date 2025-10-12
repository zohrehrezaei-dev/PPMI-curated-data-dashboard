import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from data_loader import DataLoader
from data_analyzer import DataAnalyzer
from visualization_utils import VisualizationUtils

# Page configuration
st.set_page_config(
    page_title="Parkinson's Disease Dataset Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🧠 Parkinson's Disease Dataset Dashboard")
    st.markdown("---")
    
    # Sidebar for file upload and navigation
    with st.sidebar:
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Upload your Excel file (.xlsx)", 
            type=['xlsx'],
            help="Upload your Parkinson's disease dataset with data dictionary"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            data_path = Path("data") / "temp_dataset.xlsx"
            data_path.parent.mkdir(exist_ok=True)
            
            with open(data_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success("✅ File uploaded successfully!")
            
            # Load data
            try:
                loader = DataLoader(data_path)
                main_data, data_dict = loader.load_data()
                
                # Navigation
                st.header("📊 Navigation")
                page = st.selectbox(
                    "Choose a page:",
                    ["Dataset Overview", "Variable Explorer", "Data Dictionary", 
                     "Correlation Analysis", "Missing Data Analysis"]
                )
                
                # Main content area
                if page == "Dataset Overview":
                    show_dataset_overview(main_data, data_dict)
                elif page == "Variable Explorer":
                    show_variable_explorer(main_data, data_dict)
                elif page == "Data Dictionary":
                    show_data_dictionary(data_dict)
                elif page == "Correlation Analysis":
                    show_correlation_analysis(main_data)
                elif page == "Missing Data Analysis":
                    show_missing_data_analysis(main_data)
                    
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
                st.info("Please ensure your Excel file has the correct format with data and dictionary sheets.")
        
        else:
            st.info("👆 Please upload your Excel dataset to begin analysis")
            
            # Show sample data structure
            with st.expander("📋 Expected Data Format"):
                st.markdown("""
                **Your Excel file should contain:**
                1. **Main Data Sheet**: Patient records with variables
                2. **Data Dictionary Sheet**: Variable descriptions and codes
                
                **Data Dictionary Format:**
                - Column 1: Variable Name
                - Column 2: Description
                - Column 3: Value Codes (optional)
                """)

def show_dataset_overview(data, data_dict):
    """Display dataset overview and basic statistics"""
    st.header("📊 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(data))
    with col2:
        st.metric("Total Variables", len(data.columns))
    with col3:
        st.metric("Missing Values", data.isnull().sum().sum())
    with col4:
        st.metric("Dictionary Entries", len(data_dict) if data_dict is not None else 0)
    
    st.subheader("📈 Data Preview")
    st.dataframe(data.head(10), use_container_width=True)
    
    st.subheader("📋 Basic Statistics")
    st.dataframe(data.describe(), use_container_width=True)

def show_variable_explorer(data, data_dict):
    """Explore individual variables with descriptions"""
    st.header("🔍 Variable Explorer")
    
    # Variable selection
    selected_var = st.selectbox("Select a variable to explore:", data.columns)
    
    if selected_var:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Variable description from dictionary
            if data_dict is not None and selected_var in data_dict.index:
                st.subheader(f"📝 Description: {selected_var}")
                st.info(data_dict.loc[selected_var, 'Description'])
                
                if 'Value_Codes' in data_dict.columns:
                    codes = data_dict.loc[selected_var, 'Value_Codes']
                    if pd.notna(codes):
                        st.subheader("🔑 Value Codes")
                        st.text(codes)
            
            # Visualization based on data type
            viz_utils = VisualizationUtils()
            if data[selected_var].dtype in ['object', 'category']:
                fig = viz_utils.create_categorical_plot(data, selected_var)
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = viz_utils.create_numeric_plot(data, selected_var)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Summary Statistics")
            if data[selected_var].dtype in ['object', 'category']:
                st.write(data[selected_var].value_counts())
            else:
                st.write(data[selected_var].describe())
            
            # Missing values
            missing_count = data[selected_var].isnull().sum()
            missing_pct = (missing_count / len(data)) * 100
            st.metric("Missing Values", f"{missing_count} ({missing_pct:.1f}%)")

def show_data_dictionary(data_dict):
    """Display the complete data dictionary"""
    st.header("📚 Data Dictionary")
    
    if data_dict is not None:
        st.dataframe(data_dict, use_container_width=True)
        
        # Search functionality
        search_term = st.text_input("🔍 Search variables or descriptions:")
        if search_term:
            filtered_dict = data_dict[
                data_dict.apply(lambda x: x.astype(str).str.contains(search_term, case=False)).any(axis=1)
            ]
            st.subheader("Search Results")
            st.dataframe(filtered_dict, use_container_width=True)
    else:
        st.warning("No data dictionary found in the uploaded file.")

def show_correlation_analysis(data):
    """Show correlation analysis between variables"""
    st.header("🔗 Correlation Analysis")
    
    # Select numeric columns
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) > 1:
        # Correlation matrix
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
        st.dataframe(corr_df.head(10), use_container_width=True)
    else:
        st.warning("Not enough numeric variables for correlation analysis.")

def show_missing_data_analysis(data):
    """Analyze missing data patterns"""
    st.header("❓ Missing Data Analysis")
    
    analyzer = DataAnalyzer()
    missing_summary = analyzer.analyze_missing_data(data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Missing Data Summary")
        st.dataframe(missing_summary, use_container_width=True)
    
    with col2:
        # Missing data heatmap
        fig = px.imshow(
            data.isnull().astype(int),
            title="Missing Data Pattern",
            labels=dict(color="Missing"),
            color_continuous_scale=["white", "red"]
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()