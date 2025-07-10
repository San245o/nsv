import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash.dash_table import DataTable
import plotly.express as px

# Sample data
segments = [
    {"lane": "L1", "start_lat": 26.36114, "start_lon": 76.25048, "end_lat": 26.36034, "end_lon": 76.25034, 
     "start_chainage": 247310, "end_chainage": 247400, "structure": "Normal Road", 
     "roughness": 1727.0, "rutting": 2.9, "cracking": 0.048, "ravelling": 0.0},
    {"lane": "L1", "start_lat": 26.36034, "start_lon": 76.25034, "end_lat": 26.35945, "end_lon": 76.25018, 
     "start_chainage": 247400, "end_chainage": 247500, "structure": "Normal Road", 
     "roughness": 1316.0, "rutting": 3.3, "cracking": 0.008, "ravelling": 0.0},
    {"lane": "L1", "start_lat": 26.35945, "start_lon": 76.25018, "end_lat": 26.35857, "end_lon": 76.25001, 
     "start_chainage": 247500, "end_chainage": 247600, "structure": "Normal Road", 
     "roughness": 1074.0, "rutting": 3.1, "cracking": 0.007, "ravelling": 0.0},
    {"lane": "L1", "start_lat": 26.35857, "start_lon": 76.25001, "end_lat": 26.35768, "end_lon": 76.24985, 
     "start_chainage": 247600, "end_chainage": 247700, "structure": "Normal Road", 
     "roughness": 831.0, "rutting": 2.8, "cracking": 0.004, "ravelling": 0.0},
    {"lane": "L1", "start_lat": 26.35768, "start_lon": 76.24985, "end_lat": 26.35679, "end_lon": 76.24969, 
     "start_chainage": 247700, "end_chainage": 247800, "structure": "Normal Road", 
     "roughness": 1059.0, "rutting": 2.8, "cracking": 0.049, "ravelling": 0.0},
    {"lane": "L1", "start_lat": 26.35679, "start_lon": 76.24969, "end_lat": 26.3559, "end_lon": 76.24953, 
     "start_chainage": 247800, "end_chainage": 247900, "structure": "Culvert", 
     "roughness": 1096.0, "rutting": 3.7, "cracking": 0.029, "ravelling": 0.005},
    {"lane": "L1", "start_lat": 26.3559, "start_lon": 76.24953, "end_lat": 26.35501, "end_lon": 76.24937, 
     "start_chainage": 247900, "end_chainage": 248000, "structure": "Normal Road", 
     "roughness": 1081.0, "rutting": 3.3, "cracking": 0.01, "ravelling": 0.0}
]

# DataFrame
df = pd.DataFrame(segments)
df['mid_chainage'] = (df['start_chainage'] + df['end_chainage']) / 2
df['length'] = df['end_chainage'] - df['start_chainage']
df['coordinates'] = df.apply(lambda x: f"{x['start_lat']:.5f}, {x['start_lon']:.5f} to {x['end_lat']:.5f}, {x['end_lon']:.5f}", axis=1)

# Calculate center point for map zoom
center_lat = np.mean([p['start_lat'] for p in segments] + [segments[-1]['end_lat']])
center_lon = np.mean([p['start_lon'] for p in segments] + [segments[-1]['end_lon']])

# Condition categories
def categorize_condition(value, thresholds, labels):
    for i, threshold in enumerate(thresholds):
        if value <= threshold:
            return labels[i]
    return labels[-1]

# Add condition categories
df['roughness_condition'] = df['roughness'].apply(lambda x: categorize_condition(x, [1000, 1500, 2000], ['Good', 'Fair', 'Poor', 'Very Poor']))
df['rutting_condition'] = df['rutting'].apply(lambda x: categorize_condition(x, [2, 4, 6], ['Good', 'Fair', 'Poor', 'Very Poor']))
df['cracking_condition'] = df['cracking'].apply(lambda x: categorize_condition(x*100, [1, 5, 10], ['Good', 'Fair', 'Poor', 'Very Poor']))

# App setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Highway Condition Intelligence Dashboard"
server = app.server

# Color scales
condition_colors = {
    'Good': '#2ecc71',
    'Fair': '#f39c12',
    'Poor': '#e74c3c',
    'Very Poor': '#8e44ad'
}

# Prepare table data (removing complex objects)
table_df = df.drop(columns=['coordinates']).copy()
table_columns = [{"name": col.replace("_", " ").title(), "id": col} for col in table_df.columns if col not in ['start_lat', 'start_lon', 'end_lat', 'end_lon']]

# Create map figure
def create_map_figure():
    # Create line segments for the map
    lats = []
    lons = []
    hover_texts = []
    for _, row in df.iterrows():
        lats.extend([row['start_lat'], row['end_lat'], None])  # Add None to create separate lines
        lons.extend([row['start_lon'], row['end_lon'], None])
        hover_texts.extend([
            f"Segment: {row['start_chainage']}-{row['end_chainage']}m<br>"
            f"Lane: {row['lane']}<br>"
            f"Roughness: {row['roughness']} IRI<br>"
            f"Rutting: {row['rutting']} mm<br>"
            f"Cracking: {row['cracking']*100:.1f}%",
            "",
            ""
        ])
    
    fig = go.Figure(go.Scattermapbox(
        mode="lines",
        lat=lats,
        lon=lons,
        line=dict(width=4, color='#3498db'),
        hoverinfo='text',
        hovertext=hover_texts,
        name="Road Segments"
    ))
    
    # Add markers for start points
    fig.add_trace(go.Scattermapbox(
        mode="markers",
        lat=df['start_lat'],
        lon=df['start_lon'],
        marker=dict(size=8, color='#e74c3c'),
        hoverinfo='text',
        hovertext=[f"Start: {row['start_chainage']}m" for _, row in df.iterrows()],
        name="Start Points"
    ))
    
    # Add markers for end points
    fig.add_trace(go.Scattermapbox(
        mode="markers",
        lat=df['end_lat'],
        lon=df['end_lon'],
        marker=dict(size=8, color='#2ecc71'),
        hoverinfo='text',
        hovertext=[f"End: {row['end_chainage']}m" for _, row in df.iterrows()],
        name="End Points"
    ))
    
    fig.update_layout(
        mapbox_style="streets",
        mapbox_zoom=15,
        mapbox_center={"lat": center_lat, "lon": center_lon},
        height=500,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        hovermode='closest',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        showlegend=True
    )
    
    return fig

# Layout
app.layout = dbc.Container([
    # Header with logo and title
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Img(src="https://cdn-icons-png.flaticon.com/512/2777/2777154.png", 
                        style={'height':'60px', 'margin-right':'15px'}),
                html.H1("Highway Pavement Condition Intelligence", 
                       style={'display':'inline', 'vertical-align':'middle', 'color': 'white'})
            ], style={'text-align':'center', 'margin':'20px 0'})
        ])
    ], className="mb-4"),
    
    # Summary KPI Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Total Length", className="text-center text-white bg-primary"),
                dbc.CardBody([
                    html.H4(f"{df['length'].sum()} m", className="card-title text-center text-white"),
                    html.P("Surveyed Road Length", className="card-text text-center text-muted")
                ])
            ], className="h-100")
        ], md=3, className="mb-3"),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Average Roughness", className="text-center text-white", style={'background-color': '#3498db'}),
                dbc.CardBody([
                    html.H4(f"{df['roughness'].mean():.0f} IRI", className="card-title text-center text-white"),
                    html.P(f"Condition: {categorize_condition(df['roughness'].mean(), [1000, 1500, 2000], ['Good', 'Fair', 'Poor', 'Very Poor'])}", 
                          className="card-text text-center text-muted")
                ])
            ], className="h-100")
        ], md=3, className="mb-3"),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Average Rutting", className="text-center text-white", style={'background-color': '#f39c12'}),
                dbc.CardBody([
                    html.H4(f"{df['rutting'].mean():.1f} mm", className="card-title text-center text-white"),
                    html.P(f"Condition: {categorize_condition(df['rutting'].mean(), [2, 4, 6], ['Good', 'Fair', 'Poor', 'Very Poor'])}", 
                          className="card-text text-center text-muted")
                ])
            ], className="h-100")
        ], md=3, className="mb-3"),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Average Cracking", className="text-center text-white", style={'background-color': '#e74c3c'}),
                dbc.CardBody([
                    html.H4(f"{df['cracking'].mean()*100:.2f}%", className="card-title text-center text-white"),
                    html.P(f"Condition: {categorize_condition(df['cracking'].mean()*100, [1, 5, 10], ['Good', 'Fair', 'Poor', 'Very Poor'])}", 
                          className="card-text text-center text-muted")
                ])
            ], className="h-100")
        ], md=3, className="mb-3")
    ], className="mb-4"),
    
    # Filters and main content
    dbc.Row([
        # Filters sidebar
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filters", className="text-white", style={'background-color': '#2c3e50'}),
                dbc.CardBody([
                    html.Label("Select Distress Parameters:", className="mb-2 text-white"),
                    dcc.Dropdown(
                        id='parameter-selector',
                        options=[
                            {'label': 'Roughness (IRI)', 'value': 'roughness'},
                            {'label': 'Rutting (mm)', 'value': 'rutting'},
                            {'label': 'Cracking (%)', 'value': 'cracking'},
                            {'label': 'Ravelling (%)', 'value': 'ravelling'}
                        ],
                        value=['roughness', 'rutting'],
                        multi=True,
                        className="mb-3"
                    ),
                    html.Label("Select Lane:", className="mb-2 text-white"),
                    dcc.Dropdown(
                        id='lane-selector',
                        options=[{'label': lane, 'value': lane} for lane in df['lane'].unique()],
                        value='L1',
                        className="mb-3"
                    ),
                    html.Label("Chainage Range:", className="mb-2 text-white"),
                    dcc.RangeSlider(
                        id='chainage-slider',
                        min=df['start_chainage'].min(),
                        max=df['end_chainage'].max(),
                        step=100,
                        value=[df['start_chainage'].min(), df['end_chainage'].max()],
                        marks={i: str(i) for i in range(df['start_chainage'].min(), df['end_chainage'].max()+1, 200)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        className="mb-4"
                    ),
                    
                    # Condition distribution pie charts
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Roughness Condition", className="text-white", style={'background-color': '#2c3e50'}),
                                dbc.CardBody([
                                    dcc.Graph(
                                        id='roughness-pie',
                                        figure={
                                            'data': [go.Pie(
                                                labels=df['roughness_condition'].value_counts().index,
                                                values=df['roughness_condition'].value_counts().values,
                                                marker_colors=[condition_colors[x] for x in df['roughness_condition'].value_counts().index],
                                                hole=0.4,
                                                textinfo='label+percent'
                                            )],
                                            'layout': go.Layout(
                                                template="plotly_dark",
                                                margin=dict(t=10, b=10, l=10, r=10),
                                                showlegend=False
                                            )
                                        },
                                        config={'displayModeBar': False},
                                        style={'height': '200px'}
                                    )
                                ])
                            ])
                        ], md=6, className="mb-3"),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Rutting Condition", className="text-white", style={'background-color': '#2c3e50'}),
                                dbc.CardBody([
                                    dcc.Graph(
                                        id='rutting-pie',
                                        figure={
                                            'data': [go.Pie(
                                                labels=df['rutting_condition'].value_counts().index,
                                                values=df['rutting_condition'].value_counts().values,
                                                marker_colors=[condition_colors[x] for x in df['rutting_condition'].value_counts().index],
                                                hole=0.4,
                                                textinfo='label+percent'
                                            )],
                                            'layout': go.Layout(
                                                template="plotly_dark",
                                                margin=dict(t=10, b=10, l=10, r=10),
                                                showlegend=False
                                            )
                                        },
                                        config={'displayModeBar': False},
                                        style={'height': '200px'}
                                    )
                                ])
                            ])
                        ], md=6, className="mb-3")
                    ])
                ])
            ])
        ], md=3, className="mb-4"),
        
        # Main content area
        dbc.Col([
            # Distress profile graph
            dbc.Card([
                dbc.CardHeader("Distress Profile Along Chainage", className="text-white", style={'background-color': '#2c3e50'}),
                dbc.CardBody([
                    dcc.Graph(id='distress-profile',
                              config={'responsive': True},
                              style={'height': '400px'})
                ])
            ], className="mb-4"),
            
            # Map and data table in tabs
            dbc.Tabs([
                dbc.Tab(
                    label="Route Map",
                    tabClassName="text-white",
                    children=[
                        dbc.Card([
                            dbc.CardBody([
                                dcc.Graph(
                                    id='route-map',
                                    figure=create_map_figure(),
                                    config={'scrollZoom': True, 'responsive': True},
                                    style={'height': '500px'}
                                )
                            ])
                        ])
                    ]
                ),
                dbc.Tab(
                    label="Segment Data",
                    tabClassName="text-white",
                    children=[
                        dbc.Card([
                            dbc.CardBody([
                                DataTable(
                                    id='segment-table',
                                    columns=table_columns,
                                    data=table_df.to_dict('records'),
                                    style_table={
                                        'overflowX': 'auto',
                                        'width': '100%',
                                        'minWidth': '100%'
                                    },
                                    style_header={
                                        'backgroundColor': '#2c3e50',
                                        'color': 'white',
                                        'fontWeight': 'bold',
                                        'textAlign': 'center'
                                    },
                                    style_cell={
                                        'backgroundColor': 'rgb(50, 50, 50)',
                                        'color': 'white',
                                        'padding': '10px',
                                        'textAlign': 'left'
                                    },
                                    style_data_conditional=[
                                        {
                                            'if': {
                                                'filter_query': '{roughness_condition} = "Very Poor"',
                                                'column_id': 'roughness'
                                            },
                                            'backgroundColor': condition_colors['Very Poor'],
                                            'color': 'white'
                                        },
                                        {
                                            'if': {
                                                'filter_query': '{rutting_condition} = "Very Poor"',
                                                'column_id': 'rutting'
                                            },
                                            'backgroundColor': condition_colors['Very Poor'],
                                            'color': 'white'
                                        },
                                        {
                                            'if': {'column_id': 'lane'},
                                            'textAlign': 'center'
                                        }
                                    ],
                                    page_size=10,
                                    filter_action="native",
                                    sort_action="native",
                                    sort_mode="multi",
                                    page_action="native"
                                )
                            ])
                        ])
                    ]
                )
            ])
        ], md=9)
    ]),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Div([
                html.P("© 2023 Highway Condition Monitoring System | Dashboard v2.0", 
                      className="text-center text-muted mt-4")
            ])
        ])
    ])
], fluid=True, style={'padding': '20px', 'background-color': '#1a1a1a'})

# Callbacks for interactivity
@callback(
    Output('distress-profile', 'figure'),
    [Input('parameter-selector', 'value'),
     Input('lane-selector', 'value'),
     Input('chainage-slider', 'value')]
)
def update_distress_profile(selected_params, selected_lane, chainage_range):
    filtered_df = df[(df['lane'] == selected_lane) & 
                    (df['mid_chainage'] >= chainage_range[0]) & 
                    (df['mid_chainage'] <= chainage_range[1])]
    
    data = []
    for param in selected_params:
        scale = 1
        if param == 'cracking' or param == 'ravelling':
            scale = 100  # Convert to percentage
        
        data.append(go.Scatter(
            x=filtered_df['mid_chainage'],
            y=filtered_df[param] * scale,
            name=f"{param.capitalize()} {'(%)' if param in ['cracking', 'ravelling'] else ''}",
            mode='lines+markers',
            line=dict(width=2),
            marker=dict(size=8)
        ))
    
    layout = go.Layout(
        title="",
        xaxis_title="Chainage (m)",
        yaxis_title="Distress Value",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, b=50, t=30, pad=4),
        autosize=True
    )
    
    return {'data': data, 'layout': layout}

if __name__ == "__main__":
    app.run(debug=True)