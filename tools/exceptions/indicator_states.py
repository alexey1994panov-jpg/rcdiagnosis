"""Canonical indicator states used by exception-control objects."""

INDICATOR_OFF = 3
INDICATOR_ON = 6


def indicator_is_on(state: int) -> bool:
    return int(state) == INDICATOR_ON


def indicator_is_off(state: int) -> bool:
    return int(state) == INDICATOR_OFF

