"""Dash frontend for the arcmapper library"""

import dash
from dash import html, callback, Input, Output
import dash_bootstrap_components as dbc


from .components import select

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
                            dbc.Input(type="file", id="upload-input-file"),
                            className="me-3",
                        ),
                        dbc.Col(
                            dbc.Button("Upload", id="upload-btn", color="primary"),
                            width="auto",
                        ),
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


@callback(
    Output("upload-status", "children"),
    Input("upload-btn", "clicked"),
    Input("upload-input-file", "input_file"),
    Input("upload-is-sample-data", "is_sample_data"),
    Input("upload-col-responses", "col_responses"),
    Input("upload-col-description", "col_description"),
    prevent_initial_call=True,
)
def upload_data_dictionary(
    clicked: int | None,
    input_file: str,
    col_responses: str,
    col_description: str,
    is_sample_data: bool = False,
):
    if clicked:
        return dbc.Alert("Upload successful", color="success")


app.layout = html.Div([navbar, upload_form, arc_form])
server = app.server
