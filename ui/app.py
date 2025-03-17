import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import requests

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Simulated API endpoint (replace with real API URL)
API_URL = "http://localhost:8000/outlets"  # Replace with real API

# Fetch branch data from API
def fetch_branch_data():
    try:
        response = requests.get(API_URL)
        #print(f"API Response: {response.status_code}, Data: {response.text}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
    return {"data": []} 


# Map component with dynamic markers
def create_map(data):
    markers = [
        dl.Marker(
            position=[branch["latitude"], branch["longitude"]],
            children=dl.Tooltip(branch["outlet_name"]),
            id={"type": "map-marker", "index": i},
            n_clicks=0  # Add click detection to marker
        )
        for i, branch in enumerate(data['data'])
    ]

    return dl.Map(
        [dl.TileLayer(), *markers],
        center=[3.1390, 101.6869],  # Default center (Kuala Lumpur)
        zoom=12,
        style={"height": "80vh", "width": "100%"},
        id="map"
    )

# Card layout with scrollable div
def create_cards(data):
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody([
                    html.H5(branch["outlet_name"], className="card-title"),
                    html.P(f"Address: {branch['address']}"),
                    html.P(f"Opening Hours: {branch['opening_hours']}"),
                    
                    html.Div([
                        html.A('Waze', href =branch['waze_link'], target='_blank'),
                        html.Br(),
                        html.A('Google Maps', href =branch['gmaps_link'], target='_blank'),
                    ]),
                    html.Br(),
                    dbc.Button("View on Map", id={"type": "card-button", "index": i}, color="primary"),
                ]),
                className="mb-3"
            )
            for i, branch in enumerate(data['data'])
        ],
        style={"height": "70vh", "overflowY": "auto"}  #Enable scrolling
    )


# Simple Chat UI
chat_ui = html.Div([
    html.Div("Chat Mode - Type your messages below:", className="p-2"),
    html.Div(id="chat-history", style={"height": "60vh", "overflowY": "auto", "border": "1px solid #ccc", "padding": "10px"}),  # Chat history
    dbc.Input(id="chat-input", placeholder="Type a message...", type="text", className="mt-2"),
    html.Button("Send", id="chat-send", className="btn btn-primary mt-2")
], className="p-3 border rounded", style={"height": "70vh", "display": "flex", "flexDirection": "column"})

@app.callback(
    Output("chat-history", "children"),
    Input("chat-store", "data")
)
def display_chat(chat_data):
    return html.Div([
        html.Div(
            f"{msg['role']}: {msg['message']}",
            className="p-2 my-1 border rounded bg-light" if msg["role"] == "User" else "p-2 my-1 border rounded bg-primary text-white"
        ) for msg in chat_data
    ])

@app.callback(
    Output("chat-store", "data"),
    Output("chat-input", "value"),
    Input("chat-send", "n_clicks"),
    State("chat-input", "value"),
    State("chat-store", "data"),
    prevent_initial_call=True
)
def update_chat(n_clicks, user_message, chat_data):
    if not user_message:
        return dash.no_update, ""

    # Append user's message
    chat_data.append({"role": "User", "message": user_message})

    # Call the chat API
    try:
        response = requests.post("http://localhost:8000/chat", json={"text": user_message})
        if response.status_code == 200:
            bot_response = response.json().get("response", "I'm not sure how to respond.")
        else:
            bot_response = "Error: Unable to fetch response from the chatbot API."
    except Exception as e:
        bot_response = f"Error: {e}"

    # Append bot's response
    chat_data.append({"role": "Subway Tracko", "message": bot_response[0] if len(bot_response)==1 else bot_response})

    return chat_data, ""  # Clear input box after sending



# Layout structure
app.layout = html.Div([
    dcc.Store(id="chat-store", data=[]),  # Store chat messages
    dcc.Store(id="map-reset-trigger", data={"reset": True}),
    # Navigation Bar with Logo
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand(
                html.Div([
                    html.Img(src="/assets/logo.png", height="40px", style={"margin-right": "10px"}),  # Logo
                    html.Span("Locator", style={"font-size": "20px", "font-weight": "bold"})  # App Title
                ], style={"display": "flex", "align-items": "center"}),  
                className="ms-0",
            ),

            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Home", href="/")),
                    dbc.NavItem(dbc.NavLink("About", href="/about")),
                ], className="ms-auto"), 
                id="navbar-collapse",
                navbar=True,
            ),
        ], fluid=True),
        color="dark",
        dark=True,
    ),
    
    # Page Content
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])

# Home Page Layout
def home_layout():
    branch_data = fetch_branch_data() or {"data": []}

    return dbc.Container([
        dbc.Row([
            # Left: Map Section
            dbc.Col([
                html.H4("Subway KL Outlet Map"),
                create_map(branch_data),
                html.Button("Reset Map", id="reset-map", className="btn btn-danger mt-3"),  # Reset button
            ], width=8),

            # Right: Card/Chat Toggle Section
            dbc.Col([
                html.H4("Details"),
                dbc.Switch(id="view-toggle", label="Toggle Chat Mode", value=False),
                html.Div(id="right-column-content")
            ], width=4)
        ])
    ], fluid=True)


# About Page Layout
about_layout = dbc.Container([
    html.H2("About This App"),
    html.P("This is a Subaway outlets locator app that helps users Subway branches on a map."),
    html.P([
        "The data is scrape from a ",
        html.A("Subway website.", href="https://www.subway.com.my/find-a-subway", target="_blank")
    ]),
    html.H1("What can be used for:"),
    html.H4("1. Get the coverage of a Subway outlets in 5 km radius"),
    html.Img(src='/assets/image1.png', height="500px"),
    html.P('This can be useful:'),
    html.Li('a. To understand the market coverage and reach'),
    html.Li('b. Detect overlapping area'),
    html.Li('c. Optimize for new outlet placement'),
    html.H4('2. Get the details of the Subway outlet'),
    html.Img(src='/assets/image2.png', height="500px"),
    html.P('Browse all the details and get the useful information such as address and Waze link.'),
    html.H4('3. Chat with our LLM model'),
    html.Img(src='/assets/image3.png', height="500px"),
    html.P('You can just ask our LLM if you are tired of scrolling..'),
], className="mt-4")

# Callback to update content based on URL
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/about":
        return about_layout
    return home_layout()

@app.callback(
    Output("right-column-content", "children"),
    Input("view-toggle", "value")
)
def toggle_view(view_mode):
    branch_data = fetch_branch_data()
    if view_mode:
        return chat_ui  # Show chat UI when toggled
    return create_cards(branch_data)  # Show branch cards when in normal mode



import math
# Callback to highlight location on map when clicking a card
def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance (in km) between two coordinates."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@app.callback(
    Output("map", "children"),
    [
        Input("map-reset-trigger", "data"),  #trigger for resetting on page load
        Input({"type": "map-marker", "index": dash.ALL}, "n_clicks"),
        Input({"type": "card-button", "index": dash.ALL}, "n_clicks"),
        Input("reset-map", "n_clicks"),
    ],
    prevent_initial_call=False
)
def update_map(reset_trigger, marker_clicks, button_clicks, reset_click):
    branch_data = fetch_branch_data() or {"data": []}

    ctx = dash.callback_context
    if not ctx.triggered:
        return create_map(branch_data)

    triggered_id = ctx.triggered[0]["prop_id"]

    #Reset button clicked page load
    if "reset-map" in triggered_id or "map-reset-trigger" in triggered_id:
        return create_map(branch_data)

    # Find the last clicked item (either a marker or a button)
    clicked_index = None
    if "map-marker" in triggered_id:
        clicked_index = eval(triggered_id.split(".")[0])["index"]
    elif "card-button" in triggered_id:
        clicked_index = eval(triggered_id.split(".")[0])["index"]

    if clicked_index is None or clicked_index >= len(branch_data["data"]):
        return dash.no_update

    selected_branch = branch_data["data"][clicked_index]
    selected_lat, selected_lon = selected_branch["latitude"], selected_branch["longitude"]

    icon_paths = {
        "red": "/assets/icons/marker-icon-red.png",
        "green": "/assets/icons/marker-icon-green.png",
        "yellow": "/assets/icons/marker-icon-yellow.png",
    }
    shadow_path = "/assets/icons/marker-shadow.png"

    markers = []
    for i, branch in enumerate(branch_data["data"]):
        branch_lat, branch_lon = branch["latitude"], branch["longitude"]
        distance = haversine(selected_lat, selected_lon, branch_lat, branch_lon)

        if i == clicked_index:
            color = "green"
        elif distance <= 5:
            color = "yellow"
        else:
            color = "red"

        markers.append(
            dl.Marker(
                position=[branch_lat, branch_lon],
                children=dl.Tooltip(branch["outlet_name"]),
                id={"type": "map-marker", "index": i},
                icon={
                    "iconUrl": icon_paths[color],
                    "shadowUrl": shadow_path,
                    "iconSize": [25, 41],
                    "iconAnchor": [12, 41]
                }
            )
        )

    highlight_circle = dl.Circle(
        center=[selected_lat, selected_lon],
        radius=5000, #5 km radius
        color="blue",
        fill=True,
        fillOpacity=0.3
    )

    return [dl.TileLayer(), *markers, highlight_circle]

# Run App
if __name__ == "__main__":
    app.run_server(debug=True)