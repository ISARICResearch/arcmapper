"""Dash frontend for the arcmapper library"""

import io

import pandas as pd
import dash
from dash import dcc, html, ctx, callback, dash_table, Input, Output, State
import dash_bootstrap_components as dbc

from .components import arc_form, upload_form
from .fhir import merge, FHIRMapping, FHIR_RESOURCES_ONE_TO_ONE
from .util import read_upload_data
from .dictionary import read_data_dictionary
from .strategies import use_map
from .arc import read_arc_schema
from .labels import (
    MAP_TO_ARC,
    DOWNLOAD_FHIRFLAT_MAPPING,
    SAVE_INTERMEDIATE_FILE,
    LOAD_INTERMEDIATE_FILE,
)

app = dash.Dash("arcmapper", external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "ARCMapper"

PAGE_SIZE = 25
OK = "✅"
HIGHLIGHT_COLOR = "bisque"

FHIR_MAPPING = FHIRMapping("arc-fhir/ARC_pre_1.0.0_preset_dengue.xlsx")

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

output_table = dbc.Container(
    html.Div(
        dbc.Row(
            dash_table.DataTable(
                id="mapping",
                data=[],
                columns=[
                    {"name": i, "id": i, "editable": i != "status"}
                    for i in [
                        "status",
                        "raw_variable",
                        "raw_description",
                        "raw_response",
                        "arc_variable",
                        "arc_description",
                        "arc_response",
                        "rank",
                    ]
                ],
                editable=True,
                style_data={
                    "whiteSpace": "normal",
                    "height": "auto",
                    "fontSize": "90%",
                },
                style_table={"overflowX": "auto"},
                page_size=PAGE_SIZE,
            ),
        ),
        style={"padding": "0.5em", "border": "1px solid silver", "borderRadius": "5px"},
    )
)

final_mapping_form = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Download(id="download-intermediate-mapping"),
                        dbc.Button(
                            SAVE_INTERMEDIATE_FILE,
                            id="save-intermediate",
                            style={"marginTop": "1em", "marginLeft": "0.6em"},
                        ),
                    ]
                ),
                dbc.Col(
                    dcc.Upload(
                        id="upload-intermediate-file",
                        children=html.Div(
                            LOAD_INTERMEDIATE_FILE,
                            style={
                                "background": "#316cf4",
                                "color": "white",
                                "padding": "0.45em",
                                "marginTop": "1em",
                                "marginLeft": "0.55em",
                                "borderRadius": "6px",
                                "cursor": "pointer",
                            },
                        ),
                    ),
                ),
                dbc.Col(
                    html.Div(
                        "After finalising the intermediate mapping, "
                        "download the mapping for FHIRflat conversion →",
                        style={"marginTop": "0.7em"},
                    ),
                    width=4,
                ),
                dbc.Col(
                    [
                        dcc.Download(id="download-fhirflat"),
                        dbc.Button(
                            DOWNLOAD_FHIRFLAT_MAPPING,
                            color="success",
                            id="save-fhirflat",
                            style={"marginTop": "1em"},
                        ),
                    ]
                ),
            ]
        ),
        dbc.Row(
            html.Div(
                [
                    dbc.Alert(
                        "Final mapping file may not be fully correct and should be manually reviewed",
                        color="info",
                    ),
                    html.Footer(
                        [
                            "ARCmapper can be run locally or hosted, source repository: ",
                            html.A(
                                "https://github.com/globaldothealth/arcmapper",
                                href="https://github.com/globaldothealth/arcmapper",
                            ),
                        ],
                        style={"fontSize": "90%", "textAlign": "center"},
                    ),
                ],
                style={
                    "marginLeft": "0.5em",
                    "marginBottom": "1em",
                    "marginTop": "1em",
                },
            )
        ),
    ]
)


@callback(
    Output("upload-data-dictionary", "data"),
    Output("upload-status", "children"),
    Input("upload-input-file", "contents"),
    State("upload-input-file", "filename"),
    State("upload-col-responses", "value"),
    State("upload-col-description", "value"),
    prevent_initial_call=True,
)
def upload_data_dictionary(
    upload_contents,
    filename,
    col_responses,
    col_description,
):
    ok = dbc.Alert("Upload successful", color="success", style={"marginTop": "1em"})

    def err(msg):
        return dbc.Alert(msg, color="danger", style={"marginTop": "1em"})

    if upload_contents is not None:
        try:
            df = read_upload_data(upload_contents, filename)
            # this is the unprocessed data dictionary, we will now convert
            # it into a standardised format
            assert df is not None
            if col_description not in df.columns:
                return {}, err("Description column not found")
            if col_responses not in df.columns:
                return {}, err("Responses column not found")
            data = read_data_dictionary(
                df,
                description_field=col_description,
                response_field=col_responses,
                response_func="redcap",
            )
            return data.to_json(), ok

        except Exception as e:
            print(e)
            return {}, err("Upload failed due to unknown reason")
    return {}, err("Upload failed due to unknown reason")


@callback(
    Output("map-btn", "children"),
    Input("map-btn", "n_clicks"),
    prevent_initial_call=True,
)
def set_loading_map(_):
    return [dbc.Spinner(size="sm"), MAP_TO_ARC[1:]]


@callback(
    Output("save-fhirflat", "children"),
    Input("save-fhirflat", "n_clicks"),
    prevent_initial_call=True,
)
def set_loading_save_fhirflat(_):
    return [dbc.Spinner(size="sm"), DOWNLOAD_FHIRFLAT_MAPPING[1:]]


def stringify_response_columns(df: pd.DataFrame):
    "Stringify response columns for output in mapping frame"

    def stringify(x):
        if isinstance(x, list):
            return str(x)
        else:
            return x

    df["raw_response"] = df["raw_response"].map(stringify)
    df["arc_response"] = df["arc_response"].map(stringify)


@callback(
    Output("mapping", "data"),
    Output("map-btn", "children", allow_duplicate=True),
    State("upload-data-dictionary", "data"),
    Input("map-btn", "n_clicks"),
    State("arc-version", "value"),
    State("arc-mapping-method", "value"),
    State("arc-num-matches", "value"),
    prevent_initial_call=True,
)
def invoke_map_arc(data, _, version, method, num_matches):
    if ctx.triggered_id == "map-btn":
        arc = read_arc_schema(version)
        dictionary = pd.read_json(data)

        mapped_data = use_map(method, dictionary, arc, num_matches)
        stringify_response_columns(mapped_data)
        data = mapped_data.to_dict("records")
        for i, row in enumerate(data):
            row["id"] = i
        return data, MAP_TO_ARC

    else:
        return html.Span("No data to see here"), "↪ Map to ARC"


@callback(
    Output("mapping", "data", allow_duplicate=True),
    Output("mapping", "style_data_conditional"),
    Output("mapping", "active_cell"),
    Input("mapping", "data"),
    Input("mapping", "active_cell"),
    prevent_initial_call=True,
)
def handle_status(data, active_cell):
    if active_cell and active_cell.get("column_id") == "status":
        i = active_cell.get("row_id")
        row = data[i]
        row["status"] = OK if row["status"] == "-" else "-"
    else:
        raise dash.exceptions.PreventUpdate
    highlighted_rows = [i for i in range(len(data)) if data[i]["status"] == OK]
    return (
        data,  # mapping data
        [
            {
                "if": {
                    "filter_query": " || ".join(
                        f"{{id}} = {k}" for k in highlighted_rows
                    )
                },
                "backgroundColor": HIGHLIGHT_COLOR,
            }
        ],  # style_data_conditional
        False,  # unsets active cell, allowing the cell to be clicked immediately again
    )


@callback(
    Output("mapping", "data", allow_duplicate=True),
    Output("mapping", "style_data_conditional", allow_duplicate=True),
    Input("upload-intermediate-file", "contents"),
    State("upload-intermediate-file", "filename"),
    prevent_initial_call=True,
)
def upload_intermediate_file(contents, filename):
    df = read_upload_data(contents, filename)
    assert df is not None
    data = df.to_dict("records")
    highlighted_rows = [i for i in range(len(data)) if data[i]["status"] == OK]
    return (
        data,  # mapping data
        [
            {
                "if": {
                    "filter_query": " || ".join(
                        f"{{id}} = {k}" for k in highlighted_rows
                    )
                },
                "backgroundColor": HIGHLIGHT_COLOR,
            }
        ],
    )


@callback(
    Output("download-intermediate-mapping", "data"),
    Input("save-intermediate", "n_clicks"),
    State("mapping", "data"),
    prevent_initial_call=True,
)
def handle_download(_, data):
    if ctx.triggered_id == "save-intermediate":
        df = pd.DataFrame(data)
        return dcc.send_data_frame(df.to_csv, "arcmapper-mapping-file.csv", index=False)
    else:
        raise dash.exceptions.PreventUpdate


@callback(
    Output("download-fhirflat", "data"),
    Output("save-fhirflat", "children", allow_duplicate=True),
    Input("save-fhirflat", "n_clicks"),
    State("mapping", "data"),
    prevent_initial_call=True,
)
def handle_download_fhir(_, data):
    if ctx.triggered_id == "save-fhirflat":
        df = pd.DataFrame(data)
        df = df[df.status == OK].drop(columns=["status", "rank"])
        dfs_by_resource = merge(df, FHIR_MAPPING)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            non_empty_resources = [
                res for res in dfs_by_resource if not dfs_by_resource[res].empty
            ]
            resource_type = [
                ("one-to-one" if res in FHIR_RESOURCES_ONE_TO_ONE else "one-to-many")
                for res in non_empty_resources
            ]
            index = pd.DataFrame(
                {"Resources": non_empty_resources, "Resource Type": resource_type}
            )
            index.to_excel(writer, sheet_name="Resources")
            for resource in dfs_by_resource:
                if dfs_by_resource[resource].empty:
                    continue
                dfs_by_resource[resource].to_excel(
                    writer, sheet_name=resource, index=False
                )
        data = output.getvalue()
        return dcc.send_bytes(data, "fhirflat-mapping.xlsx"), DOWNLOAD_FHIRFLAT_MAPPING
    else:
        raise dash.exceptions.PreventUpdate


app.layout = html.Div([navbar, upload_form, arc_form, output_table, final_mapping_form])
server = app.server
