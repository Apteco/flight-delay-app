import apteco_api as aa
import pandas as pd
from plotly import express as px

from .api_shared_methods import (
    create_clause,
    create_column,
    create_cube,
    create_dimension,
    create_export,
    create_measure,
    create_query,
    create_topn,
    make_cube_dataframe,
)
from .fs_var_names import (
    AIRLINE_NAME_CODE,
    ORIGIN_DESTINATION_CODE,
    REPORTING_AIRPORT_CODE,
    REPORTING_AIRPORT_LATITUDE,
    REPORTING_AIRPORT_LONGITUDE,
    REPORTING_PERIOD_MONTHS_CODE,
    REPORTING_PERIOD_YEARS_CODE,
)

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def get_example_four_dataframe(session, airline, year, reporting_airport=None):
    """ Create dataframe from merging the cube and export results together. """
    if year is None:
        varcodes = [ORIGIN_DESTINATION_CODE, REPORTING_PERIOD_YEARS_CODE]
    else:
        varcodes = [ORIGIN_DESTINATION_CODE, REPORTING_PERIOD_MONTHS_CODE]

    airline = airline.upper()
    if reporting_airport is not None:
        reporting_airport = reporting_airport.upper()

    cube = get_example_four_cube(session, varcodes, airline, year, reporting_airport)
    cube_df = make_cube_dataframe(cube, year)

    if year is not None:
        cube_df["date"] = cube_df["date"].apply(
            lambda x: MONTHS[int(x[-2:]) - 1] + " " + x[-4:-2]  # Mon YY formatting
        )

    export = get_example_four_export(session, airline)
    export_df = make_export_dataframe(export)

    df = pd.merge(
        cube_df, export_df, how="right", left_on="var_name", right_on="Origin Dest"
    )

    # Filter df to only include Origin Destinations that have had at least one flight in the date range selected
    grouped_df = df.groupby("Origin Dest").sum()
    filtered_df = grouped_df.loc[grouped_df["routes"] > 0]
    df = df.loc[df["Origin Dest"].isin(filtered_df.index)]
    return df


def get_example_four_cube(
    session,
    varcodes,
    selected_airline,
    selected_year=None,
    selected_reporting_airport=None,
):
    """ Get 2D cube of number of flight routes per Airline per time period. """
    cubes_api = aa.CubesApi(session.api_client)

    clauses = [create_clause(session, AIRLINE_NAME_CODE, [selected_airline])]

    if selected_year is not None:
        clauses.append(
            create_clause(session, REPORTING_PERIOD_YEARS_CODE, [selected_year])
        )

    if selected_reporting_airport is not None:
        clauses.append(
            create_clause(session, REPORTING_AIRPORT_CODE, [selected_reporting_airport])
        )

    logic = aa.Logic(operation="AND", operands=clauses, table_name="Flight Route")
    query = create_query(rule=aa.Rule(clause=aa.Clause(logic=logic)))

    dimensions = [create_dimension(code) for code in varcodes]
    measure = create_measure()
    cube = create_cube(query, dimensions, [measure])
    cube_result = cubes_api.cubes_calculate_cube_synchronously(
        session.data_view, session.system, cube=cube
    )
    return cube_result


def get_example_four_export(session, airline):
    """ Create export giving the co-ordinates of each destination airport the airline goes to. """
    exports_api = aa.ExportsApi(session.api_client)

    # Get destination name and co-ordinates
    column_codes = [
        ORIGIN_DESTINATION_CODE,
        REPORTING_AIRPORT_LATITUDE,
        REPORTING_AIRPORT_LONGITUDE,
    ]
    columns = [create_column(code.title(), code) for code in column_codes]

    # Filter to only airports that airline goes to
    airline_rule = create_clause(session, AIRLINE_NAME_CODE, [airline])
    # Ensures max 1 row per unique destination
    one_per_destination = create_topn(ORIGIN_DESTINATION_CODE)

    query = create_query(rule=airline_rule, top_n=one_per_destination)

    export = create_export(query, columns)
    export_result = exports_api.exports_perform_export_synchronously(
        session.data_view, session.system, export=export
    )
    return export_result


def make_export_dataframe(export):
    """ Create dataframe from export data """
    export_data = [row.descriptions.split("\t") for row in export.rows]
    export_df = pd.DataFrame(export_data, columns=["Origin Dest", "Lat", "Long"])
    return export_df


def make_example_four_map(df):
    """ Get html for plotly bubble map of airline flight routes to destinations """
    fig = px.scatter_geo(
        df,
        lat="Lat",
        lon="Long",
        animation_frame="date",
        text="Origin Dest",
        size_max=30,
        size="routes",
        color="routes",  # Size and colour of bubbles determined by number of flights there
        color_continuous_scale=px.colors.sequential.YlOrRd,  # Specifies what colour scale to use
        projection="natural earth",
        height=800,
        width=1500,
    )
    fig.write_html("fig.html", full_html=False)
    with open("fig.html", "r") as file:
        html = file.read()
    return html
