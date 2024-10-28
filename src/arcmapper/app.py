"""Dash frontend for the arcmapper library"""

import pandas as pd
import dash
from dash import dcc, html, ctx, callback, dash_table, Input, Output, State
import dash_bootstrap_components as dbc


from .components import select
from .util import read_upload_data

app = dash.Dash("arcmapper", external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "ARCMapper"

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src=dash.get_asset_url("ISARIC_logo_wh.png"),
                                height="60px",
                            )
                        ),
                        dbc.Col(dbc.NavbarBrand("ARCMapper", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="https://isaric.org/",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        ]
    ),
    color="#BA0225",
    dark=True,
)

upload_form = dbc.Container(
    html.Div(
        dbc.Form(
            [
                dbc.Row(
                    [
                        html.P(
                            [
                                html.Strong("SOURCE: "),
                                "ARCmapper supports data dictionaries in CSV, XLSX, JSON schema, or you can upload sample data.",
                            ]
                        )
                    ]
                ),
                dbc.Row(
                    dbc.Col(
                        dbc.Switch(
                            id="upload-is-sample-data",
                            label="Uploaded file is sample data, not a data dictionary. Data will be sent to server, only use on local deployments",
                        )
                    )
                ),
                dbc.Row(
                    [
                        dbc.Label("Responses column", width="auto"),
                        dbc.Col(
                            dbc.Input(
                                id="upload-col-responses",
                                type="text",
                                placeholder="Column that has form response choices",
                            ),
                            className="me-3",
                        ),
                        dbc.Label("Description column", width="auto"),
                        dbc.Col(
                            dbc.Input(
                                id="upload-col-description",
                                type="text",
                                placeholder="Defaults to longest column",
                            ),
                            className="me-3",
                        ),
                        dbc.Col(
                            dcc.Upload(
                                id="upload-input-file",
                                children=html.Div(
                                    "Drag and drop or select file",
                                    style={
                                        "border": "1px dashed silver",
                                        "padding": "0.3em",
                                    },
                                ),
                            ),
                            className="me-3"
                        ),
                        dbc.Col(dbc.Button("Upload", id="upload-btn", color="primary", n_clicks=0)),
                        dcc.Store(id="upload-data-dictionary")
                    ],
                    className="g-2",
                ),
                dbc.Row(id="upload-status"),
            ]
        ),
        style={
            "border": "1px solid silver",
            "border-radius": "0.4em",
            "padding": "1em",
        },
    ),
    style={"margin-top": "1em"},
)

arc_form = dbc.Container(
    html.Div(
        dbc.Form(
            [
                dbc.Row(
                    html.P(
                        [
                            html.Strong("TARGET: "),
                            "Choose the target ARC version and select method and method parameters",
                        ]
                    )
                ),
                dbc.Row(
                    [
                        dbc.Label("Target ARC version", width="auto"),
                        dbc.Col(
                            select("arc-version", ["1.0.0", "1.0.1"]),
                            className="me-3",
                        ),
                        dbc.Label("Mapping method", width="auto"),
                        dbc.Col(
                            dbc.Select(
                                id="mapping-method",
                                options=[
                                    {"label": "TF-IDF", "value": "tf-idf"},
                                    {
                                        "label": "Sentence Transformers",
                                        "value": "sbert",
                                    },
                                ],
                                value="sbert",
                            ),
                            className="me-3",
                        ),
                        dbc.Label("Number of matches", width="auto"),
                        dbc.Col(
                            dbc.Input(type="number", min=2, max=10, step=1, value=3),
                        ),
                        dbc.Label("Threshold", width="auto"),
                        dbc.Col(
                            dbc.Input(
                                type="number", min=0.1, max=1, step=0.1, value=0.3
                            ),
                        ),
                        dbc.Col(dbc.Button("Map to ARC"), width="auto"),
                    ],
                    className="g-2",
                ),
            ]
        ),
        style={
            "border": "1px solid silver",
            "border-radius": "0.4em",
            "padding": "1em",
        },
    ),
    style={"margin-top": "1em"},
)

output_table = dbc.Container(html.Div(dbc.Row(id="output"), style={"padding": "0.5em", "border": "1px solid silver", "borderRadius": "5px"}))

@callback(
    Output("upload-data-dictionary", "data"),
    Output("upload-status", "children"),
    Input("upload-btn", "n_clicks"),
    State("upload-input-file", "contents"),
    State("upload-input-file", "filename"),
    # State("upload-is-sample-data", "value"),
    # State("upload-col-responses", "value"),
    # State("upload-col-description", "value"),
    prevent_initial_call=True,
)
def upload_data_dictionary(
    _,
    upload_contents,
    filename,
    # is_sample_data,
    # col_responses,
    # col_description,
):
    success = dbc.Alert("Upload successful", color="success")
    error = dbc.Alert("Upload failed", color="danger")
    if ctx.triggered_id == "upload-btn" and upload_contents is not None:
        try:
            data = read_upload_data(upload_contents, filename)
            print(data)
        except Exception as e:
            print(e)
            return {}, error
        return data, success
    return {}, error


@callback(
        Output("output", "children"),
        State("upload-data-dictionary", "data")
        Input("map-btn", "n_clicks"),
)
def invoke_map_arc(data, _):
    if ctx.triggered_id == "map-btn":
        df = pd.read_json(data)
        return dash_table.DataTable(df.to_dict('records'))
    return html.Span("No data to see here")
app.layout = html.Div([navbar, upload_form, arc_form, output_table])
server = app.server
