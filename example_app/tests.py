import apteco_api as aa
from apteco.session import Session
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from .api_shared_methods import get_codes_with_filter, get_selector_variable_codes
from .example_four_code import (
    get_example_four_cube,
    get_example_four_dataframe,
    get_example_four_datagrid,
)
from .example_one_code import get_example_one_count
from .example_three_code import get_example_three_dataframe
from .example_two_code import get_example_two_dataframe
from .fs_credentials import DATA_VIEW, PASSWORD, SYSTEM_NAME, URL, USERNAME
from .fs_var_names import (
    AIRLINE_NAME_CODE,
    ORIGIN_DESTINATION_CODE,
    ORIGIN_AIRPORT_LATITUDE,
    ORIGIN_AIRPORT_LONGITUDE,
    REPORTING_AIRPORT_CODE,
    REPORTING_PERIOD_CODE,
)
from .views import start_session

session_details = {
    "username": USERNAME,
    "password": PASSWORD,
    "url": URL,
    "system_name": SYSTEM_NAME,
    "data_view": DATA_VIEW,
}
session = start_session(USERNAME, PASSWORD, URL, SYSTEM_NAME, DATA_VIEW)
routes = session.tables["Flight Route"]
airports = session.tables["Reporting Airport"]


class TestSessionCreation(TestCase):
    def test_pyapteco_session(self):
        self.assertIsInstance(session, Session)


class TestApiEndpoints(TestCase):
    def setUp(self):
        self.codes = get_selector_variable_codes(session, REPORTING_AIRPORT_CODE)

    def test_variable_codes(self):
        self.assertNotEqual(
            self.codes, None, "Can't get variables codes through OrbitAPI"
        )
        self.assertTrue(any("Heathrow" in code for code in self.codes))

    def test_count_with_var_codes(self):
        try:
            aberdeen = str(self.codes[1].upper())
            flights_from_aberdeen = airports[REPORTING_AIRPORT_CODE] == aberdeen
            query_count = (routes * flights_from_aberdeen).count()
            self.assertEqual(query_count, 4540)
        except aa.ApiException:
            self.assertTrue(False, "ApiException in getting variable codes")

    def test_datagrid(self):
        malaga_las_palmas = routes[ORIGIN_DESTINATION_CODE] == ["MALAGA", "LAS PALMAS"]
        cols = [routes[ORIGIN_AIRPORT_LATITUDE], routes[ORIGIN_AIRPORT_LONGITUDE]]
        dg = malaga_las_palmas.datagrid(cols, max_rows=10)
        test_row = dg._data[0]
        self.assertEqual(test_row, ("   36.674900", "   -4.499110"))

    def test_cube(self):
        dims = [routes[REPORTING_PERIOD_CODE].year, airports[REPORTING_AIRPORT_CODE]]
        cube = routes.cube(dims)
        test_row = cube._data[0][:, 7].tolist()
        self.assertEqual(
            test_row,
            ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "179", "1633", "1765", "1896", "5473"],
        )


class TestSharedExampleLogic(TestCase):
    def test_get_codes_with_filter_limit_zero(self):
        codes = get_codes_with_filter(session, REPORTING_AIRPORT_CODE)
        self.assertEqual(len(codes), 25)
        self.assertEqual(codes[10], "Edinburgh")

    def test_get_codes_with_filter_limit_nonzero(self):
        codes = get_codes_with_filter(session, AIRLINE_NAME_CODE, 10000)
        self.assertEqual(len(codes), 19)
        self.assertEqual(codes[10], "Flybe Ltd")

    def test_get_selector_variable_codes(self):
        codes = get_selector_variable_codes(session, ORIGIN_DESTINATION_CODE)
        self.assertEqual(len(codes), 1261)
        self.assertEqual(codes[0], "Unclassified")


class TestExampleOneLogic(TestCase):
    def test_nonzero_count(self):
        count = get_example_one_count(session, "ABERDEEN", "FARO")
        self.assertEqual(count, 48)

    def test_zero_count(self):
        count = get_example_one_count(session, "JERSEY", "MALTA")
        self.assertEqual(count, 0)


class TestExampleTwoLogic(TestCase):
    def test_example_two_dataframe_all_years_no_limit(self):
        expected_counts = [0, 1818, 2666, 2850, 2805, 2471, 3181, 3193, 2942, 3217, 3286, 3564, 3623, 3595, 3010, 2829, 2711, 2682, 2681, 2814, 2793, 3347, 2961]
        df = get_example_two_dataframe(session, REPORTING_AIRPORT_CODE, None, 0)
        newcastle_counts = df.loc[df["Reporting Airport"] == "NEWCASTLE"]["Flight Routes"].to_list()
        self.assertEqual(newcastle_counts, expected_counts)

    def test_example_two_dataframe_selected_year_limit_10(self):
        expected_counts = [384, 638, 381, 191, 203, 84, 596, 175, 406, 84]
        df = get_example_two_dataframe(session, AIRLINE_NAME_CODE, "2015", 10)
        jan15_counts = df.loc[df["Date"] == "20150101"]["Flight Routes"].to_list()
        self.assertEqual(jan15_counts, expected_counts)


class TestExampleThreeLogic(TestCase):
    def setUp(self):
        self.df = get_example_three_dataframe(session, "EXETER")

    def test_example_three_dataframe_shape(self):
        self.assertEqual(self.df.shape, (114, 5))

    def test_example_three_dataframe_data(self):
        expected_data = [-6.270070, 53.421300, -3.413890, 50.734400, "Exeter - Dublin"]
        exeter_dublin = self.df[self.df["Flight Route Name"] == "Exeter - Dublin"]
        self.assertEqual(len(exeter_dublin), 1)
        self.assertEqual(exeter_dublin.iloc[0].to_list(), expected_data)

    def test_example_three_dataframe_reporting_coords(self):
        self.assertTrue((self.df["Reporting Airport Longitude"] == -3.413890).all())
        self.assertTrue((self.df["Reporting Airport Latitude"] == 50.734400).all())


class TestExampleFourLogic(TestCase):
    def test_example_four_cube(self):
        cube = get_example_four_cube(session, "RYANAIR", None, "GATWICK")
        df = cube.to_df().reset_index()
        expected_counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 4, 24, 24, 22, 16, 20, 24, 20]
        seville_counts = df[df["Origin Destination"] == "SEVILLE"]["Flight Routes"].to_list()
        self.assertEqual(df.shape, (28980, 3))
        self.assertEqual(seville_counts, expected_counts)

    def test_example_four_datagrid(self):
        dg = get_example_four_datagrid(session, "BRITISH AIRWAYS PLC")
        # df = make_export_dataframe(export)
        df = dg.to_df()
        expected_details = ["HEATHROW", 39.7684,  -86.1581, "INDIANAPOLIS"]
        indianapolic_details = df[df["Origin Destination"] == "INDIANAPOLIS"].iloc[0].to_list()
        self.assertEqual(df.shape, (411, 4))
        self.assertEqual(indianapolic_details, expected_details)

    def test_example_four_dataframe_all_years_no_origin_airport(self):
        df = get_example_four_dataframe(session, "FLYBE LTD", None, None)
        stansted_routes = df[df["Origin Destination"] == "STANSTED"]["Flight Routes"].sum()

        for dest in set(df["Origin Destination"].to_list()):
            self.assertEqual(len(set(df[df["Origin Destination"] == dest]["Origin Airport Latitude"].to_list())), 1)
            self.assertEqual(len(set(df[df["Origin Destination"] == dest]["Origin Airport Longitude"].to_list())), 1)

        self.assertEqual(df.shape, (4071, 7))
        self.assertEqual(stansted_routes, 42)

    def test_example_four_dataframe_selected_year_selected_origin_airport(self):
        df = get_example_four_dataframe(
            session, "BRITISH AIRWAYS PLC", "1996", "HEATHROW"
        )
        feb_routes = df[df["Date"] == "19960201"]["Flight Routes"].sum()

        for dest in set(df["Origin Destination"].to_list()):
            self.assertEqual(len(set(df[df["Origin Destination"] == dest]["Origin Airport Latitude"].to_list())), 1)
            self.assertEqual(len(set(df[df["Origin Destination"] == dest]["Origin Airport Longitude"].to_list())), 1)

        self.assertEqual(df.shape, (1944, 7))
        self.assertEqual(feb_routes, 232)


class TestLoggedOut(SimpleTestCase):
    def test_index_page_html(self):
        response = self.client.get("")
        self.assertContains(
            response, '<h2>Please <a href="/login_local/">login</a></h2>'
        )
        self.assertNotContains(response, "<h1>Welcome to your home page!</h1>")


class TestHomePage(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", password="this word will pass")
        self.client.login(username="test", password="this word will pass")

    def test_home_page_html(self):
        response = self.client.get("")
        self.assertContains(response, "<h1>Welcome to your home page!</h1>")


class TestLoginApi(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", password="this word will pass")
        self.client.login(username="test", password="this word will pass")

    def test_login_api(self):
        response = self.client.post("/login_api/login_api_proc", session_details)
        self.assertContains(response, "Successfully logged in")
        self.assertNotContains(response, "Incorrect login details")


class TestExampleOnePage(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", password="this word will pass")
        self.client.login(username="test", password="this word will pass")
        self.login_api_response = self.client.post(
            "/login_api/login_api_proc", session_details
        )

    def test_example_one_with_flights(self):
        form_details = {"origin_code": "Birmingham", "dest_code": "Las Palmas"}
        response = self.client.post("/example_one/show_count", form_details)
        self.assertContains(
            response, "2511 flight routes were found between Birmingham and Las Palmas"
        )

    def test_example_one_without_flights(self):
        form_details = {"origin_code": "Jersey", "dest_code": "Malta"}
        response = self.client.post("/example_one/show_count", form_details)
        self.assertContains(
            response, "0 flight routes were found between Jersey and Malta"
        )
