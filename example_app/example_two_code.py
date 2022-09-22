import pandas as pd
from plotly import graph_objects as go

from .api_shared_methods import get_html, make_cube_dataframe
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


def get_example_two_dataframe(session, measure_var_code, date_var_code, selected_year, limit):
    """Create dataframe for example two graph, filtered by top selectors if set."""
    measure_var = session.variables[measure_var_code]
    date_var = session.variables[date_var_code]
    measure_var_desc = measure_var.description
    date_var_desc = date_var.description

    cube = get_example_two_cube(session, measure_var_code, date_var_code, selected_year=selected_year)
    df = make_cube_dataframe(cube, date_var_desc, selected_year)

    # Filter the dataframe to only return rows regarding the top selectors
    if limit > 0:
        top_names = df.groupby(measure_var_desc).sum().nlargest(limit, "Flight Routes")
        df = df[df[measure_var_desc].isin(top_names.index)]
    return df


def get_example_two_cube(session, measure_var_code, date_var_code, selected_year=None):
    """Create 2D cube of flight routes per 'measure' variable, per date selector."""
    routes = session.tables["Flight Route"]

    # If specified, only return flight counts for the selected year
    if selected_year is not None:
        query = routes[REPORTING_PERIOD_YEARS_CODE] == selected_year
    # Else, no underlying base query
    else:
        query = None

    dimensions = [session.variables[code] for code in (measure_var_code, date_var_code)]
    cube = routes.cube(dimensions, selection=query)
    return cube


def make_example_two_graph(df: pd.DataFrame, measure_var_desc, year=None):
    """Return HTML for plotly graph of number of flights over time per 'measure'."""
    fig = go.Figure(data=go.Scatter())

    # Add line trace for each selector description
    for i, elem in enumerate(sorted(set(df[measure_var_desc]))):
        mask = df[measure_var_desc] == elem
        fig.add_trace(
            go.Scatter(
                mode="lines+markers",
                x=df[mask]["Date"],
                y=df[mask]["Flight Routes"],
                name=elem,
            )
        )

    fig.update_layout(
        xaxis={"title": "Year"},
        yaxis={"title": "Number of Flight Routes"},
        width=1500,
        height=800,
    )
    # If showing months, show natural language month values
    if year is not None:
        fig.update_xaxes(
            tickvals=df["Date"], ticktext=MONTHS, title_text=f"Month ({year})"
        )
    return get_html(fig)
