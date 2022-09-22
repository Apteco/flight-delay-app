from plotly import graph_objects as go

from .api_shared_methods import get_html
from .fs_var_names import (
    ORIGIN_AIRPORT_LATITUDE,
    ORIGIN_AIRPORT_LONGITUDE,
    ROUTE_NAME_CODE,
    REPORTING_AIRPORT_CODE,
    REPORTING_AIRPORT_LATITUDE,
    REPORTING_AIRPORT_LONGITUDE,
)


def get_datagrid_as_dataframe(session, airport_code):
    """Create datagrid for example three data, return dataframe from the data."""
    airports = session.tables["Reporting Airport"]
    routes = session.tables["Flight Route"]

    columns = [
        routes[ORIGIN_AIRPORT_LONGITUDE],
        routes[ORIGIN_AIRPORT_LATITUDE],
        airports[REPORTING_AIRPORT_LONGITUDE],
        airports[REPORTING_AIRPORT_LATITUDE],
        routes[ROUTE_NAME_CODE],
    ]

    airport_clause = airports[REPORTING_AIRPORT_CODE] == airport_code
    one_per_dest = (routes * airport_clause).limit(1, per=routes[ROUTE_NAME_CODE])
    dg = one_per_dest.datagrid(columns, table=routes)
    df = dg.to_df()

    return df


def make_example_three_map(df):
    """Return HTML code for plotly map of unique flight routes from an airport."""
    fig = go.Figure()

    # Add each unique flight route as a line on a globe map, with co-ordinates set
    for i in range(len(df)):
        fig.add_trace(
            go.Scattergeo(
                lon=[df["Origin Airport Longitude"][i], df["Reporting Airport Longitude"][i]],
                lat=[df["Origin Airport Latitude"][i], df["Reporting Airport Latitude"][i]],
                mode="lines+markers",
                line={"width": 3},
                text=df["Flight Route Name"][i],
                name=df["Flight Route Name"][i],
            )
        )
    fig.update_layout(
        geo={
            "showcountries": True,
            "projection": {"type": "orthographic"},  # try natural earth too
        },
        width=1500,
        height=700,  # Change figure size
    )
    return get_html(fig)
