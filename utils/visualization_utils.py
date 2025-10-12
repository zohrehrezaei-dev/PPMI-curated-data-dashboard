import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st

class VisualizationUtils:
    """Utility class for creating interactive visualizations"""
    
    def __init__(self):
        # Define a consistent color palette
        self.color_palette = px.colors.qualitative.Set3
        self.primary_color = '#1f77b4'
        self.secondary_color = '#ff7f0e'
    
    def create_categorical_plot(self, data, column):
        """Create appropriate plot for categorical variables"""
        value_counts = data[column].value_counts()
        
        if len(value_counts) <= 20:  # Bar chart for reasonable number of categories
            fig = px.bar(
                x=value_counts.index, 
                y=value_counts.values,
                title=f'Distribution of {column}',
                labels={'x': column, 'y': 'Count'},
                color_discrete_sequence=[self.primary_color]
            )
            fig.update_layout(xaxis_tickangle=45)
        else:  # Just show top 20 categories
            top_values = value_counts.head(20)
            fig = px.bar(
                x=top_values.index, 
                y=top_values.values,
                title=f'Top 20 Categories in {column}',
                labels={'x': column, 'y': 'Count'},
                color_discrete_sequence=[self.primary_color]
            )
            fig.update_layout(xaxis_tickangle=45)
        
        return fig
    
    def create_numeric_plot(self, data, column):
        """Create appropriate plot for numeric variables"""
        # Create subplot with histogram and box plot
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=[f'Distribution of {column}', f'Box Plot of {column}'],
            vertical_spacing=0.12
        )
        
        # Histogram
        fig.add_trace(
            go.Histogram(
                x=data[column].dropna(),
                name='Distribution',
                marker_color=self.primary_color,
                opacity=0.7
            ),
            row=1, col=1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(
                y=data[column].dropna(),
                name='Box Plot',
                marker_color=self.secondary_color
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            title_text=f'Analysis of {column}',
            showlegend=False
        )
        
        return fig
    
    def create_correlation_heatmap(self, data, title="Correlation Matrix"):
        """Create correlation heatmap for numeric variables"""
        numeric_data = data.select_dtypes(include=[np.number])
        
        if len(numeric_data.columns) < 2:
            st.warning("Not enough numeric variables for correlation analysis")
            return None
        
        corr_matrix = numeric_data.corr()
        
        fig = px.imshow(
            corr_matrix,
            title=title,
            color_continuous_scale='RdBu_r',
            aspect='auto',
            text_auto=True
        )
        
        fig.update_layout(
            width=800,
            height=600
        )
        
        return fig
    
    def create_missing_data_heatmap(self, data, title="Missing Data Pattern"):
        """Create heatmap showing missing data patterns"""
        # Sample data if too large
        if len(data) > 1000:
            sample_data = data.sample(n=1000, random_state=42)
        else:
            sample_data = data
        
        missing_matrix = sample_data.isnull().astype(int)
        
        fig = px.imshow(
            missing_matrix,
            title=title,
            labels=dict(color="Missing"),
            color_continuous_scale=["white", "red"],
            aspect='auto'
        )
        
        fig.update_layout(
            xaxis_title="Variables",
            yaxis_title="Records",
            height=400
        )
        
        return fig
    
    def create_parkinson_relevance_chart(self, relevance_df):
        """Create chart showing Parkinson's disease relevance scores"""
        if relevance_df.empty:
            return None
        
        # Take top 20 most relevant variables
        top_relevant = relevance_df.head(20)
        
        fig = px.bar(
            top_relevant,
            x='Relevance_Score',
            y='Variable',
            orientation='h',
            title='Variables Most Relevant to Parkinson\'s Disease',
            labels={'Relevance_Score': 'Relevance Score', 'Variable': 'Variable'},
            color='Relevance_Score',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            height=max(400, len(top_relevant) * 25),
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    def create_data_quality_dashboard(self, data):
        """Create a comprehensive data quality dashboard"""
        # Calculate metrics
        total_cells = len(data) * len(data.columns)
        missing_cells = data.isnull().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Data Completeness by Variable',
                'Data Types Distribution',
                'Missing Values Heatmap',
                'Variable Cardinality'
            ],
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "heatmap"}, {"type": "scatter"}]]
        )
        
        # 1. Data completeness by variable
        completeness_by_var = ((len(data) - data.isnull().sum()) / len(data)) * 100
        fig.add_trace(
            go.Bar(
                x=completeness_by_var.index,
                y=completeness_by_var.values,
                name='Completeness %',
                marker_color=self.primary_color
            ),
            row=1, col=1
        )
        
        # 2. Data types distribution
        dtype_counts = data.dtypes.astype(str).value_counts()
        fig.add_trace(
            go.Pie(
                labels=dtype_counts.index,
                values=dtype_counts.values,
                name='Data Types'
            ),
            row=1, col=2
        )
        
        # 3. Missing values pattern (sample)
        if len(data) > 100:
            sample_data = data.sample(n=100, random_state=42)
        else:
            sample_data = data
        
        missing_matrix = sample_data.isnull().astype(int)
        fig.add_trace(
            go.Heatmap(
                z=missing_matrix.values,
                x=missing_matrix.columns,
                y=list(range(len(missing_matrix))),
                colorscale=[[0, 'white'], [1, 'red']],
                name='Missing Pattern'
            ),
            row=2, col=1
        )
        
        # 4. Variable cardinality
        cardinality = [data[col].nunique() for col in data.columns]
        fig.add_trace(
            go.Scatter(
                x=list(range(len(data.columns))),
                y=cardinality,
                mode='markers',
                text=data.columns,
                name='Unique Values',
                marker=dict(
                    size=8,
                    color=cardinality,
                    colorscale='Viridis',
                    showscale=True
                )
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text=f"Data Quality Dashboard - Overall Completeness: {completeness:.1f}%",
            showlegend=False
        )
        
        return fig
    
    def create_variable_comparison_plot(self, data, var1, var2):
        """Create comparison plot between two variables"""
        if data[var1].dtype in ['object', 'category'] and data[var2].dtype in ['object', 'category']:
            # Categorical vs Categorical - Stacked bar or heatmap
            crosstab = pd.crosstab(data[var1], data[var2])
            
            fig = px.imshow(
                crosstab,
                title=f'{var1} vs {var2}',
                labels=dict(color="Count"),
                aspect='auto'
            )
            
        elif data[var1].dtype in ['object', 'category']:
            # Categorical vs Numeric - Box plot
            fig = px.box(
                data,
                x=var1,
                y=var2,
                title=f'{var2} by {var1}'
            )
            fig.update_layout(xaxis_tickangle=45)
            
        elif data[var2].dtype in ['object', 'category']:
            # Numeric vs Categorical - Box plot
            fig = px.box(
                data,
                x=var2,
                y=var1,
                title=f'{var1} by {var2}'
            )
            fig.update_layout(xaxis_tickangle=45)
            
        else:
            # Numeric vs Numeric - Scatter plot
            fig = px.scatter(
                data,
                x=var1,
                y=var2,
                title=f'{var1} vs {var2}',
                trendline='ols'
            )
        
        return fig