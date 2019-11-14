import apteco_api as aa
import pandas as pd
from plotly import graph_objects as go

from .api_shared_methods import (
    create_clause,
    create_column,
    create_export,
    create_query,
    create_topn,
    get_html,
)
from .fs_var_names import (
    ORIGIN_AIRPORT_LATITUDE,
    ORIGIN_AIRPORT_LONGITUDE,
    ORIGINDEST_CODE,
    REPORTING_AIRPORT_CODE,
    REPORTING_AIRPORT_LATITUDE,
    REPORTING_AIRPORT_LONGITUDE,
)


def get_export_as_dataframe(session, airport_code):
    """ Create export for example three data, return dataframe from the data. """
    api_client = session.api_client
    exports_api = aa.ExportsApi(api_client)

    # Get origin and destination co-ordinates, and a name for the flight route
    column_details = [
        ("OriginLong", ORIGIN_AIRPORT_LONGITUDE),
        ("OriginLat", ORIGIN_AIRPORT_LATITUDE),
        ("DestLong", REPORTING_AIRPORT_LONGITUDE),
        ("DestLat", REPORTING_AIRPORT_LATITUDE),
        ("OriginDest", ORIGINDEST_CODE),
    ]
    columns = [create_column(*i) for i in column_details]

    # Filter to only the airport chosen
    airport_clause = create_clause(session, REPORTING_AIRPORT_CODE, [airport_code])
    airport_rule = aa.Rule(airport_clause)
    # Show one row per unique Origin - Dest flight path
    one_per_dest = create_topn(ORIGINDEST_CODE)
    query = create_query(rule=airport_rule, top_n=one_per_dest)
    export = create_export(query, columns)
    export_result = exports_api.exports_perform_export_synchronously(
        session.data_view, session.system, export=export
    )
    # Create dataframe from export_result
    rows = [i.descriptions.split("\t") for i in export_result.rows]
    df = pd.DataFrame(rows, columns=[i[0] for i in column_details])

    return df


def make_example_three_map(df):
    """ Return html code for plotly map of unique flight routes from an airport. """
    fig = go.Figure()

    # Add each unique flight route as a line on a globe map, with co-ordinates set
    for i in range(len(df)):
        fig.add_trace(
            go.Scattergeo(
                lon=[df["OriginLong"][i], df["DestLong"][i]],
                lat=[df["OriginLat"][i], df["DestLat"][i]],
                mode="lines+markers",
                line={"width": 3},
                text=df["OriginDest"][i],
                name=df["OriginDest"][i],
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
