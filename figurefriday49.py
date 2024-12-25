import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
from datetime import date

# Load and process the data
data = pd.read_csv("https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2024/week-49/megawatt_demand_2024.csv")
data['Local Timestamp'] = pd.to_datetime(data['Local Timestamp Eastern Time (Interval Beginning)'])

regions = [
    "Connecticut Actual Load (MW)", "Maine Actual Load (MW)",
    "New Hampshire Actual Load (MW)", "Northeast Massachusetts Actual Load (MW)",
    "Rhode Island Actual Load (MW)", "Southeast Massachusetts Actual Load (MW)",
    "Vermont Actual Load (MW)", "Western/Central Massachusetts Actual Load (MW)"
]

# Initialize the Dash app
app = dash.Dash()

# Layout of the app
app.layout = html.Div(
    style={
        'backgroundColor': '#111111',
        'color': '#FFFFFF',
        'padding': '10px',
        'width': '100%',
        'height': '100vh',
        'overflow': 'hidden',
        'display': 'flex',
        'flexDirection': 'column'
    },
    children=[
        # Title and controls
        html.Div(
            style={
                'flex': '0 0 auto',
                'marginBottom': '10px',
                'display': 'flex',
                'alignItems': 'center'
            },
            children=[
                html.H1(id="graph-title",
                        style={
                            'fontSize': '38px',
                            'marginRight': '10px',
                            'textAlign': 'left',
                            'flex': '0 0 auto'
                        }),
            ]
        ),
        
        # Date picker single with dark background
        html.Div(
            style={'flex': 'flex-start', 'marginBottom': '10px'},
            children=[
                dcc.DatePickerSingle(
                    id='date-picker',
                    date=date(2024, 10, 1),  # Default date
                    min_date_allowed=data['Local Timestamp'].min().date(),
                    max_date_allowed=data['Local Timestamp'].max().date(),
                    display_format='YYYY-MM-DD',
                    style={
                        'color': 'black',
                        'padding': '5px',
                        'width': '500px'
                    },
                    calendar_orientation='horizontal'
                )
            ]
        ),

        # Region selector using checkboxes
        html.Div(
            style={
                'flex': '0 0 auto',
                'marginBottom': '20px',
                'display': 'flex',
                'flexWrap': 'wrap',
                'alignItems': 'center'
            },
            children=[
                dcc.Checklist(
                    id='region-checkbox',
                    options=[{'label': region.split(' ')[0], 'value': region} for region in regions],
                    value=["Connecticut Actual Load (MW)", "Maine Actual Load (MW)"],  # Default selected regions
                    style={
                        'display': 'flex',
                        'flexDirection': 'row',
                        'alignItems': 'center',
                        'flexWrap': 'wrap'
                    },
                    inputStyle={'marginRight': '5px', 'width': '20px', 'height': '20px'},
                    labelStyle={'margin': '5px', 'color': 'white', 'fontSize': '16px'}
                ),
            ]
        ),
        
        # Graph section
        html.Div(
            style={
                'flex': '1 1 auto',
                'marginTop': '10px'
            },
            children=[
                dcc.Graph(id='demand-graph', style={'height': '70vh', 'width': '100%'})
            ]
        )
    ]
)

# Callback to update the graph and the dynamic title
@app.callback(
    [Output('demand-graph', 'figure'),
     Output('graph-title', 'children')],
    [Input('region-checkbox', 'value'),
     Input('date-picker', 'date')]
)
def update_graph_and_title(selected_regions, selected_date):
    # Filter data for the selected date
    filtered_data = data[data['Local Timestamp'].dt.date == pd.to_datetime(selected_date).date()]

    fig = go.Figure()

    if selected_regions:
        for region in selected_regions:
            fig.add_trace(go.Scatter(
                x=filtered_data['Local Timestamp'],
                y=filtered_data[region],
                mode='lines',
                stackgroup='one',
                name=region.split(' ')[0],
                line_shape='spline',
                line_width=5
            ))
        # Create a dynamic title based on selected regions
        title = f"Hourly Demand for: {', '.join([region.split(' ')[0] for region in selected_regions])} on {selected_date}"
    else:
        title = "Select at least one region to display data"
        fig.add_annotation(
            text=title,
            xref="paper", yref="paper",
            x=0.5, y=1,
            showarrow=False,
            font=dict(size=16, color="white")
        )

    fig.update_layout(
        title="",
        title_font_size=20,
        title_x=0,
        title_xanchor='left',
        yaxis_title='Megawatts (MW)',  
        xaxis_title=None,
        legend_title="Regions",
        legend_title_font_size=14,
        template="plotly_dark",
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )

    return fig, title

if __name__ == '__main__':
    app.run_server(debug=True)
