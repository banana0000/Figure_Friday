import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Load and preprocess the data
df = pd.read_csv('https://raw.githubusercontent.com/banana0000/NYC_Marathon2024/refs/heads/main/NYCMaraton2024.csv')

# Convert `pace` column from string format (minutes:seconds) to numeric (float) in minutes
def convert_pace_to_minutes(pace_str):
    try:
        minutes, seconds = map(int, pace_str.split(':'))
        return minutes + seconds / 60
    except ValueError:
        return None

# Apply conversion to the `pace` column
df['pace_minutes'] = df['pace'].apply(convert_pace_to_minutes)

# Drop rows where `pace_minutes` could not be calculated
# Create a copy of the filtered data to avoid "SettingWithCopyWarning"
cleaned_data = df[df['pace_minutes'].notna()].copy()

# Define age groups
bins = [10, 20, 30, 40, 50, 60, 70, 80, 90]
labels = ['10-20', '20-30', '30-40', '40-50', '50-60', '60-70', '70-80', '80-90']

# Create a new column for age groups (make sure we use .loc to avoid warnings)
cleaned_data.loc[:, 'age_group'] = pd.cut(cleaned_data['age'], bins=bins, labels=labels, right=False)

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

# Layout of the app with the full HD violin plot
app.layout = dbc.Container([
    # Title row with centered alignment
    dbc.Row([
        dbc.Col(html.H1("NYC Marathon 2024 Age Groups", style={'textAlign': 'center'}), width=12)
    ], style={'marginBottom': '20px', 'justifyContent': 'center'}),  # Center the row
    
    # Dropdown for Age Groups
    dbc.Row([
        dbc.Col([ 
            dcc.Dropdown(
                id='age-group-dropdown', 
                options=[{'label': age, 'value': age} for age in labels] + [{'label': 'All', 'value': 'All'}],
                value='None',
                clearable=False,
                placeholder="Select Age Group",
                style={'width': '100%'}
            ),
        ], width=6)
    ], style={'marginBottom': '20px', 'justifyContent': 'center', 'textAlign': 'center'}),  # Center the row
    
    # Row for KPI Cards in a single row centered and smaller
    dbc.Row([
        dbc.Col([  # First KPI: Total Runners
            dbc.Card([
                dbc.CardHeader("Total Runners", style={'fontSize': '18px', 'textAlign': 'center'}),
                dbc.CardBody([
                    html.Div(id='name-kpi', style={'fontSize': '20px', 'fontWeight': 'bold', 'textAlign': 'center'})
                ])
            ], style={'width': '12rem', 'padding': '10px', 'margin': 'auto', 'borderRadius': '10px'})
        ], width=2),
        
        dbc.Col([  # Second KPI: Average Pace (min/mile)
            dbc.Card([
                dbc.CardHeader("Average Pace", style={'fontSize': '18px', 'textAlign': 'center'}),
                dbc.CardBody([
                    html.Div(id='average-pace-kpi', style={'fontSize': '20px', 'fontWeight': 'bold', 'textAlign': 'center'})
                ])
            ], style={'width': '12rem', 'padding': '10px', 'margin': 'auto', 'borderRadius': '10px'})
        ], width=2)
    ], className='justify-content-center'),  # Center the cards row
    
    # Graph for Violin Plot
    dbc.Row([
        dbc.Col(dcc.Graph(id='pace-violin-plot', style={'height': '80vh', 'width': '100%'}), width=12)
    ])
])

# Callback to update the graph and the KPI cards based on selected age group
@app.callback(
    [Output('pace-violin-plot', 'figure'),
     Output('name-kpi', 'children'),
     Output('average-pace-kpi', 'children')],
    [Input('age-group-dropdown', 'value')]
)
def update_graph(selected_age_group):
    filtered_data = cleaned_data
    
    # Filter by age group
    if selected_age_group != 'All':
        filtered_data = filtered_data[filtered_data['age_group'] == selected_age_group]
    
    # Set title based on the filters
    if selected_age_group == 'All':
        title = 'Distribution of Minutes per Mile, by Gender'
    else:
        title = f'Distribution of Minutes per Mile, Age Group: {selected_age_group}'
    
    # Calculate the KPIs
    name_kpi = len(filtered_data['firstName'].unique()) if not filtered_data.empty else 0  # Count of unique first names
    average_pace_kpi = filtered_data['pace_minutes'].mean() if not filtered_data.empty else 0  # Average pace in minutes per mile
    
    # Custom color palette for gender
    custom_colors = ['black', 'violet', 'orange']  # Blue for 'Male', Orange for 'Female'
    
    # Create the violin plot
    fig = px.violin(
        filtered_data,
        y='pace_minutes',
        color='gender',
        hover_data=df.columns,
        title=title,
        violinmode='overlay',
        color_discrete_sequence=custom_colors  # Apply custom color palette
    )
    
    # Return the figure and the KPI values for all cards
    return fig, f'{name_kpi}', f'{average_pace_kpi:.2f} min/mile'

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
