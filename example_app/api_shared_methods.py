import os

import apteco_api as aa
import pandas as pd


def get_selector_variable_codes(session, var_name):
    """Return list of codes possible for a selector variable."""
    api_client = session.api_client
    fss_api = aa.FastStatsSystemsApi(api_client)
    try:
        all_var_codes = fss_api.fast_stats_systems_get_fast_stats_variable_codes(
            session.data_view,
            session.system,
            var_name,
            count=2000,  # Show top 2000 codes
        )
        # Get codes without whitespace after code and in title format
        codes = [str(varcode.code).strip().title() for varcode in all_var_codes.list]
        codes = [
            i if i != "!" else "Unclassified" for i in codes
        ]  # Make unclassifid code ('!') human readable
        return codes
    except aa.ApiException:  # If var_name doesn't exist in system
        print(f"Variable id '{var_name}' doesn't exist in system")
        return None


def get_codes_with_filter(session, varcode, limit=0):
    """Return descriptions of selector 'varcode' with > limit flight routes."""
    routes = session.tables["Flight Route"]

    cube = routes.cube([session.variables[varcode]])
    cube_df = cube.to_df()

    filtered_df = cube_df[cube_df["Flight Routes"] > limit]
    variable_descs = [desc.title() for desc in filtered_df.index.to_list()]

    return variable_descs


def make_cube_dataframe(cube, date_var_desc, selected_year):
    """Create dataframe based on cube, filtered to selected year."""
    df = cube.to_df().reset_index().rename(columns={date_var_desc: "Date"})
    try:
        df.loc[:, "Date"] = pd.to_datetime(df.loc[:, "Date"], format="%Y%m")
        df.loc[:, "Month"] = df.loc[:, "Date"].dt.strftime("%B")
    except ValueError:
        df.loc[:, "Date"] = pd.to_datetime(df.loc[:, "Date"], format="%Y")
        df.loc[:, "Year"] = df.loc[:, "Date"].dt.strftime("%Y")

    if selected_year is not None:
        df = df[df.loc[:, "Date"].dt.year == int(selected_year)]

    return df


def get_html(fig):
    """Return HTML for plotly figure."""
    fig.write_html("fig.html", full_html=False)
    with open("fig.html", "r") as file:
        html = file.read()
    os.remove("fig.html")
    return html
