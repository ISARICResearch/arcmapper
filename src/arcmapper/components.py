from dash import html, dcc
import dash_bootstrap_components as dbc


def select(id: str, values: list[str], default: str | None = None) -> dbc.Select:
    return dbc.Select(
        id=id,
        value=default if default else values[0],
        options=[{"label": v, "value": v} for v in values],
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
                    [
                        dbc.Label("Responses column", width="auto"),
                        dbc.Col(
                            dbc.Input(
                                id="upload-col-responses",
                                type="text",
                                value="Choices, Calculations, OR Slider Labels",
                            ),
                            className="me-3",
                        ),
                        dbc.Label("Description column", width="auto"),
                        dbc.Col(
                            dbc.Input(
                                id="upload-col-description",
                                type="text",
                                placeholder="Defaults to longest column",
                                value="Field Label",
                            ),
                            className="me-3",
                        ),
                        dbc.Col(
                            dcc.Upload(
                                id="upload-input-file",
                                children=html.Div(
                                    "Upload data dictionary",
                                    style={
                                        "background": "#316cf4",
                                        "color": "white",
                                        "padding": "0.4em",
                                        "borderRadius": "5px",
                                        "cursor": "pointer",
                                    },
                                ),
                            ),
                            className="me-3",
                        ),
                        dcc.Store(id="upload-data-dictionary"),
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
                                id="arc-mapping-method",
                                options=[
                                    {"label": "TF-IDF", "value": "tf-idf"},
                                    {
                                        "label": "Sentence Transformers",
                                        "value": "sbert",
                                    },
                                ],
                                value="tf-idf",
                            ),
                            className="me-3",
                        ),
                        dbc.Label("Number of matches", width="auto"),
                        dbc.Col(
                            dbc.Input(
                                id="arc-num-matches",
                                type="number",
                                min=2,
                                max=10,
                                step=1,
                                value=3,
                            ),
                        ),
                        dbc.Label("Threshold", width="auto"),
                        dbc.Col(
                            dbc.Input(
                                id="arc-threshold",
                                type="number",
                                min=0.1,
                                max=1,
                                step=0.1,
                                value=0.3,
                            ),
                        ),
                        dbc.Col(dbc.Button("Map to ARC", id="map-btn"), width="auto"),
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
