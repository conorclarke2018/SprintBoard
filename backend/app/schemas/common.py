"""Reusable validators shared by several schemas."""

from pydantic import BeforeValidator


def empty_to_none(value: object) -> object:
    """Treat blank optional text (e.g. an empty description box) as 'not provided'."""
    if isinstance(value, str) and not value.strip():
        return None
    return value


BlankToNone = BeforeValidator(empty_to_none)
