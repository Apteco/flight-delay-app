import apteco_api as aa
from apteco.session import Session, login_with_password
from django.contrib.auth import authenticate
from django.contrib.auth import login as dj_login
from django.contrib.auth import logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .api_shared_methods import get_codes_with_filter, get_selector_variable_codes
from .example_four_code import get_example_four_dataframe, make_example_four_map
from .example_one_code import route_counts
from .example_three_code import get_datagrid_as_dataframe, make_example_three_map
from .example_two_code import get_example_two_dataframe, make_example_two_graph
from .forms import LoginApiForm, LoginUserForm
from .fs_var_names import (
    AIRLINE_NAME_CODE,
    ORIGIN_DESTINATION_CODE,
    REPORTING_AIRPORT_CODE,
    REPORTING_PERIOD_MONTHS_CODE,
    REPORTING_PERIOD_YEARS_CODE,
)

EXAMPLE_ONE_DESTS = ["Malaga", "Faro", "Las Palmas", "Malta"]
EXAMPLE_TWO_SELECTORS = ["Reporting Airport", "Airline Name", "Destination"]


def index(request, context=None):
    """  Return the home page. """
    if context is None:
        context = {}
    context.update({"title": "Index Page", "active": "home"})
    if request.user.is_authenticated:
        return home(request, context=context)
    else:
        return render(request, "index.html", context)


@login_required
def home(request, context=None):
    """ Return home screen. """
    if context is None:
        context = {}

    session = request.session.get("ApiSession", None)
    if session is not None:
        session = Session.deserialize(session)
        context.update(
            {
                "system_name": session.system,
                "data_view": session.data_view,
                "access_token": session.access_token,
                "session_id": session.session_id,
            }
        )
    context.update({"title": "Home"})
    return render(request, "home.html", context)


def login_local(request, context=None):
    """" Create login_local form and return login_local page. """
    if context is None:
        context = {}
    form = LoginUserForm()
    context.update({"title": "Log In", "active": "login_local", "form": form})
    return render(request, "login_local.html", context)


def login_local_proc(request):
    """ Check user is in DB, start session if details correct. """
    if request.method == "POST":
        form = LoginUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                dj_login(request, user)
                context = {
                    "title": "Home Page",
                    "active": "home",
                    "alert_type": "alert-success",
                    "alert_message": "Successfully logged in",
                }
                return index(request, context)
            return incorrect_details(request, "login_local")
        return incorrect_details(request, "login_local")
    return redirect("login_local")


@login_required
def login_api(request, context=None):
    if context is None:
        context = {}
    """ Create API login_local form and return api login_local page. """
    form = LoginApiForm()
    context.update({"title": "FastStats Login", "active": "login_api", "form": form})
    return render(request, "login_api.html", context)


@login_required
def login_api_proc(request):
    """" Check API session details, create and store session if correct details. """
    if request.method == "POST":
        form = LoginApiForm(request.POST)
        if form.is_valid():
            session = start_session(
                form.cleaned_data["username"],
                form.cleaned_data["password"],
                form.cleaned_data["url"],
                form.cleaned_data["system_name"],
                form.cleaned_data["data_view"],
            )
            if session is not None:
                request.session["ApiSession"] = session.serialize()
                context = {
                    "alert_type": "alert-success",
                    "alert_message": "Successfully logged in",
                }
                return index(request, context)
            return incorrect_details(request, "login_api")
        return incorrect_details(request, "login_api")
    return redirect("login_api")


@login_required
def logout(request):
    """" Log user out, delete session info. """
    session = request.session.get("ApiSession", None)
    if session is not None:
        session = Session.deserialize(request.session["ApiSession"])
        aa.SessionsApi(session.api_client).sessions_logout_session(
            session.data_view, session.session_id
        )
    username = request.user.username
    dj_logout(request)

    context = {
        "alert_type": "alert-success",
        "alert_message": username + " has been logged out.",
    }
    return index(request, context)


@login_required
def logout_api(request):
    """ Logs out of FastStats session. """
    session = request.session.get("ApiSession", None)
    if session is not None:
        session = Session.deserialize(request.session["ApiSession"])
        aa.SessionsApi(session.api_client).sessions_logout_session(
            session.data_view, session.session_id
        )
        del request.session["ApiSession"]

    context = {
        "alert_type": "alert-success",
        "alert_message": "Logged out of FastStats session.",
    }
    return index(request, context)


@login_required
def example_one(request, context=None):
    """ Return web page for example one. """
    if context is None:
        context = {}

    session = request.session.get("ApiSession", None)
    if session is None:
        return no_session_set(request)
    session = Session.deserialize(session)

    origin_codes = get_codes_with_filter(session, REPORTING_AIRPORT_CODE, 0)
    context.update(
        {
            "title": "Example 1",
            "active": "example_one",
            "origin_codes": origin_codes,
            "dest_codes": EXAMPLE_ONE_DESTS,
        }
    )
    return render(request, "example_one.html", context)


@login_required
def example_one_count(request):
    """ Return count from user input in example one. """
    if request.method == "POST":
        session = request.session.get("ApiSession", None)
        if session is None:
            return no_session_set(request)
        session = Session.deserialize(session)

        origin = request.POST["origin_code"]
        dest = request.POST["dest_code"]

        counts_per_year = route_counts(session, origin.upper(), dest.upper())
        context = {
            "count": counts_per_year,
            "selected_origin": origin,
            "selected_dest": dest,
            "selected_origin_title": origin.title(),
            "selected_dest_title": dest.title(),
        }
        return example_one(request, context)
    return redirect("example_one")


@login_required
def example_two(request, context=None):
    """ Return web page for example two. """
    if context is None:
        context = {}

    session = request.session.get("ApiSession", None)
    if session is None:
        return no_session_set(request)
    session = Session.deserialize(session)

    reporting_years = get_selector_variable_codes(session, REPORTING_PERIOD_YEARS_CODE)
    reporting_years[
        0
    ] = "Show All Years"  # Remove '0000' year and include show all option
    context.update(
        {
            "title": "Example 2",
            "active": "example_two",
            "selector_cols": EXAMPLE_TWO_SELECTORS,
            "date_options": ["Years", "Months"],
            "years": reporting_years,
        }
    )
    return render(request, "example_two.html", context)


@login_required
def example_two_graph(request):
    """ Return graph from user input in example two. """
    if request.method == "POST":
        session = request.session.get("ApiSession", None)
        if session is None:
            return no_session_set(request)
        session = Session.deserialize(session)

        first_selector = request.POST["first_selector"]
        date_option = request.POST["date_option"]
        top_pick = request.POST["top_choice"]

        measure_selector_code = encode_variable(first_selector)
        measure_var_desc = session.variables[measure_selector_code].description

        if date_option == "Show All Years":
            selected_year = None
            date_selector_code = REPORTING_PERIOD_YEARS_CODE
        else:
            selected_year = date_option
            date_selector_code = REPORTING_PERIOD_MONTHS_CODE

        limit = int(top_pick)  # if limit = 0, same as None

        df = get_example_two_dataframe(session, measure_selector_code, date_selector_code, selected_year, limit)
        graph_html = make_example_two_graph(df, measure_var_desc, selected_year)
        context = {
            "first_selected_col": first_selector,
            "selected_year": date_option,
            "selected_top_choice": top_pick,
            "graph": graph_html,
        }
        return example_two(request, context)
    return redirect("example_two")


@login_required
def example_three(request, context=None):
    """ Return web page for example three. """
    if context is None:
        context = {}

    session = request.session.get("ApiSession", None)
    if session is None:
        return no_session_set(request)
    session = Session.deserialize(session)

    airport_names = get_codes_with_filter(session, REPORTING_AIRPORT_CODE, 0)
    context.update(
        {
            "title": "Example 3",
            "active": "example_three",
            "airport_names": airport_names,
        }
    )
    return render(request, "example_three.html", context)


@login_required
def example_three_map(request):
    """ Return graph from user input in example three. """
    # Get selected airport, update context that that one is selected, and encode it
    if request.method == "POST":
        session = request.session.get("ApiSession", None)
        if session is None:
            return no_session_set(request)
        session = Session.deserialize(session)

        reporting_airport = request.POST["reporting_airport"]

        df = get_datagrid_as_dataframe(session, reporting_airport.upper())
        graph_html = make_example_three_map(df)
        context = {"graph": graph_html, "selected_airport": reporting_airport}
        return example_three(request, context)
    return redirect("example_three")


@login_required
def example_four(request, context=None):
    """ Return web page for example three. """
    if context is None:
        context = {}
    session = request.session.get("ApiSession", None)
    if session is None:
        return no_session_set(request)
    session = Session.deserialize(session)

    airline_names = get_codes_with_filter(session, AIRLINE_NAME_CODE, 10001)
    airport_names = get_codes_with_filter(session, REPORTING_AIRPORT_CODE, 0)
    airport_names.insert(0, " ")  # First option is blank
    years = get_selector_variable_codes(session, REPORTING_PERIOD_YEARS_CODE)
    years[0] = "Show All Years"  # Remove '0000' year and include show all option
    context.update(
        {
            "title": "Example 4",
            "active": "example_four",
            "airline_names": airline_names,
            "years": years,
            "reporting_airports": airport_names,
        }
    )
    return render(request, "example_four.html", context)


@login_required
def example_four_map(request):
    """ Return graph from user input in example three. """
    if request.method == "POST":
        session = request.session.get("ApiSession", None)
        if session is None:
            return no_session_set(request)
        session = Session.deserialize(session)

        airline = request.POST["airline_name"]
        date_option = request.POST["year"]
        reporting_airport = request.POST["reporting_airport"]

        if date_option == "Show All Years":
            selected_year = None
        else:
            selected_year = date_option

        if reporting_airport == "":
            reporting_airport = None

        df = get_example_four_dataframe(
            session, airline, selected_year, reporting_airport
        )

        if (df["Flight Routes"] == 0).all():
            graph_html = """<div class="alert alert-danger" role="alert" style="margin-left:14px;">
                                No flight routes were found in this selection
                            </div>"""
        else:
            graph_html = make_example_four_map(df)
        context = {
            "graph": graph_html,
            "selected_airline": airline,
            "selected_year": selected_year,
            "selected_airport": reporting_airport,
        }
        return example_four(request, context)
    return redirect("example_four")


# Helper functions
def start_session(username, password, url, system_name, data_view):
    try:
        session = login_with_password(url, data_view, system_name, username, password)
        return session
    except aa.ApiException:
        return None


def not_logged_in(request):
    """ Return error page if login required for web page. """
    context = {
        "alert_type": "alert-danger",
        "alert_message": "The page you were trying to access requires you to login",
    }
    return login_local(request, context)


def incorrect_details(request, page):
    """ Return context for incorrect login_local on login_local pages. """
    context = {
        "alert_type": "alert-danger",
        "alert_message": "Incorrect login details, please try again",
    }
    if page == "login_local":
        return login_local(request, context)
    if page == "login_api":
        return login_api(request, context)
    return redirect("index")


def no_session_set(request):
    context = {
        "alert_type": "alert-danger",
        "alert_message": "Please log in to a FastStats system to access that page. ",
    }
    return index(request, context)


def encode_variable(var):
    """ Return variable code from natural language description. """
    codec = {
        "Reporting Airport": REPORTING_AIRPORT_CODE,
        "Airline Name": AIRLINE_NAME_CODE,
        "Destination": ORIGIN_DESTINATION_CODE,
    }
    try:
        return codec[var]
    except KeyError:
        print(f"Encoding '{var}' is not defined")
        return None
