import dash
from dash import dcc, html
import dash_leaflet as dl
from dash.dependencies import Output, Input, State
from FlightRadar24 import FlightRadar24API
from utils import (
    update_rotation_angles,
    get_closest_round_angle,
    get_custom_icon,
    fetch_flight_data
)

# App initialization
app = dash.Dash(__name__)
# FlightRadar24API client
fr_api = FlightRadar24API()
airlines = fr_api.get_airlines()
liste_compagnie = [{'label': compagnie['Name'], 'value': compagnie['ICAO']} for compagnie in airlines if compagnie['ICAO']]

default_map_children = [
    dl.TileLayer(
        url="https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",  # URL pour les tuiles satellite de Google Maps
        subdomains=['mt0', 'mt1', 'mt2', 'mt3'],
        maxZoom=20
    )
]

app.layout = html.Div(style={'fontFamily': '"Courier New", Courier, monospace', 'backgroundColor': '#f8f9fa', 'overflow': 'hidden', 'height': '100vh'}, children=[
    dcc.Store(id="memory"),
    dcc.Store(id="local", storage_type="local"),
    dcc.Store(id="session", storage_type="session"),
    html.Div([
        html.H3('Choix de la compagnie aérienne', style={'marginBottom': '20px', 'color': '#1AA7E7'}),
        html.Hr(style={'borderColor': '#1AA7E7'}),
        dcc.Dropdown(
            id='dropdown',
            options=liste_compagnie,
            value='AFR',
            style={'width': '100%', 'marginBottom': '20px'}
        ),
        html.H4('Informations sur les vols', style={'color': '#1AA7E7'}),
        html.Hr(style={'borderColor': '#1AA7E7'}),
        html.P('Suivez en direct les vols des compagnies aériennes françaises et découvrez les aéroports de départ et de destination en France et en Europe.',
               style={'fontSize': '14px', 'lineHeight': '1.5', 'color': '#555'}),
        html.P('Les informations sur les vols incluent l’identifiant du vol, les aéroports d’origine et de destination, ainsi que la vitesse au sol.',
               style={'fontSize': '14px', 'lineHeight': '1.5', 'color': '#555'})
    ], style={
        'width': '250px',
        'background': '#f8f9fa',
        'padding': '10px',
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'height': '100vh'
    }),
    html.Div([
        dl.Map(
            id='map',
            center=[46.2276, 2.2137],  # Coordonnées approximatives du centre de la France
            zoom=6,  # Niveau de zoom initial (ajustez selon vos préférences)
            style={'width': '100%', 'height': '100vh'},
            children=default_map_children  # Ajout de la couche de tuiles satellite
        )
    ], style={'marginLeft': '270px', 'padding': '10px', 'height': '100vh'}),
    dcc.Interval(
        id="interval-component",
        interval=2*1000,  # in milliseconds
        n_intervals=0
    )
])

@app.callback(
    [Output('map', 'children'), Output('memory', 'data')],
    [Input('interval-component', 'n_intervals'), Input('dropdown', 'value')],
    [State('memory', 'data')]
)
def update_graph_live(n, airline_icao, previous_data):
    # Retrieve a list of flight dictionaries with 'latitude', 'longitude' and 'id' keys
    data = fetch_flight_data(client=fr_api, airline_icao=airline_icao, zone_str="europe")
    # Add a rotation_angle key to dictionaries
    if previous_data is None:
        for flight_data in data:
            flight_data.update(rotation_angle=0)
    else:
        update_rotation_angles(data, previous_data)

    # Update map children by adding markers to the default tiles layer
    children = default_map_children + [
        dl.Marker(
            id=flight['id'],
            position=[flight['latitude'], flight['longitude']],
            # TO MODIFY
            children=[
                dl.Popup(html.Div([
                    dcc.Markdown(f'''
                        **Identifiant du vol**: {flight['id']}.

                        **Aéroport d'origine**: {flight['origin_airport_iata']}.

                        **Aéroport de destination**: {flight['destination_airport_iata']}.

                        **Vitesse au sol**: {flight['ground_speed']} noeuds.
                    ''')
                ]))
            ],
            icon=get_custom_icon(
                get_closest_round_angle(flight['rotation_angle'])
            ),
        ) for flight in data
    ]

    return [children, data]

if __name__ == '__main__':
    app.run_server(
        debug=True, port=5000, host='0.0.0.0'
    )
