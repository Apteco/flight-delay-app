"""Central reference point for FastStats system variable names.

The numbers and letters in the comments note where the variable is used in the project:
- 1: example_one_code.py
- 2: example_two_code.py
- 3: example_three_code.py
- 4: example_four_code.py
- v: views.py
- t: tests.py

"""

# Virtual Variables
# Combined Categories VV: Reporting Period combined up to months: 4, v, t
REPORTING_PERIOD_MONTHS_CODE = "fl1FOVQJ"
# Combined Categories VV: Reporting Period Months combined up to years: 2, 4, v, t
REPORTING_PERIOD_YEARS_CODE = "fl1FOVRG"
# Expression VV: Flight route name: 3
ROUTE_NAME_CODE = "fl1H1F70"

#
REPORTING_AIRPORT_CODE = "reRepor1"  # 1, 3, 4, v
AIRLINE_NAME_CODE = "flAirlin"  # 4, v
ORIGIN_DESTINATION_CODE = "flOrigi1"  # 4, v

# Latitude and Longitude variables
ORIGIN_AIRPORT_LONGITUDE = "AiLongit"  # 3
ORIGIN_AIRPORT_LATITUDE = "AiLatitu"  # 3
REPORTING_AIRPORT_LONGITUDE = "AiLongi1"  # 3, 4
REPORTING_AIRPORT_LATITUDE = "AiLatit1"  # 3, 4
