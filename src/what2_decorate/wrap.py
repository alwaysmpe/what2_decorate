"""
Similar to `functools.wraps`, but utilities to take attributes from multiple different functions.
"""
from collections.abc import Callable
from functools import partial, update_wrapper
from typing import Any

WRAPPER_ASSIGNMENTS = (
    "__module__",
    "__name__",
    "__qualname__",
    "__doc__",
    "__type_params__",
)
WRAPPER_UPDATES = (
    "__dict__",
)

SIGNATURE_ASSIGNMENTS = (
    "__annotations__",
)


def __wrap_signature[W: Callable[..., Any]](wrapped: Callable[..., Any], wrapper: W) -> W:
    update_wrapper(wrapper, wrapped, assigned=SIGNATURE_ASSIGNMENTS, updated=())
    return wrapper


def signature[W: Callable[..., Any]](wrapped: Callable[..., Any]) -> Callable[[W], W]:
    """
    A decorator to copy the passed in callable signature to the decorated function.

    :param wrapped: The function to take the signature from.
    :returns:       A decorator that will apply the signature from the passed wrapped function.
    """
    return partial(__wrap_signature, wrapped)


def __wrap_definition[W: Callable[..., Any]](wrapped: Callable[..., Any], wrapper: W) -> W:
    # don't use update_wrapper, don't want to set __wrapped__ as inspect.signature will give wrong result.
    for attr in WRAPPER_ASSIGNMENTS:
        setattr(wrapper, attr, getattr(wrapped, attr))
    for attr in WRAPPER_UPDATES:
        getattr(wrapper, attr).update(getattr(wrapped, attr))
    return wrapper


def definition[W: Callable[..., Any]](wrapper: Callable[..., Any]) -> Callable[[W], W]:
    """
    A decorator to copy attributes from a wrapper funnction that specify its definition name and loaction.
    """
    return partial(__wrap_definition, wrapper)
