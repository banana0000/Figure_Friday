import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

# Load and process the data
df = pd.read_csv("https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2024/week-48/API_IT.NET.USER.ZS_DS2_en_csv_v2_2160.csv")
df_filtered = df[df["Country Name"].isin(["Angola", "Albania", "Andorra", "Argentina"])]  # Filter for specific countries

melted_data = pd.melt(
    df_filtered,
    id_vars=['Country Name'],
    var_name='Year',
    value_name='Quantity'
)

melted_data['Year'] = pd.to_numeric(melted_data['Year'], errors='coerce')
melted_data = melted_data.dropna(subset=['Year', 'Quantity'])

# Dash app setup
app = dash.Dash(__name__)

# Layout
app.layout = html.Div(
    style={'backgroundColor': '#1e1e1e', 'color': '#ffffff', 'padding': '20px'},
    children=[
        # Title below the summary
        html.Div(
            style={'display': 'flex', 'justify-content': 'flex-start', 'align-items': 'center', 'width': '100%'},
            children=[
                html.H1(
                    "Internet Users Over Time",
                    style={'font-size': '35px', 'font-family': 'Arial Black', 'color': '#ffffff'}
                )
            ]
        ),

        # Date range slider (top-right corner)
        html.Div(
            style={'display': 'flex', 'justify-content': 'flex-end', 'align-items': 'center', 'margin-bottom': '10px'},
            children=[
                html.Div(
                    style={'width': '30%'},
                    children=[
                        html.Label("Select Year Range:", style={'color': '#ffffff', 'font-size': '18px'}),
                        dcc.RangeSlider(
                            id='year-slider',
                            min=melted_data['Year'].min(),
                            max=melted_data['Year'].max(),
                            step=1,
                            marks={int(year): str(int(year)) for year in range(int(melted_data['Year'].min()), int(melted_data['Year'].max()) + 1, 5)},
                            value=[melted_data['Year'].min(), melted_data['Year'].max()]
                        )
                    ]
                )
            ]
        ),

        # Line chart with space between label and chart
        dcc.Graph(id='line-chart', style={'width': '100%', 'height': '75vh', 'margin-top': '10px'})
    ]
)

@app.callback(
    Output('line-chart', 'figure'),
    [Input('year-slider', 'value')]
)
def update_chart_and_summary(selected_year_range):
    # Filter data for the selected year range
    filtered_data = melted_data[
        (melted_data['Year'] >= selected_year_range[0]) & 
        (melted_data['Year'] <= selected_year_range[1])
    ]

    # Create the line chart with increased line thickness and smooth lines
    fig = px.line(
        filtered_data,
        x="Year",
        y="Quantity",
        color="Country Name",
        markers=True,
        line_shape="spline",  # Smooth lines
    )

    # Apply color for the lines
    fig.update_traces(
        line=dict(width=5), 
    )

    # Add annotations for the country name and percentage at the last point (without data label)
    for country in filtered_data['Country Name'].unique():
        country_data = filtered_data[filtered_data['Country Name'] == country]
        last_point = country_data[country_data['Year'] == country_data['Year'].max()].iloc[0]

        # Add annotation for the country name and percentage at the last point
        fig.add_annotation(
            x=last_point['Year'],
            y=last_point['Quantity'],
            text=f"{country}: {last_point['Quantity']:.0f}%",
            showarrow=True,
            arrowhead=0,
            ax=5,
            ay=-20,
            font=dict(size=14, color=px.colors.qualitative.Plotly[filtered_data['Country Name'].unique().tolist().index(country)]),
        )

    # Update layout for the title and legend removal
    fig.update_layout(
        hovermode='x unified',
        template='plotly_dark',
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        margin=dict(l=50, r=50, t=100, b=50),  # Adjust margin to accommodate the top legend
        legend=dict(
            visible=False  # Remove legend
        )
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
