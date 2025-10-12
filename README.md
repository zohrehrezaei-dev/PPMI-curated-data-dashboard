# Parkinson's Disease Dataset Dashboard

A comprehensive web-based dashboard for exploring and analyzing Parkinson's disease datasets with integrated data dictionary functionality.

## Features

- 📊 **Interactive Data Exploration**: Upload Excel files and explore your dataset through an intuitive web interface
- 📚 **Data Dictionary Integration**: Automatically detect and integrate data dictionaries for variable descriptions
- 🔍 **Variable Explorer**: Detailed analysis of individual variables with visualizations and statistics
- 🧠 **Parkinson's Disease Focus**: Automatic identification of variables relevant to Parkinson's disease research
- 📈 **Advanced Visualizations**: Interactive plots using Plotly for better data understanding
- 🔗 **Correlation Analysis**: Discover relationships between variables
- ❓ **Missing Data Analysis**: Comprehensive analysis of data completeness patterns
- 📋 **Data Quality Reports**: Automated assessment of dataset quality

## Installation

1. **Clone or download this project**
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the dashboard**:
   ```bash
   streamlit run src/main.py
   ```

2. **Open your browser** and navigate to the displayed URL (typically `http://localhost:8501`)

3. **Upload your Excel file** using the sidebar file uploader

4. **Explore your data** through the different pages:
   - **Dataset Overview**: Basic statistics and data preview
   - **Variable Explorer**: Detailed analysis of individual variables
   - **Data Dictionary**: Browse variable descriptions and codes
   - **Correlation Analysis**: Discover variable relationships
   - **Missing Data Analysis**: Analyze data completeness patterns

## Expected Data Format

Your Excel file should contain:
- **Main Data Sheet**: Patient records with variables (columns) and observations (rows)
- **Data Dictionary Sheet** (optional but recommended): Variable descriptions with columns:
  - Variable Name
  - Description
  - Value Codes (optional)

The dashboard will automatically detect which sheets contain your main data and data dictionary based on sheet names and content.

## Project Structure

```
├── src/
│   └── main.py                 # Main Streamlit application
├── utils/
│   ├── data_loader.py          # Excel data loading and preprocessing
│   ├── data_analyzer.py        # Data analysis and quality assessment
│   └── visualization_utils.py  # Interactive visualization functions
├── config/
│   └── settings.py             # Configuration and constants
├── data/
│   └── (uploaded files stored here temporarily)
└── requirements.txt            # Python dependencies
```

## Technologies Used

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **OpenPyXL**: Excel file handling
- **NumPy/SciPy**: Numerical computing
- **Scikit-learn**: Machine learning utilities (for future features)

## Parkinson's Disease Specific Features

The dashboard includes specialized functionality for Parkinson's disease research:

- **Automatic Variable Relevance Detection**: Uses medical keywords to identify variables likely related to Parkinson's disease
- **Clinical Scale Recognition**: Recognizes common assessment scales (UPDRS, Hoehn & Yahr, etc.)
- **Motor/Non-motor Classification**: Helps categorize variables by clinical domain
- **Research-Ready Analysis**: Prepares data for machine learning and statistical analysis

## Future Enhancements

- Machine learning model integration for predictions
- Advanced statistical analysis tools
- Export functionality for processed datasets
- Multi-dataset comparison capabilities
- Clinical trial specific analysis modules

## Support

For questions or issues:
1. Check that your Excel file follows the expected format
2. Ensure all dependencies are properly installed
3. Verify that your dataset contains the expected data types

---

**Note**: This dashboard is designed for research and educational purposes. Always validate results and consult with domain experts for clinical interpretations.