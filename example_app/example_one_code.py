from .fs_var_names import ORIGIN_DESTINATION_CODE, REPORTING_AIRPORT_CODE


def get_example_one_count(session, origin_code, dest_code):
    """Get count of flight routes between origin and dest."""
    routes = session.tables["Flight Route"]
    airports = session.tables["Reporting Airport"]

    origin = airports[REPORTING_AIRPORT_CODE] == origin_code
    dest = routes[ORIGIN_DESTINATION_CODE] == dest_code
    audience = routes * origin & dest
    return audience.count()
