import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load CSV data
def load_data():
    try:
        return pd.read_csv("detection_data.csv")
    except FileNotFoundError:
        # Return an empty dataframe if file doesn't exist
        return pd.DataFrame(columns=["Timestamp", "Object", "Count"])

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Object Detection Dashboard"

# Expose the Flask server for Gunicorn
server = app.server

# Define layout
app.layout = html.Div([
    html.H1("Object Detection Dashboard", style={"textAlign": "center"}),
    html.Div([
        html.Label("Select Object Type:"),
        dcc.Dropdown(
            id="object-filter",
            options=[{"label": "All", "value": "All"}],  # Dynamically populated
            value="All",
            clearable=False
        )
    ], style={"width": "50%", "margin": "auto"}),
    dcc.Graph(id="object-graph"),
    dcc.Interval(id="interval", interval=2000, n_intervals=0),  # Auto-refresh every 2s
])

# Callback to update dropdown options dynamically
@app.callback(
    Output("object-filter", "options"),
    Input("interval", "n_intervals")
)
def update_dropdown(n):
    data = load_data()
    object_types = data["Object"].unique() if not data.empty else []
    options = [{"label": "All", "value": "All"}] + [{"label": obj, "value": obj} for obj in object_types]
    return options

# Callback to update graph based on selected object type
@app.callback(
    Output("object-graph", "figure"),
    [Input("interval", "n_intervals"),
     Input("object-filter", "value")]
)
def update_graph(n, selected_object):
    data = load_data()
    if data.empty:
        return px.bar(title="No Data Available")

    # Filter data based on dropdown selection
    if selected_object != "All":
        data = data[data["Object"] == selected_object]

    # Create bar chart
    fig = px.bar(
        data,
        x="Timestamp",
        y="Count",
        color="Object",
        title="Object Detection Counts",
        labels={"Count": "Detection Count", "Timestamp": "Time"},
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

# Run the app locally for debugging
if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050)
