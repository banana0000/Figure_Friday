from dash import Dash, dcc, html, callback, Output, Input, State, ALL
import plotly.express as px
import pandas as pd

# Load data
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/MTA_Ridership_by_DATA_NY_GOV.csv")
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year  # Extract year for filtering

# Identify available services dynamically
services = [col for col in df.columns if col.endswith("Comparable Pre-Pandemic Day")]

# Assign distinct colors to services using Plotly's qualitative color palettes
service_colors = {service: px.colors.qualitative.Set3[i % len(px.colors.qualitative.Set3)] for i, service in enumerate(services)}

# Initialize the Dash app
app = Dash(__name__)

# App Layout
app.layout = html.Div([
    # Title and Subtitle
    html.Div([
        html.H1("MTA Ridership Dashboard", style={'textAlign': 'left', 'fontSize': '36px', 'color': '#FFFFFF'}),
        html.P("Explore ridership recovery trends for various transportation services during the pandemic.",
               style={'textAlign': 'left', 'fontSize': '20px', 'color': '#FFFFFF'}),
    ], style={'marginBottom': '20px'}),

    # KPI Section
    html.Div(
        id='kpi-div',
        style={
            'display': 'flex',
            'justifyContent': 'space-around',
            'marginBottom': '20px',
            'color': '#FFFFFF',
        }
    ),

    # Date Picker
    html.Div([
        html.Label("Select Date Range:", style={'color': '#FFFFFF', 'fontSize': '16px'}),
        dcc.DatePickerRange(
            id='date-picker-range',
            min_date_allowed=df['Date'].min(),
            max_date_allowed=df['Date'].max(),
            start_date=df['Date'].min(),
            end_date=df['Date'].max(),
            display_format='YYYY-MM-DD',
            style={'margin': '10px'}
        )
    ], style={'marginBottom': '20px'}),

    # Service Filter Buttons
    html.Div(
        id='service-buttons',
        children=[
            html.Button(service.split(':')[0], id={'type': 'service-button', 'index': service}, n_clicks=0,
                        style={
                            'margin': '10px', 'padding': '12px 20px', 'border': f'2px solid {service_colors[service]}',
                            'backgroundColor': '#1C1C1C', 'color': service_colors[service],
                            'borderRadius': '8px', 'fontSize': '16px'
                        })
            for service in services
        ],
        style={'textAlign': 'center', 'marginBottom': '20px', 'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'}
    ),

    # Graph
    dcc.Graph(id='area-chart', style={'marginTop': '20px', 'width': '100%', 'height': '75vh'}),

    # Dynamic Summary
    html.Div(id='summary-div', style={'textAlign': 'left', 'marginTop': '20px', 'color': '#FFFFFF', 'fontSize': '18px'}),
], style={
    'fontFamily': 'Arial, sans-serif',
    'backgroundColor': '#121212',
    'padding': '30px',
    'color': '#FFFFFF',
    'maxWidth': '100%',
    'minHeight': '1080px',
    'margin': '0 auto'
})


# Callback for updating graph, summary, and KPIs
@callback(
    [Output('area-chart', 'figure'),
     Output('summary-div', 'children'),
     Output('kpi-div', 'children'),
     Output({'type': 'service-button', 'index': ALL}, 'style')],
    [Input({'type': 'service-button', 'index': ALL}, 'n_clicks'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')],
    [State({'type': 'service-button', 'index': ALL}, 'id'),
     State({'type': 'service-button', 'index': ALL}, 'style')]
)
def update_chart(service_clicks, start_date, end_date, button_ids, button_styles):
    # Determine active services based on button clicks
    active_services = [
        button_id['index'] for clicks, button_id, style in zip(service_clicks, button_ids, button_styles)
        if clicks % 2 == 1  # Odd clicks indicate active
    ]

    # Default to all services if none are selected
    if not active_services:
        active_services = services

    # Filter data based on the selected date range
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()

    # **Correct scaling logic: Ensure the values are between 0 and 1**
    for service in active_services:
        if filtered_df[service].max() > 1.0:  # Assuming data is in percentage form (e.g., 100 = 100%)
            filtered_df[service] /= 100.0  # Normalize to decimal values (e.g., 100 → 1.0)

    # Create the area chart
    fig = px.area(
        filtered_df,
        x='Date',
        y=active_services,
        labels={'value': 'Percentage'},
        title="Ridership Recovery Trends",
        color_discrete_map=service_colors,
    )
    fig.update_layout(
        yaxis=dict(
            tickformat=".0%",  # Display as percentage
            showgrid=True,
            gridcolor="#333333"
        ),
        legend_title_text='',
        title_font=dict(size=24, color='#FFFFFF'),
        font_color="#FFFFFF",
        plot_bgcolor="#121212",
        paper_bgcolor="#121212",
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="center", x=0.5)
    )

    # Calculate KPIs for active services
    kpi_elements = []
    for service in active_services:
        latest_value = filtered_df[service].iloc[-1] * 100 if not filtered_df.empty else 0
        avg_value = filtered_df[service].mean() * 100 if not filtered_df.empty else 0
        peak_value = filtered_df[service].max() * 100 if not filtered_df.empty else 0

        kpi_elements.append(html.Div([
            html.P(f"{service.split(':')[0]}:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.P(f"Current: {latest_value:.2f}%", style={'margin': '0'}),
            html.P(f"Avg: {avg_value:.2f}%", style={'margin': '0'}),
            html.P(f"Peak: {peak_value:.2f}%", style={'margin': '0'}),
        ], style={
            'backgroundColor': service_colors[service],
            'color': '#121212',
            'borderRadius': '10px',
            'padding': '20px',
            'boxShadow': '0px 4px 8px rgba(0,0,0,0.2)',
            'textAlign': 'center',
            'width': '200px',
            'margin': '10px',
            'border': f'2px solid {service_colors[service]}'
        }))

    # Dynamic summary text
    summary_texts = [f"Selected Date Range: {start_date} to {end_date}."]
    for service in active_services:
        summary_texts.append(
            f"{service.split(':')[0]} - Max: {filtered_df[service].max() * 100:.2f}% on "
            f"{filtered_df.loc[filtered_df[service].idxmax()]['Date'].strftime('%Y-%m-%d') if not filtered_df.empty else 'N/A'}, "
            f"Min: {filtered_df[service].min() * 100:.2f}% on "
            f"{filtered_df.loc[filtered_df[service].idxmin()]['Date'].strftime('%Y-%m-%d') if not filtered_df.empty else 'N/A'}."
        )

    summary_div = html.Div([html.P(text, style={'marginBottom': '5px'}) for text in summary_texts])

    # Update button styles dynamically to reflect active state
    updated_styles = [
        {
            **style,
            'backgroundColor': service_colors[button_id['index']] if button_id['index'] in active_services else '#1C1C1C',
            'color': '#1C1C1C' if button_id['index'] in active_services else service_colors[button_id['index']],
            'border': f"2px solid {service_colors[button_id['index']]}",
        }
        for button_id, style in zip(button_ids, button_styles)
    ]

    return fig, summary_div, kpi_elements, updated_styles


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
