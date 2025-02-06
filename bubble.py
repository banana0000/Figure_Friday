import plotly.express as px
import pandas as pd
from dash import Dash, dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import webbrowser

# Load dataset
df = pd.read_csv("https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2025/week-5/Steam%20Top%20100%20Played%20Games%20-%20List.csv")

# Data cleaning and conversion
df["Price"] = df["Price"].replace("Free To Play", 0.0)
df["Price"] = df["Price"].astype(str).str.replace("\u00a3", "", regex=False).astype(float)
df["Current Players"] = df["Current Players"].str.replace(",", "").astype(int)
df["Peak Today"] = df["Peak Today"].str.replace(",", "").astype(int)

# Keep only the top 10 games by Current Players
df = df.nlargest(50, "Current Players")

# Get the max and min values for annotation
max_price_row = df.loc[df["Price"].idxmax()]
min_price_row = df.loc[df["Price"].idxmin()]
max_players_row = df.loc[df["Current Players"].idxmax()]
min_players_row = df.loc[df["Current Players"].idxmin()]

# Create scatter plot
fig = px.scatter(
    df, x="Price", y="Current Players", size="Peak Today", color="Price",
    hover_data=["Name", "Price"],  # Add the game names as text
    size_max=70,
    color_continuous_scale="Plasma"
)

# Customize text positioning to be above the bubbles
fig.update_traces(
    textposition="middle center",  # Position text above the bubbles
    textfont_size=15,
    textfont_color="black"
)

# Add annotations for max and min values
fig.update_layout(
    annotations=[
        # Max Price
        dict(
            x=max_price_row['Price'],
            y=max_price_row['Current Players'],
            xref='x', yref='y',
            text=f"Max Price: £{max_price_row['Price']:.2f}",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-80,
            font=dict(size=30, color='white'),
            bgcolor='black',
            opacity=0.7
        ),
        # Min Price
        dict(
            x=min_price_row['Price'],
            y=min_price_row['Current Players'],
            xref='x', yref='y',
            text=f"Min Price: £{min_price_row['Price']:.2f}",
            showarrow=True,
            arrowhead=2,
            ax=250,
            ay=-40,
            font=dict(size=30, color='white'),
            bgcolor='black',
            opacity=0.7
        ),
        # Max Current Players
        dict(
            x=max_players_row['Price'],
            y=max_players_row['Current Players'],
            xref='x', yref='y',
            text=f"Max Players: {max_players_row['Current Players']}",
            showarrow=True,
            arrowhead=2,
            ax=400,
            ay=40,
            font=dict(size=30, color='white'),
            bgcolor='black',
            opacity=0.7
        ),
        # Min Current Players
        dict(
            x=min_players_row['Price'],
            y=min_players_row['Current Players'],
            xref='x', yref='y',
            text=f"Min Players: {min_players_row['Current Players']}",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-180,
            font=dict(size=30, color='white'),
            bgcolor='black',
            opacity=0.7
        )
    ],
    paper_bgcolor='lightgrey',  # Background color
    plot_bgcolor='white',
    width=1800,  # Set width (adjust as needed)
    height=900,
    xaxis=dict(
        showgrid=False,
        #gridcolor='lightgrey'  # Set gridline color to grey
    ),
    yaxis=dict(
        showgrid=False,
        #gridcolor='lightgrey',  # Set gridline color to grey
    ),
    xaxis_title="Price (in GBP)",
    title="Current Players vs. Price of Top 50 Steam Games"
)

# Dash app setup with Bootstrap theme
app = Dash()
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.H1('Steam Top 50 Played Games'),
                ),
            ],
            justify="center",
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.H2('Click on the bubbles to open the game store page!'),
                ),
            ],
            justify="center",
            align="center",
            style={'height': '10vh'},
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id='scatter-fig', figure=fig, clickData={})
                )
            ],
            justify="center",
            align="center",
            style={'height': '80vh'},
        ),
    ],
    fluid=True,
    style={
        'display': 'flex',
        'flexDirection': 'column',
        'height': '100vh',
        'justifyContent': 'center',
        'alignItems': 'center',
    }
)

@callback(
    Output('scatter-fig', 'figure'),
    Input('scatter-fig', 'clickData')
)
def open_link(clickData):
    if clickData:
        point = clickData['points'][0]
        game_name = point['customdata'][0]
        game_row = df[df['Name'] == game_name]
        if not game_row.empty and 'Store Link' in game_row.columns:
            webbrowser.open(game_row.iloc[0]['Store Link'])
    return fig

if __name__ == '__main__':
    app.run(debug=True)
