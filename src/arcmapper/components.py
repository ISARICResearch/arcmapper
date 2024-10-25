import dash_bootstrap_components as dbc


def select(id: str, values: list[str], default: str | None = None) -> dbc.Select:
    return dbc.Select(
        id=id,
        value=default if default else values[0],
        options=[{"label": v, "value": v} for v in values],
    )
