from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

# Load the dataset from the GitHub URL
url = "https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2024/week-52/SaaS-businesses-NYSE-NASDAQ.csv"
data = pd.read_csv(url)

# Clean and preprocess the data
data['Annualized Revenue'] = data['Annualized Revenue'].str.replace('[$,]', '', regex=True).astype(float)
data['Last Quarter Revenue'] = data['Last Quarter Revenue'].str.replace('[$,]', '', regex=True).astype(float)
data['YoY Growth%'] = data['YoY Growth%'].str.replace('%', '', regex=True).astype(float)

# Select the top 10 companies by Annualized Revenue
top_companies = data.nlargest(10, 'Annualized Revenue')

# Extract necessary data
companies = top_companies['Company']
last_quarter_revenue = top_companies['Last Quarter Revenue']
yoy_growth = top_companies['YoY Growth%']

# Create the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Create the figure
fig = go.Figure()

# Add bar chart for Last Quarter Revenue with gradient colors
fig.add_trace(
    go.Bar(
        x=companies,
        y=last_quarter_revenue,
        name="Last Quarter Revenue",
        marker=dict(
            color="green",
            showscale=False
        ),
    )
)

# Add line chart for YoY Growth%
fig.add_trace(
    go.Scatter(
        x=companies,
        y=yoy_growth,
        name="YoY Growth%",
        mode="lines+markers",
        line=dict(color="lightblue", width=3),
        marker=dict(size=10, color="lightblue"),
    )
)

# Min and Max annotations for "Last Quarter Revenue"
min_revenue_idx = last_quarter_revenue.idxmin()
max_revenue_idx = last_quarter_revenue.idxmax()

# Min and Max annotations for "YoY Growth%"
min_growth_idx = yoy_growth.idxmin()
max_growth_idx = yoy_growth.idxmax()

# Add annotations for min and max values
fig.update_layout(
    title="Last Quarter Revenue and YoY Growth% for Top 10 SaaS Companies",
    title_font=dict(size=24, color="white"),  # White title font color
    plot_bgcolor="black",  # Dark background
    paper_bgcolor="black",  # Paper background color (for surrounding area)
    xaxis=dict(
        title="", 
        tickangle=-15,
        titlefont=dict(size=20, color="white"),  # Larger font size for X-axis title
        tickfont=dict(size=20, color="white"),  # Larger font size for X-axis ticks
    ),
    yaxis=dict(
        title="Last Quarter Revenue (in billions)",
        titlefont=dict(size=20, color="lightgreen"),  # Larger font size for Y-axis title
        tickfont=dict(size=20, color="lightgreen"),  # Larger font size for Y-axis ticks
        showgrid=False,  # No gridlines
    ),
    yaxis2=dict(
        title="YoY Growth% (%)",
        titlefont=dict(size=20, color="lightblue"),  # Larger font size for Y2-axis title
        tickfont=dict(size=16, color="lightblue"),  # Larger font size for Y2-axis ticks
        overlaying="y",
        side="right",
        showgrid=False,  # No gridlines
    ),
    legend=dict(x=0.5, y=-0.3, orientation="h", font=dict(size=16, color="white")),
    height=1080,  # Full HD height
    width=1920,   # Full HD width
    barmode="group",
    annotations=[
        # Min/Max Annotations for Last Quarter Revenue
        dict(
            x=companies[min_revenue_idx],
            y=last_quarter_revenue[min_revenue_idx],
            xanchor="center",
            yanchor="bottom",
            text=f"Min Revenue: {last_quarter_revenue[min_revenue_idx]:,.2f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            ax=0,
            ay=-40,
            font=dict(size=18, color="green"),  # Increased font size
            bgcolor="lightgreen",  # Dark background with transparency
            bordercolor="green",  # Border color
            borderwidth=2,  # Border width
            opacity=1  # Fully opaque
        ),
        dict(
            x=companies[max_revenue_idx],
            y=last_quarter_revenue[max_revenue_idx],
            xanchor="center",
            yanchor="bottom",
            text=f"Max Revenue: {last_quarter_revenue[max_revenue_idx]:,.2f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            ax=0,
            ay=-40,
            font=dict(size=18, color="green"),  # Increased font size
            bgcolor="lightgreen",  # Dark background with transparency
            bordercolor="green",  # Border color
            borderwidth=2,  # Border width
            opacity=1  # Fully opaque
        ),
        # Min/Max Annotations for YoY Growth
        dict(
            x=companies[min_growth_idx],
            y=yoy_growth[min_growth_idx],
            xanchor="center",
            yanchor="bottom",
            text=f"Min Growth: {yoy_growth[min_growth_idx]:.2f}%",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            ax=0,
            ay=40,
            font=dict(size=18, color="blue"),  # Increased font size
            bgcolor="lightblue",  # Dark background with transparency
            bordercolor="blue",  # Border color
            borderwidth=2,  # Border width
            opacity=1  # Fully opaque
        ),
        dict(
            x=companies[max_growth_idx],
            y=yoy_growth[max_growth_idx],
            xanchor="center",
            yanchor="bottom",
            text=f"Max Growth: {yoy_growth[max_growth_idx]:.2f}%",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            ax=0,
            ay=-640,
            font=dict(size=18, color="blue"),  # Increased font size
            bgcolor="lightblue",  # Dark background with transparency
            bordercolor="blue",  # Border color
            borderwidth=2,  # Border width
            opacity=1  # Fully opaque
        ),
    ]
)

# Attach secondary y-axis for YoY Growth%
fig.update_traces(yaxis="y2", selector=dict(name="YoY Growth%"))

# App layout with centered chart
app.layout = dbc.Container(
    [
        html.Div(
            [
                html.H1(
                    "This visualization compares the top 10 SaaS companies (Year Founded 1987-2007)",
                
                    style={
                        'textAlign': 'center',  # Center align text
                        'color': 'white',  # White text color
                        'fontSize': 40,  # Larger font size for the summary
                        'marginBottom': '40px',
                        
                    }
                ),
                dcc.Graph(figure=fig)
            ],
            style={
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'center',  # Center vertically
                'alignItems': 'center',  # Center horizontally
                'height': '100vh',  # Full viewport height
            }
        )
    ],
    fluid=True,
    style={
        'backgroundColor': 'rgb(0,0,0,0.5)'  # Background color of the container
    }
)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
