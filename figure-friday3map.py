import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_ag_grid as dag

# Load your data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2025/week-3/ODL-Export-Countries.csv')

# Calculate the total funding globally for percentage calculation
total_funding = df['FA Financing $'].sum()

# Add a new column for percentage of total global funding
df['Percentage of Global Funding'] = (df['FA Financing $'] / total_funding) * 100

# Extract unique regions for the radio button options
unique_regions = ['All'] + df['Region'].unique().tolist()

# List of available color scales
color_scales = px.colors.named_colorscales()

# Predefined funding ranges for the dropdown
funding_ranges = [
    {'label': 'All', 'value': 'All'},
    {'label': 'Under $1M', 'value': '0-1000000'},
    {'label': '$1M - $10M', 'value': '1000000-10000000'},
    {'label': '$10M - $50M', 'value': '10000000-50000000'},
    {'label': '$50M+', 'value': '50000000-1000000000'}
]

# Function to filter the dataframe by region and funding range
def filter_data(region, funding_range):
    filtered_df = df[df['Region'] == region] if region and region != 'All' else df
    
    if funding_range != 'All':
        min_funding, max_funding = map(int, funding_range.split('-'))
        filtered_df = filtered_df[(filtered_df['FA Financing $'] >= min_funding) & (filtered_df['FA Financing $'] < max_funding)]
    
    return filtered_df

# Function to create the choropleth map
def create_map(selected_region=None, selected_color_scale='deep', funding_range='All'):
    filtered_df = filter_data(selected_region, funding_range)
    
    fig = px.choropleth(
        data_frame=filtered_df,
        locations='ISO3',
        color='FA Financing $',
        hover_name='Country Name',
        title='',
        color_continuous_scale=selected_color_scale,
        hover_data={
            'FA Financing $': ':,.2f',
            'Country Name': True,
            'Percentage of Global Funding': ':.2f'
        }
    )

    fig.update_layout(
        geo=dict(
            projection_type='robinson',
            showcoastlines=True,
            coastlinecolor='Black',
            showland=True,
            landcolor='lightgray',
            showocean=True,
            oceancolor='whitesmoke',
        ),
        coloraxis_colorbar=dict(
            title='Funding ($)', 
            tickprefix='$',
            ticks='outside',
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            len=0.4,
        ),
        margin={"r":0,"t":50,"l":0,"b":0},
        height=800,
    )
    return fig

# Load the projects dataset
projects_df = pd.read_excel('ODL-Export-projects-1737305653693.xlsx')

# Create a mapping of ISO3 to country names
iso3_to_country = dict(zip(df['ISO3'], df['Country Name']))

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div(
    style={'display': 'flex', 'flexDirection': 'column'},
    children=[
        html.Div(
            style={'textAlign': 'center', 'padding': '20px'},
            children=[
                html.H1(
                    "Green Climate Fund Activities by Countries",
                    style={'fontSize': '40px', 'fontWeight': 'bold'}
                )
            ]
        ),
        html.Div(
            style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'center', 'alignItems': 'center', 'padding': '10px'},
            children=[
                html.Div(
                    style={'padding': '0 20px'},
                    children=[
                        html.H3('Select Region', style={'textAlign': 'center', 'fontSize': '24px'}),
                        dcc.RadioItems(
                            id='region-radio',
                            options=[{'label': region, 'value': region} for region in unique_regions],
                            value='All',
                            labelStyle={'display': 'inline-block', 'fontSize': '20px', 'margin': '10px', 'padding': '5px'},
                            style={'fontSize': '24px', 'textAlign': 'center'}
                        ),
                    ]
                ),
                html.Div(
                    style={'padding': '0 20px'},
                    children=[
                        html.H3('Select Color Scale', style={'textAlign': 'center', 'fontSize': '24px'}),
                        dcc.Dropdown(
                            id='color-scale-dropdown',
                            options=[{'label': scale, 'value': scale} for scale in color_scales],
                            value='deep',
                            style={'fontSize': '20px'}
                        ),
                    ]
                ),
                html.Div(
                    style={'padding': '0 20px'},
                    children=[
                        html.H3('Select Funding Range', style={'textAlign': 'center', 'fontSize': '24px'}),
                        dcc.Dropdown(
                            id='funding-range-dropdown',
                            options=funding_ranges,
                            value='All',
                            style={'fontSize': '20px'}
                        ),
                    ]
                ),
            ]
        ),
        html.Div(
            style={'padding': '20px'},
            children=[
                dcc.Graph(id='funding-map', figure=create_map('All', 'deep', 'All')),
                dcc.Link(
                    "Source: UNEP", 
                    target="_blank", 
                    href="https://www.unep.org/about-un-environment/funding-and-partnerships/green-climate-fund",
                    style={'fontSize': '20px', 'display': 'block', 'textAlign': 'center', 'marginTop': '20px'}
                ),
            ]
        ),
        html.Div(
            style={'padding': '20px'},
            children=[
                html.H2("Funding Activities by Country"),
                dag.AgGrid(
                    id='funding-activities-grid',
                    columnDefs=[{'headerName': col, 'field': col} for col in projects_df.columns],
                    rowData=projects_df.to_dict('records'),
                    dashGridOptions={'pagination': True, 'paginationPageSize': 20},
                    style={'height': '400px', 'width': '100%'}
                )
            ]
        )
    ]
)

# Callback to update the map dynamically based on region, color scale, and funding range
@app.callback(
    Output('funding-map', 'figure'),
    [Input('region-radio', 'value'),
     Input('color-scale-dropdown', 'value'),
     Input('funding-range-dropdown', 'value')]
)
def update_map(selected_region, selected_color_scale, funding_range):
    return create_map(selected_region, selected_color_scale, funding_range)

# Callback to update the AG Grid based on map click
@app.callback(
    Output('funding-activities-grid', 'rowData'),
    [Input('funding-map', 'clickData')]
)
def update_ag_grid(clickData):
    if clickData:
        # Extract the ISO3 code from the clicked country
        clicked_country_iso3 = clickData['points'][0]['location']
        # Map ISO3 to country name
        clicked_country_name = iso3_to_country.get(clicked_country_iso3)
        
        if clicked_country_name:
            # Filter projects_df using country name
            filtered_df = projects_df[projects_df['Countries'] == clicked_country_name]
            return filtered_df.to_dict('records')
    return projects_df.to_dict('records')

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
