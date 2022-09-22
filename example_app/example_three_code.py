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


def get_example_three_dataframe(session, airport_code):
    """Create dataframe for example three graph, based on the given airport."""
    dg = get_example_three_datagrid(session, airport_code)
    df = dg.to_df()
    return df


def get_example_three_datagrid(session, airport_code):
    """Create datagrid for example three data."""
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
    datagrid = one_per_dest.datagrid(columns, table=routes)

    return datagrid


def make_example_three_map(df):
    """Return HTML code for plotly map of unique flight routes from an airport."""
    fig = go.Figure()

    # Add each unique flight route as a line on a globe map, with co-ordinates set
    df = df.rename(columns={
        "Origin Airport Longitude": "orig_lon",
        "Origin Airport Latitude": "orig_lat",
        "Reporting Airport Longitude": "rep_lon",
        "Reporting Airport Latitude": "rep_lat",
        "Flight Route Name": "route_name",
    })
    for row in df.itertuples(index=False):
        fig.add_trace(
            go.Scattergeo(
                lon=[row.orig_lon, row.rep_lon],
                lat=[row.orig_lat, row.rep_lat],
                mode="lines+markers",
                line={"width": 3},
                text=row.route_name,
                name=row.route_name,
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
