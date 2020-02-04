import os

import apteco_api as aa
import numpy as np
import pandas as pd
from apteco.query import SelectorClause


def get_selector_variable_codes(session, var_name):
    """ Return list of codes possible for a selector variable. """
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
    """ Return descriptions of selector 'varcode' with > limit flight routes. """
    query = create_query()
    cube_api = aa.CubesApi(session.api_client)

    dimension = create_dimension(varcode)
    measure = create_measure()
    cube = create_cube(query, [dimension], [measure])
    cube_result = cube_api.cubes_calculate_cube_synchronously(
        session.data_view, session.system, cube=cube
    )

    descriptions = cube_result.dimension_results[0].header_descriptions.split(
        "\t"
    )  # Get varcode names as list
    counts = (
        cube_result.measure_results[0].rows[0].split("\t")
    )  # Get counts for each varname as list

    # Only return varnames with > limit count
    variable_descs = [
        desc.title() for i, desc in enumerate(descriptions) if int(counts[i]) > limit
    ]
    variable_descs = variable_descs[:-1]  # Get rid of iTOTAL
    return variable_descs


def make_cube_dataframe(cube, selected_year):
    """ Create dataframe based on cube_result.  """
    var_names, counts = get_dimension_measures(cube)
    dates = cube.dimension_results[1].header_descriptions.split("\t")

    df_data = [
        [var_name, date, int(counts[j][i])]
        for j, date in enumerate(dates)
        for i, var_name in enumerate(var_names)
        if selected_year is None or date[:4] == selected_year
    ]
    df = pd.DataFrame(df_data, columns=["var_name", "date", "routes"])
    df = df.loc[df["var_name"] != "iTOTAL"]  # Remove iTOTAL row from var_name

    # Remove iTOTAL and irrelevant rows from date
    if selected_year is None:
        df = df.loc[~df["date"].isin(["iTOTAL", "0000"])]
    else:
        df = df.loc[~df["date"].isin(["iTOTAL", "000000"])]

    return df


def get_dimension_measures(cube):
    """ Extract selector variable description names and their flight route counts from a cube result. """
    # Get variable names and counts from cube
    variable_names = cube.dimension_results[0].header_descriptions.split("\t")
    counts = [i.split("\t") for i in cube.measure_results[0].rows]

    # Get list of all variables with 0 flights for every year / month
    to_delete = [
        i
        for i in range(len(counts[0]))
        if all(elem == "0" for elem in [counts[j][i] for j in range(len(counts))])
    ]
    variable_names = np.delete(variable_names, to_delete).tolist()

    # Remove counts for those selected variables
    deleted = 0
    for i in to_delete:
        for j in range(len(counts)):
            del counts[j][i - deleted]
        deleted += 1

    return variable_names, counts


def get_html(fig):
    """ Return html for plotly figure. """
    fig.write_html("fig.html", full_html=False)
    with open("fig.html", "r") as file:
        html = file.read()
    os.remove("fig.html")
    return html


# apteco-api object creation
def create_clause(session, varcode, filters):
    """ Return clause of variable (varcode), with list of filters applied. """
    return SelectorClause("Flight Route", varcode, filters, session=session)._to_model()


def create_topn(group_var):
    """ Return top n to filter the parent query to only one result per the grouping variable. """
    return aa.TopN(grouping_variable_name=group_var, group_max=1)


def create_query(rule=None, top_n=None):
    """ Return query from selection, with possible given rule or top_n. """
    return aa.Query(aa.Selection(table_name="Flight Route", rule=rule, top_n=top_n))


def create_measure():
    """ Return count measure on Flight Route table. """
    return aa.Measure(id="Count", resolve_table_name="Flight Route", function="Count")


def create_column(col_name, varcode):
    """ Return column for export with values of the variable code given """
    return aa.Column(id=col_name, variable_name=varcode, column_header=col_name)


def create_dimension(varcode):
    """ Return dimension of varcode for a cube. """
    return aa.Dimension(id=varcode, type="Selector", variable_name=varcode)


def create_cube(base_query, dimensions, measures):
    """ Return cube from give base query, dimensions and measures. """
    return aa.Cube(
        base_query=base_query,
        resolve_table_name="Flight Route",
        storage="Full",
        dimensions=dimensions,
        measures=measures,
    )


def create_export(base_query, columns):
    """ Return export from given base query and column measures. """
    return aa.Export(
        base_query=base_query,
        resolve_table_name="Flight Route",
        maximum_number_of_rows_to_browse=100000,
        return_browse_rows=True,
        columns=columns,
    )
