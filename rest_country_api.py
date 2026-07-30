# This file name is rest_country_api.py
import re
import requests
from input import trip

# The entirety of the code here is to access the countries.dev API and get
# information on a country: name, capital, region, population, currencies,
# languages, flag image, and timezones.

TIMEZONE_PATTERN = re.compile(r"^UTC([+-])(\d{2}):(\d{2})$")


class CountryNotFoundError(Exception):
    pass


class CountryAPIError(Exception):
    pass


def get_country_info(country_name):
    """Fetch country data from countries.dev and return it as a plain dict.
    Raises CountryNotFoundError / CountryAPIError instead of printing+returning None,
    so callers (CLI or GUI) can handle failures however they need to."""
    url = f"https://countries.dev/name/{country_name}"

    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        raise CountryAPIError(f"Could not reach countries.dev: {e}")

    if response.status_code == 404:
        raise CountryNotFoundError(f"Country '{country_name}' not found.")
    if response.status_code != 200:
        raise CountryAPIError(f"countries.dev returned status {response.status_code}.")

    try:
        data = response.json()
    except ValueError:
        raise CountryAPIError("countries.dev returned an unreadable response.")

    if not data:
        raise CountryNotFoundError(f"Country '{country_name}' not found.")

    country = data[0]

    name = country.get("name", "N/A")
    capital = country.get("capital", "N/A")
    region = country.get("region", "N/A")
    population = f"{country.get('population', 0):,}"

    code = (country.get("alpha2Code") or country.get("alpha3Code") or "").lower()
    flags = country.get("flags") or {}
    flag_png = flags.get("png") or (f"https://flagcdn.com/w320/{code}.png" if code else "N/A")

    timezones_list = country.get("timezones", [])
    timezones = ", ".join(timezones_list) if timezones_list else "N/A"

    languages_list = country.get("languages", [])
    languages = ", ".join(lang["name"] for lang in languages_list) if isinstance(languages_list, list) and languages_list else "N/A"

    currencies_list = country.get("currencies", [])
    currencies = ", ".join(
        f"{curr['name']} ({curr.get('symbol', '')})" for curr in currencies_list
    ) if isinstance(currencies_list, list) and currencies_list else "N/A"

    return {
        "Name": name,
        "Capital": capital,
        "Region": region,
        "Population": population,
        "Currencies": currencies,
        "Languages": languages,
        "Flag Image URL": flag_png,
        "Timezones": timezones,
    }


def info(country_name=None):
    """Returns the info dict for the given country (or the currently stored
    trip.name if no argument is given). This used to only print the data --
    now it actually returns it, which is what google_api.py and Storage.py need."""
    name = country_name or trip.name
    return get_country_info(name)


def parse_utc_offset(tz_string):
    """Parses a 'UTC+HH:MM' / 'UTC-HH:MM' string (validated via regex) into a
    signed float number of hours. Returns None if the format doesn't match."""
    match = TIMEZONE_PATTERN.match((tz_string or "").strip())
    if not match:
        return None
    sign, hours, minutes = match.groups()
    offset = int(hours) + int(minutes) / 60
    return offset if sign == "+" else -offset


def timezone_difference(timezones_a, timezones_b):
    """Given two comma-separated timezone strings (as returned in the info dict),
    returns a list of (tz_a, tz_b, hour_difference) tuples for every valid pairing."""
    zones_a = [t.strip() for t in timezones_a.split(",") if t.strip()]
    zones_b = [t.strip() for t in timezones_b.split(",") if t.strip()]

    diffs = []
    for tz_a in zones_a:
        offset_a = parse_utc_offset(tz_a)
        if offset_a is None:
            continue
        for tz_b in zones_b:
            offset_b = parse_utc_offset(tz_b)
            if offset_b is None:
                continue
            diffs.append((tz_a, tz_b, round(offset_b - offset_a, 2)))
    return diffs
