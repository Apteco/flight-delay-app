from apteco.query import SelectorClause

from .fs_var_names import REPORTING_AIRPORT_CODE


def route_counts(session, origin_code, dest_code):
    """ Get count of flight routes between origin and dest. """
    routes = session.tables["Flight Route"]
    # airports = session.tables["Reporting Airport"]
    # origin = airports["Reporting Airport"] == origin_code
    origin = SelectorClause(
        "Reporting Airport", REPORTING_AIRPORT_CODE, [origin_code], session=session
    )
    dest = routes["Origin Destination"] == dest_code
    audience = routes * origin & dest
    return audience.select().count
