from dash import Dash, dcc, html 
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

# Initialize Dash app with Bootstrap dark theme
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[
    dbc.themes.CYBORG,
    dbc_css,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"  # Font Awesome for icons
])

# Load the template consistent styling
load_figure_template("SLATE")

# Load and preprocess data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2024/week-51/ors-limited-dataset.csv')

# Filter for sitting and standing jobs
df = df[
    (df['ESTIMATE TEXT'] == 'Hours of the day that workers were required to sit, mean') | 
    (df['ESTIMATE TEXT'] == 'Hours of the day that workers were required to stand, mean')
]

# Remove occupations with glitches
df = df[
    (df['OCCUPATION'] != 'Firefighters') & 
    (df['OCCUPATION'] != 'First-line supervisors of fire fighting and prevention workers')
]

# Convert 'ESTIMATE' column to numeric
df["ESTIMATE"] = pd.to_numeric(df["ESTIMATE"], errors='coerce')

# Separate data for sitting and standing
df_standing = df[df['ESTIMATE TEXT'] == 'Hours of the day that workers were required to stand, mean']
df_sitting = df[df['ESTIMATE TEXT'] == 'Hours of the day that workers were required to sit, mean']

# Helper function to create bar charts
def create_bar_chart(data, title, color_scale, cmin, cmax, icon_html):
    fig = px.bar(
        data,
        x='ESTIMATE',
        y='OCCUPATION',
        orientation='h',
        labels={'ESTIMATE': 'Average Hours', 'OCCUPATION': 'Occupation'},
        color='ESTIMATE',
        color_continuous_scale=color_scale
    )

    # Remove the color scale from the legend
    fig.update_layout(
        title={
            'text': f"{icon_html} {title}",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18}  # Font size for responsive titles
        },
        height=700,
        margin=dict(l=50, r=50, t=100, b=50),
        xaxis_tickfont=dict(size=17),
        yaxis_tickfont=dict(size=17),
        coloraxis_showscale=False,  # This removes the color scale from the legend
        showlegend=False  # Disable the legend
    )
    return fig

# Create the layout for the app
app.layout = dbc.Container([
    html.H1("Top Jobs for Standing and Sitting", style={'textAlign': 'center', 'color': 'white'}),
    html.Br(),

    # Dropdown to select occupation (Aligned to the left)
    dbc.Row([
        dbc.Col([ 
            html.H6("Select Occupation /not only form the TOP 10/", style={'color': 'white'}),
            dcc.Dropdown(
                id='occupation-dropdown',
                options=[{'label': occupation, 'value': occupation} for occupation in df['OCCUPATION'].unique()],
                multi=True,  # Allow multi-selection
                style={'width': '70%'}
            ),
        ], width={"size": 6}, style={'textAlign': 'left'}),  # Align to the left
    ], justify="start"),
    html.Br(),  # Align the dropdown to the left

    # KPI cards placed beside the dropdown
    dbc.Row([
        dbc.Col([ 
            dbc.Card([ 
                dbc.CardBody([ 
                    html.H3("Standing Hours", className="card-title", style={'textAlign': 'center'}),
                    html.H5(id='kpi-standing-hours', className="text-center", style={'color': 'white'})
                ])
            ], className="text-center")
        ], xs=12, sm=6, md=4, lg=3, xl=2),
        dbc.Col([ 
            dbc.Card([ 
                dbc.CardBody([ 
                    html.H3("Sitting Hours", className="card-title", style={'textAlign': 'center'}),
                    html.H5(id='kpi-sitting-hours', className="text-center", style={'color': 'white'})
                ])
            ], className="text-center")
        ], xs=12, sm=6, md=4, lg=3, xl=2)
    ], justify="center"),
    html.Br(),

    # Graph rows for sitting and standing (order swapped)
    dbc.Row([
        dbc.Col([ 
            dcc.Loading(
                type="circle", 
                children=[
                    dcc.Graph(id='graph-sitting', style={'height': '60vh'})  # Graph for sitting jobs
                ]
            )
        ], xs=12, sm=12, md=6, lg=6, xl=6),  # Responsive widths for graphs

        dbc.Col([ 
            dcc.Loading(
                type="circle", 
                children=[
                    dcc.Graph(id='graph-standing', style={'height': '60vh'})  # Graph for standing jobs
                ]
            )
        ], xs=12, sm=12, md=6, lg=6, xl=6),  # Responsive widths for graphs
    ], justify="center", align="center"),
], fluid=True)

# Define callback to update graphs and KPI based on dropdown selection
@app.callback(
    [Output('graph-standing', 'figure'),
     Output('graph-sitting', 'figure'),
     Output('kpi-sitting-hours', 'children'),
     Output('kpi-standing-hours', 'children')],
    [Input('occupation-dropdown', 'value')]
)
def update_graphs(selected_occupations):
    # Filter data based on selected occupations, default to top 10
    if selected_occupations:
        filtered_standing = df_standing[df_standing['OCCUPATION'].isin(selected_occupations)]
        filtered_sitting = df_sitting[df_sitting['OCCUPATION'].isin(selected_occupations)]
    else:
        # Get top 10 occupations for both sitting and standing, sorted in ascending order by ESTIMATE
        filtered_standing = df_standing.nsmallest(10, 'ESTIMATE')
        filtered_sitting = df_sitting.nsmallest(10, 'ESTIMATE')

    # Create the graph for standing jobs with reversed title (Top 10 Sitting Jobs)
    graph_figure_standing = create_bar_chart(
        filtered_standing, 
        "Top 10 Sitting Jobs",  # Reversed title
        ['pink', 'magenta'], 
        cmin=0, 
        cmax=8, 
        icon_html="🪑" 
    )

    # Create the graph for sitting jobs with reversed title (Top 10 Standing Jobs)
    graph_figure_sitting = create_bar_chart(
        filtered_sitting, 
        "Top 10 Standing Jobs",  # Reversed title
        ['lightblue', 'blue'], 
        cmin=0, 
        cmax=9, 
        icon_html="🧍" 
    )

    # Calculate total standing hours and sitting hours
    total_standing_hours = filtered_standing['ESTIMATE'].sum()
    total_sitting_hours = filtered_sitting['ESTIMATE'].sum()

    # Update KPI for hours
    return graph_figure_standing, graph_figure_sitting, f"{total_sitting_hours:.2f} Hours", f"{total_standing_hours:.2f} Hours"

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
