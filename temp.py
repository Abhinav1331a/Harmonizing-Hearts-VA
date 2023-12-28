import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import plotly.graph_objs as go
import time
# import serial
# import Adafruit_DHT
import requests
import base64
import os
import dash_bootstrap_components as dbc

dht_sensor_pin = 17  # GPIO pin for DHT sensor
# sensor = Adafruit_DHT.DHT11
serial_port = "/dev/ttyUSB0"
weather_api_key = "D75AASYAZL85Y8AQUHZN8CPNG"
weather_city = "buffalo"

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_dht_sensor():
    # humidity, temperature = Adafruit_DHT.read_retry(sensor, dht_sensor_pin)
    return 0, 0

def read_soil_moisture_sensor(serial_port='/dev/ttyUSB0', baud_rate=250000):
    # ser = serial.Serial(serial_port, baud_rate, timeout=10)
    # print("here")
    # line = ser.readline().decode('utf-8').rstrip()
    # print(f"Received Moisture Percentage: {line}")
    # try:
    #     numeric_data = ''.join(str(ord(c)) for c in line)
    #     print("here2: ", numeric_data)
    #     if numeric_data:
    #         moisture_percentage = int(float(numeric_data))
    #         return moisture_percentage
    # except (ValueError, IndexError) as e:
    #     print(f"Error parsing moisture percentage: {e}")
    return 0

def get_weather_data():
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{weather_city}?unitGroup=us&key={weather_api_key}&contentType=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error getting weather data: {response.status_code}")
        return {}

def save_uploaded_file(upload_data):
    if upload_data is not None:
        content_type, content_string = upload_data.split(',')
        decoded_image = base64.b64decode(content_string)

        filepath = os.path.join(UPLOAD_FOLDER, 'uploaded_image.jpg')

        with open(filepath, 'wb') as f:
            f.write(decoded_image)

def card_content(title, id):
    return [
        dbc.CardHeader(title),
        dbc.CardBody(
            [
                html.H5("Loading...", className="card-title", id=id),
                html.P("Last update just now", className="card-text"),
            ]
        ),
    ]

app.layout = dbc.Container([
    html.H1("Agriculture Dashboard", className="mb-4"),
    dbc.Row([
        dbc.Col(dbc.Card(card_content("Temperature", "temperature-text"), color="warning", inverse=True), width=4),
        dbc.Col(dbc.Card(card_content("Humidity", "humidity-text"), color="info", inverse=True), width=4),
        dbc.Col(dbc.Card(card_content("Soil Moisture", "moisture-text"), color="success", inverse=True), width=4),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='temperature-graph'), width=4),
        dbc.Col(dcc.Graph(id='humidity-graph'), width=4),
        dbc.Col(dcc.Graph(id='soil-moisture-graph'), width=4),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(html.Div(id='weather-info'), width=12),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(html.Div([
            dcc.Upload(
                id='upload-image',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                multiple=False
            ),
            html.Div(id='output-image-upload')
        ]), width=12),
    ], className="mb-4"),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    )
], fluid=True)

time_history = []
temperature_history = []
humidity_history = []
soil_moisture_history = []

@app.callback(
    [Output('temperature-text', 'children'),
     Output('humidity-text', 'children'),
     Output('moisture-text', 'children'),
     Output('temperature-graph', 'figure'),
     Output('humidity-graph', 'figure'),
     Output('soil-moisture-graph', 'figure'),
     Output('weather-info', 'children'),
     Output('output-image-upload', 'children')],  # Added output for weather info and image upload
    [Input('interval-component', 'n_intervals')],
    [State('upload-image', 'contents')]
)
def update_metrics(n, upload_data):
    global temperature_history, humidity_history, soil_moisture_history, time_history
    humidity, temperature = read_dht_sensor()
    soil_moisture = read_soil_moisture_sensor()

    # Get weather data
    weather_data = get_weather_data()
    temperature_weather = weather_data["currentConditions"]["temp"]
    humidity_weather = weather_data["currentConditions"]["humidity"]
    weather_info = f"Weather: {temperature_weather}°F, Humidity: {humidity_weather}%"

    # Get the current time for the x-axis
    current_time = time.time()

    # Append the current time and sensor readings to the history
    time_history.append(current_time)
    temperature_history.append(temperature)
    humidity_history.append(humidity)
    soil_moisture_history.append(soil_moisture)

    # Create figures using the history
    temperature_figure = {
        'data': [{'x': list(time_history), 'y': list(temperature_history), 'type': 'line', 'name': 'Temperature'}],
        'layout': {'title': 'Temperature Over Time'}
    }

    humidity_figure = {
        'data': [{'x': list(time_history), 'y': list(humidity_history), 'type': 'line', 'name': 'Humidity'}],
        'layout': {'title': 'Humidity Over Time'}
    }

    soil_moisture_figure = {
        'data': [{'x': list(time_history), 'y': list(soil_moisture_history), 'type': 'line', 'name': 'Soil Moisture'}],
        'layout': {'title': 'Soil Moisture Over Time'}
    }

    # Save uploaded image
    save_uploaded_file(upload_data)

    # Display uploaded image
    image_output = html.Img(src=f'/uploads/uploaded_image.jpg', style={'width': '100%'})

    return (
        f"{temperature:.1f} °C",
        f"{humidity:.1f} %",
        f"{soil_moisture:.1f} %",
        temperature_figure,
        humidity_figure,
        soil_moisture_figure,
        weather_info,
        image_output
    )

if __name__ == '__main__':
    app.run_server(debug=True)
