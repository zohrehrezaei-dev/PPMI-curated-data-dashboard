# Configuration file for the Parkinson's Disease Dashboard

# Application settings
APP_CONFIG = {
    'title': 'Parkinson\'s Disease Dataset Dashboard',
    'page_icon': '🧠',
    'layout': 'wide',
    'max_file_size_mb': 100,
    'supported_formats': ['.xlsx', '.xls']
}

# Data processing settings
DATA_CONFIG = {
    'max_categories_for_plot': 20,
    'sample_size_for_heatmap': 1000,
    'missing_data_threshold': 0.5,  # 50% missing threshold for warnings
    'correlation_threshold': 0.3     # Minimum correlation to highlight
}

# Parkinson's disease specific keywords for relevance detection
PARKINSON_KEYWORDS = [
    'parkinson', 'pd', 'motor', 'tremor', 'rigidity', 'bradykinesia',
    'dopamine', 'levodopa', 'dopa', 'updrs', 'hoehn', 'yahr',
    'gait', 'balance', 'freezing', 'dyskinesia', 'cognitive',
    'depression', 'anxiety', 'sleep', 'olfactory', 'constipation',
    'rbd', 'rem', 'substantia', 'nigra', 'alpha-synuclein',
    'schwab', 'england', 'adl', 'activities', 'daily', 'living',
    'mmse', 'moca', 'pigd', 'postural', 'instability'
]

# Data dictionary keywords for sheet identification
DICTIONARY_KEYWORDS = [
    'dictionary', 'dict', 'metadata', 'variables', 'codebook', 
    'legend', 'description', 'variable_info', 'data_dict'
]

# Column name patterns for automatic identification
COLUMN_PATTERNS = {
    'variable_name': ['variable', 'var', 'name', 'column', 'field'],
    'description': ['description', 'desc', 'meaning', 'definition', 'label'],
    'value_codes': ['value', 'code', 'category', 'level', 'encoding', 'values']
}

# Visualization settings
VIZ_CONFIG = {
    'color_palette': [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ],
    'primary_color': '#1f77b4',
    'secondary_color': '#ff7f0e',
    'height_default': 400,
    'height_large': 600
}