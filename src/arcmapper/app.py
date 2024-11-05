"""Dash frontend for the arcmapper library"""

import pandas as pd
import dash
from dash import dcc, html, ctx, callback, dash_table, Input, Output, State
import dash_bootstrap_components as dbc

from .components import arc_form, upload_form
from .util import read_upload_data
from .dictionary import read_data_dictionary
from .strategies import map as map_data_dictionary_to_arc
from .arc import read_arc_schema

app = dash.Dash("arcmapper", external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "ARCMapper"

PAGE_SIZE = 25
OK = "✅"
HIGHLIGHT_COLOR = "bisque"

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
        dbc.Row(id="output"),
        style={"padding": "0.5em", "border": "1px solid silver", "borderRadius": "5px"},
    )
)

final_mapping_form = dbc.Container(
    dbc.Row(
        dbc.Col(
            [
                dcc.Download(id="download-mapping"),
                dbc.Button(
                    "Download mapping", id="download-btn", style={"marginTop": "1em"}
                ),
            ]
        )
    )
)


@callback(
    Output("upload-data-dictionary", "data"),
    Output("upload-status", "children"),
    Input("upload-btn", "n_clicks"),
    State("upload-input-file", "contents"),
    State("upload-input-file", "filename"),
    State("upload-col-responses", "value"),
    State("upload-col-description", "value"),
    prevent_initial_call=True,
)
def upload_data_dictionary(
    _,
    upload_contents,
    filename,
    col_responses,
    col_description,
):
    ok = dbc.Alert("Upload successful", color="success", style={"marginTop": "1em"})

    def err(msg):
        return dbc.Alert(msg, color="danger", style={"marginTop": "1em"})

    if ctx.triggered_id == "upload-btn" and upload_contents is not None:
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
    Output("output", "children"),
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

        mapped_data = map_data_dictionary_to_arc(method, dictionary, arc, num_matches)
        data = mapped_data.to_dict("records")
        for i, row in enumerate(data):
            row["id"] = i
        return (
            dash_table.DataTable(
                id="mapping",
                data=data,
                columns=[
                    {"name": i, "id": i, "editable": i != "status"}
                    for i in mapped_data.columns
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
        )
    else:
        return html.Span("No data to see here")


@callback(
    Output("mapping", "data"),
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
    Output("download-mapping", "data"),
    Input("download-btn", "n_clicks"),
    State("mapping", "data"),
    prevent_initial_call=True,
)
def handle_download(_, data):
    if ctx.triggered_id == "download-btn":
        df = pd.DataFrame(data)
        df = df[df.status == OK].drop(columns=["status", "rank"])
        return dcc.send_data_frame(df.to_csv, "arcmapper-mapping-file.csv", index=False)
    else:
        raise dash.exceptions.PreventUpdate


app.layout = html.Div([navbar, upload_form, arc_form, output_table, final_mapping_form])
server = app.server
