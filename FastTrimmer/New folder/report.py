import dash
from dash import html, dcc, Dash, Input, Output
import plotly.graph_objs as go
import pandas as pd

# Sample data
segments = [
    {"lane":"L1","start":[26.36114,76.25048],"end":[26.36034,76.25034],"start_chainage":247310,"end_chainage":247400,"structure":"Normal Road","roughness":1727.0,"rutting":2.9,"cracking":0.048,"ravelling":0.0},
    {"lane":"L1","start":[26.36034,76.25034],"end":[26.35945,76.25018],"start_chainage":247400,"end_chainage":247500,"structure":"Normal Road","roughness":1316.0,"rutting":3.3,"cracking":0.008,"ravelling":0.0},
    {"lane":"L1","start":[26.35945,76.25018],"end":[26.35857,76.25001],"start_chainage":247500,"end_chainage":247600,"structure":"Normal Road","roughness":1074.0,"rutting":3.1,"cracking":0.007,"ravelling":0.0},
    {"lane":"L1","start":[26.35857,76.25001],"end":[26.35768,76.24985],"start_chainage":247600,"end_chainage":247700,"structure":"Normal Road","roughness":831.0,"rutting":2.8,"cracking":0.004,"ravelling":0.0},
    {"lane":"L1","start":[26.35768,76.24985],"end":[26.35679,76.24969],"start_chainage":247700,"end_chainage":247800,"structure":"Normal Road","roughness":1059.0,"rutting":2.8,"cracking":0.049,"ravelling":0.0},
    {"lane":"L1","start":[26.35679,76.24969],"end":[26.3559,76.24953],"start_chainage":247800,"end_chainage":247900,"structure":"Culvert","roughness":1096.0,"rutting":3.7,"cracking":0.029,"ravelling":0.005},
    {"lane":"L1","start":[26.3559,76.24953],"end":[26.35501,76.24937],"start_chainage":247900,"end_chainage":248000,"structure":"Normal Road","roughness":1081.0,"rutting":3.3,"cracking":0.01,"ravelling":0.0},
]

# Create DataFrame
df = pd.DataFrame(segments)
df['mid_chainage'] = (df['start_chainage'] + df['end_chainage']) / 2

# Initialize Dash app
app = Dash(__name__)
app.title = "Highway Condition Report"

# Layout
app.layout = html.Div([
    html.H1("Highway Pavement Condition Report", style={'textAlign': 'center'}),
    
    dcc.Graph(
        id='profile-distresses',
        figure={
            "data": [
                go.Scatter(x=df['mid_chainage'], y=df['roughness'], name="Roughness", mode='lines+markers'),
                go.Scatter(x=df['mid_chainage'], y=df['rutting'], name="Rutting", mode='lines+markers'),
                go.Scatter(x=df['mid_chainage'], y=df['cracking'] * 1000, name="Cracking (×1000)", mode='lines+markers'),
            ],
            "layout": go.Layout(
                title="Distress Profile along Chainage",
                xaxis_title="Chainage (m)",
                yaxis_title="Distress Value",
                hovermode='closest'
            )
        }
    ),

    dcc.Graph(
        id='structure-boxplot',
        figure=go.Figure(
            data=[
                go.Box(y=df[df['structure']==s]['roughness'], name=f'Roughness - {s}')
                for s in df['structure'].unique()
            ],
            layout=go.Layout(title="Roughness Distribution by Structure Type")
        )
    ),

    dcc.Graph(
        id='map-path',
        figure=go.Figure(
            data=[
                go.Scattermapbox(
                    mode="markers+lines",
                    lat=[p['start'][0] for p in segments] + [segments[-1]['end'][0]],
                    lon=[p['start'][1] for p in segments] + [segments[-1]['end'][1]],
                    marker={'size': 6},
                    name='Segment Path'
                )
            ],
            layout=go.Layout(
                mapbox_style="open-street-map",
                mapbox_zoom=15,
                mapbox_center={"lat":26.358, "lon":76.249},
                title="Geographical View of Segment Path"
            )
        )
    ),

    html.H3("Segment Data Table"),
    dcc.Graph(
        id='data-table',
        figure=go.Figure(
            data=[go.Table(
                header=dict(values=list(df.columns), fill_color='paleturquoise', align='left'),
                cells=dict(values=[df[col] for col in df.columns], fill_color='lavender', align='left')
            )]
        )
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
