from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import dash.dependencies

# Read data
df = pd.read_csv("https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2025/week-4/Post45_NEAData_Final.csv")
df['age of writer'] = df.nea_grant_year - df.birth_year

# Normalize gender labels
df['gender'] = df['gender'].str.strip().str.title()

# Define custom colors
color_map = {
    'Female': 'pink', 
    'Male': 'blue',     
}

# Create Dash app
app = Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("NEA Grant Data Dashboard 1996-2024 in US", style={"textAlign": "left", "marginLeft": "40px"}),  

    # Title for pie chart cross-filtering with larger font
    html.Div([  
        html.H5("Click on the Pie Chart to Filter Data:", style={"fontSize": "30px", "textAlign": "center", "marginBottom": "30px"}), 
    ]), 

    # Reset Filter Button
    html.Div([  
        html.Button("Reset Filters", id="reset-button", n_clicks=0, style={"fontSize": "20px", "textAlign": "center", "marginBottom": "20px", "padding": "10px 20px"}), 
    ], style={"textAlign": "center"}), 

    # Layout for Pie Chart, Histogram, Grant Bar Chart, and US State Treemap
    html.Div([  
        # Pie Chart (Gender Distribution)
        html.Div([dcc.Graph(id='gender-pie-chart')], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}), 

        # Histogram
        html.Div([dcc.Graph(id='age-histogram')], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),  
    ], style={'display': 'flex', 'justifyContent': 'space-between'}), 

    # Layout for Grant Bar Chart and US State Treemap side by side
    html.Div([
        # Grant Bar Chart
        html.Div([dcc.Graph(id='grant-bar-chart')], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

        # US State Treemap
        html.Div([dcc.Graph(id='us-state-treemap')], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ], style={'display': 'flex', 'justifyContent': 'space-between'}), 
])

# Callback to update all charts
@app.callback(
    [dash.dependencies.Output('age-histogram', 'figure'),
     dash.dependencies.Output('gender-pie-chart', 'figure'),
     dash.dependencies.Output('grant-bar-chart', 'figure'),
     dash.dependencies.Output('us-state-treemap', 'figure')],
    [dash.dependencies.Input('gender-pie-chart', 'clickData'),
     dash.dependencies.Input('grant-bar-chart', 'clickData'),
     dash.dependencies.Input('reset-button', 'n_clicks')]
)
def update_charts(pieClickData, barClickData, resetButton):
    # Initialize gender filter
    selected_gender = None

    # If the Reset Filters button was clicked, reset the filters
    if resetButton > 0:
        pieClickData = None
        barClickData = None

    # Determine gender filter from pie chart click
    if pieClickData is not None:
        selected_gender = pieClickData['points'][0]['label']

    # Filter data by gender if selected (from pie chart or bar chart)
    filtered_df = df
    if selected_gender:
        filtered_df = filtered_df[filtered_df['gender'] == selected_gender]

    # Handle Bar Chart Click (cross-filtering)
    if barClickData is not None:
        clicked_gender = barClickData['points'][0]['label']
        filtered_df = filtered_df[filtered_df['gender'] == clicked_gender]

    # Create Histogram (Age Distribution)
    age_histogram_fig = px.histogram(
        filtered_df,
        x='age of writer',
        nbins=20,
        title="Age Distribution of Writers",
        labels={'age of writer': 'Age of Writer'},
        color='gender',
        color_discrete_map=color_map
    )

    # Create Pie Chart (Gender Distribution)
    gender_counts = filtered_df['gender'].value_counts().reset_index()
    gender_counts.columns = ['gender', 'count']
    
    gender_pie_chart_fig = px.pie(
        gender_counts,
        names='gender',
        values='count',
        title="Gender Distribution",
        color='gender',
        color_discrete_map=color_map
    )

    # Create Bar Chart (Gender by Year)
    grant_counts = filtered_df.groupby(['nea_grant_year', 'gender']).size().reset_index(name='grant_count')

    grant_fig = px.bar(
        grant_counts,
        x='nea_grant_year',
        y='grant_count',
        color='gender',
        title=f"Grant Counts by Year (Stacked by Gender)",
        labels={"nea_grant_year": "Grant Year", "grant_count": "Number of Grants"},
        color_discrete_map=color_map,
        category_orders={"gender": ["Female", "Male"]},
        barmode='stack'
    )

    # Create Treemap for US States
    us_state_counts = filtered_df['us_state'].value_counts().reset_index()
    us_state_counts.columns = ['us_state', 'count']

    treemap_fig = px.treemap(
        us_state_counts,
        path=['us_state'],
        values='count',
        color='count',
        color_continuous_scale='Blues',
        hover_name='us_state',
        title="Grant Distribution Across US States"
    )

    # Set layout adjustments for Treemap
    treemap_fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=40, b=40)
    )

    return age_histogram_fig, gender_pie_chart_fig, grant_fig, treemap_fig

# Run app
if __name__ == "__main__":
    app.run(debug=True)
