# This file name is option.py

class InputError(Exception):
    pass


# Module-level state the GUI reads/writes instead of prompting via input().
selected_option = None


def set_option(value):
    """GUI-friendly replacement for options_value(): validates and stores the choice."""
    global selected_option
    if value not in ("1", "2"):
        raise InputError("Invalid input, Try '1' or '2'.")
    selected_option = value
    return selected_option


def options_value():
    """Original CLI menu loop. Kept for command-line use; the GUI uses set_option()
    instead so nothing runs automatically on import."""
    print("-" * 8, "Menu", "-" * 8)
    print("1. Research about a Country")
    print("2. Compare Two Countries")

    while True:
        menu = input("Enter Option here: ")

        if menu not in ("1", "2"):
            raise InputError("Invalid input, Try '1' or '2'.")
        return menu


# NOTE: options_value() is intentionally NOT called here anymore.
# Calling it at import time meant a terminal prompt fired the instant
# this module was imported -- which breaks GUI usage entirely.
