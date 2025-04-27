"""
Custom format definitions for localization.
"""

# Number formats
NUMBER_FORMAT = "#,##0.##########"
DECIMAL_SEPARATOR = "."
THOUSAND_SEPARATOR = ","
NUMBER_GROUPING = 3

# Date and time formats
DATE_FORMAT = "Y-m-d"
TIME_FORMAT = "H:i:s"
DATETIME_FORMAT = "Y-m-d H:i:s"
SHORT_DATE_FORMAT = "Y-m-d"
SHORT_DATETIME_FORMAT = "Y-m-d H:i"

# Year formats
YEAR_MONTH_FORMAT = "F Y"
MONTH_DAY_FORMAT = "F j"

# Time formats
TIME_INPUT_FORMATS = [
    "%H:%M:%S",  # 14:30:59
    "%H:%M",     # 14:30
]

# Date formats
DATE_INPUT_FORMATS = [
    "%Y-%m-%d",  # 2006-10-25
    "%m/%d/%Y",  # 10/25/2006
    "%m/%d/%y",  # 10/25/06
]

# Datetime formats
DATETIME_INPUT_FORMATS = [
    "%Y-%m-%d %H:%M:%S",     # 2006-10-25 14:30:59
    "%Y-%m-%d %H:%M",        # 2006-10-25 14:30
    "%m/%d/%Y %H:%M:%S",     # 10/25/2006 14:30:59
    "%m/%d/%Y %H:%M",        # 10/25/2006 14:30
    "%m/%d/%y %H:%M:%S",     # 10/25/06 14:30:59
    "%m/%d/%y %H:%M",        # 10/25/06 14:30
] 