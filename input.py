import re


COUNTRY_NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ\s\-'.,()]+$")


class InvalidCountryNameError(ValueError):
    pass


def validate_country_name(name):
    """Raises InvalidCountryNameError if the name fails basic regex validation."""
    name = (name or "").strip()
    if not name:
        raise InvalidCountryNameError("Country name cannot be empty.")
    if not COUNTRY_NAME_PATTERN.match(name):
        raise InvalidCountryNameError(
            f"'{name}' contains invalid characters. Use letters, spaces, and basic punctuation only."
        )
    return name


class Country:
    """Represents a single country the user wants to look up."""

    def __init__(self, name=""):
        self.name = name

    def set_name(self, name):
        self.name = validate_country_name(name)
        return self.name


class CountryComparator:
    """Holds the two countries the user wants to compare."""

    def __init__(self, country_a="", country_b=""):
        self.country_a = country_a
        self.country_b = country_b

    def set_countries(self, country_a, country_b):
        self.country_a = validate_country_name(country_a)
        self.country_b = validate_country_name(country_b)
        return self.country_a, self.country_b


trip = Country()
comparison = CountryComparator()
