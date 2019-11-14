import apteco_api as aa
from plotly import graph_objects as go

from .api_shared_methods import (
    create_clause,
    create_cube,
    create_dimension,
    create_measure,
    create_query,
    get_html,
    make_cube_dataframe,
)
from .fs_var_names import REPORTING_PERIOD_YEARS_CODE

# Used for the x axis in example two graph
MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def get_example_two_dataframe(session, varcodes, selected_year, limit):
    """ Create dataframe for example two graph, filtered by top selectors if set. """
    cube = get_example_two_cube(session, varcodes, selected_year=selected_year)
    df = make_cube_dataframe(cube, selected_year)

    # Filter the dataframe to only return rows regarding the top selectors
    if limit > 0:
        top_names = df.groupby("var_name").sum().nlargest(limit, "routes")
        df = df[df["var_name"].isin(top_names.index)]
    return df


def get_example_two_cube(session, varcodes, selected_year=None):
    """ Create 2D cube of flight routes per selector variable description, per date selector. """
    cubes_api = aa.CubesApi(session.api_client)

    # If no selected year, no underlying base query
    if selected_year is None:
        query = create_query()
    # Else, only return flight counts for the selected year
    else:
        year_rule = aa.Rule(
            create_clause(session, REPORTING_PERIOD_YEARS_CODE, [selected_year])
        )
        query = create_query(rule=year_rule)

    dimensions = [create_dimension(code) for code in varcodes]
    measure = create_measure()
    cube = create_cube(query, dimensions, [measure])
    cube_result = cubes_api.cubes_calculate_cube_synchronously(
        session.data_view, session.system, cube=cube
    )
    return cube_result


def make_example_two_graph(df, date=None):
    """ Return html code for plotly graph of number of flights over time per selector description. """
    fig = go.Figure(data=go.Scatter())

    # Add line trace for each selector description
    for i, elem in enumerate(sorted(set(df["var_name"]))):
        mask = df["var_name"] == elem
        fig.add_trace(
            go.Scatter(
                mode="lines+markers",
                x=df[mask]["date"],
                y=df[mask]["routes"],
                name=elem,
            )
        )

    fig.update_layout(
        xaxis={"title": "Years"},
        yaxis={"title": "Number of Flight Routes"},
        width=1500,
        height=800,
    )
    # If showing months, show natural language month values
    if date is not None:
        print(date)
        print(df["date"])
        fig.update_xaxes(
            tickvals=df["date"].unique(), ticktext=MONTHS, title_text="Months"
        )
    return get_html(fig)
