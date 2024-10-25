"""Dash frontend for the arcmapper library"""

import dash
from dash import html
import dash_bootstrap_components as dbc


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
                            html.Img(src="assets/ISARIC_logo_wh.png", height="60px")
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

main_content = dbc.Container([dbc.Row([html.H1("Hello world")])])

app.layout = dbc.Container([navbar, main_content])
server = app.server
