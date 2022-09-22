import io

from example_app.fs_var_names import REPORTING_PERIOD_CODE


def get_codes_with_filter(session, varcode, limit=0):
    """Return descriptions of selector 'varcode' with > limit flight routes."""
    routes = session.tables["Flight Route"]

    cube = routes.cube([session.variables[varcode]])
    cube_df = cube.to_df()

    filtered_df = cube_df[cube_df["Flight Routes"] > limit]
    variable_descs = [desc.title() for desc in filtered_df.index.to_list()]

    return variable_descs


def get_reporting_years(session):
    """Return list of options for reporting years."""
    reporting_period_var = session.variables[REPORTING_PERIOD_CODE]

    year_range = range(reporting_period_var.min_date.year, reporting_period_var.max_date.year + 1)
    reporting_years = ["Show All Years"] + [str(year) for year in year_range]

    return reporting_years


def create_and_filter_cube_dataframe(cube, selected_year):
    """Create dataframe based on cube, filtered to selected year."""

    if selected_year is not None:
        date_var_desc = "Reporting Period (Month)"
        new_col_name = "Month"
        new_col_fmt = "%B"
    else:
        date_var_desc = "Reporting Period (Year)"
        new_col_name = "Year"
        new_col_fmt = "%Y"

    df = cube.to_df().reset_index().rename(columns={date_var_desc: "Date"})
    df.loc[:, new_col_name] = df.loc[:, "Date"].dt.strftime(new_col_fmt)

    if selected_year is not None:
        df = df[df.loc[:, "Date"].dt.year == int(selected_year)]

    return df


def get_html(fig):
    """Return HTML for plotly figure."""
    with io.StringIO() as file:
        fig.write_html(file, full_html=False)
        return file.getvalue()
