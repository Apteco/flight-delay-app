import pandas as pd
from plotly import express as px

from .api_shared_methods import make_cube_dataframe, get_html
from .fs_var_names import (
    AIRLINE_NAME_CODE,
    ORIGIN_DESTINATION_CODE,
    REPORTING_AIRPORT_CODE,
    ORIGIN_AIRPORT_LATITUDE,
    ORIGIN_AIRPORT_LONGITUDE,
    REPORTING_PERIOD_MONTHS_CODE,
    REPORTING_PERIOD_YEARS_CODE,
)


def get_example_four_dataframe(session, airline, year, reporting_airport=None):
    """Create dataframe by merging the cube and datagrid results together."""
    if year is None:
        varcodes = [ORIGIN_DESTINATION_CODE, REPORTING_PERIOD_YEARS_CODE]
        reporting_period_desc = "Reporting Period Year"
    else:
        varcodes = [ORIGIN_DESTINATION_CODE, REPORTING_PERIOD_MONTHS_CODE]
        reporting_period_desc = "Reporting Period Month"

    airline = airline.upper()
    if reporting_airport is not None:
        reporting_airport = reporting_airport.upper()

    cube = get_example_four_cube(session, varcodes, airline, year, reporting_airport)
    cube_df = make_cube_dataframe(cube, reporting_period_desc, year)

    datagrid = get_example_four_datagrid(session, airline)
    datagrid_df = datagrid.to_df()

    df = pd.merge(cube_df, datagrid_df, how="right", on="Origin Destination")

    # Filter df to only include Origin Destinations that have had at least one flight in the date range selected
    grouped_df = df.groupby("Origin Destination").sum()
    filtered_df = grouped_df.loc[grouped_df["Flight Routes"] > 0]
    df = df.loc[df["Origin Destination"].isin(filtered_df.index)]
    return df


def get_example_four_cube(
    session,
    varcodes,
    selected_airline,
    selected_year=None,
    selected_reporting_airport=None,
):
    """Get 2D cube of number of flight routes per airline per time period."""
    routes = session.tables["Flight Route"]
    airports = session.tables["Reporting Airport"]

    selection = routes[AIRLINE_NAME_CODE] == selected_airline
    if selected_year is not None:
        selection &= routes[REPORTING_PERIOD_YEARS_CODE] == selected_year
    if selected_reporting_airport is not None:
        selection &= airports[REPORTING_AIRPORT_CODE] == selected_reporting_airport

    cube = selection.cube([routes[vc] for vc in varcodes])
    return cube


def get_example_four_datagrid(session, airline):
    """Create datagrid giving the co-ordinates of each destination airport the airline goes to."""
    airports = session.tables["Reporting Airport"]
    routes = session.tables["Flight Route"]

    columns = [
        airports[REPORTING_AIRPORT_CODE],
        routes[ORIGIN_AIRPORT_LATITUDE],
        routes[ORIGIN_AIRPORT_LONGITUDE],
        routes[ORIGIN_DESTINATION_CODE],
    ]

    airline_rule = routes[AIRLINE_NAME_CODE] == airline
    one_per_destination = airline_rule.limit(1, per=routes[ORIGIN_DESTINATION_CODE])

    datagrid = one_per_destination.datagrid(columns, max_rows=100000)
    return datagrid


def make_example_four_map(df: pd.DataFrame):
    """Get HTML for plotly bubble map of airline flight routes to destinations."""
    fig = px.scatter_geo(
        df,
        lat="Origin Airport Latitude",
        lon="Origin Airport Longitude",
        animation_frame="Month" if "Month" in df.columns else "Year",
        text="Origin Destination",
        size_max=30,
        size="Flight Routes",
        color="Flight Routes",  # Size and colour of bubbles determined by number of flights there
        color_continuous_scale=px.colors.sequential.YlOrRd,  # Specifies what colour scale to use
        projection="natural earth",
        height=800,
        width=1500,
    )
    return get_html(fig)
