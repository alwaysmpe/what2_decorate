"""
Functions to simplify creating decorators.
"""

from collections.abc import Callable, Generator
from functools import wraps
from inspect import iscoroutinefunction, isgeneratorfunction, markcoroutinefunction
from typing import Any, Concatenate, NoReturn, TypeIs, cast, overload
from warnings import deprecated

from what2_decorate import wrap

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

type DecRet[**Pc, R] = Callable[[Callable[Pc, R]], Callable[Pc, R]]

type DecoratedFn[**Pw, R] = Callable[Pw, R]
type DecoratedGen[**Pw, I, S, T] = Callable[Pw, Generator[I, S, T]]

type DecoratedFnDec[**Pw, R] = Callable[Concatenate[DecoratedFn[Pw, R], Pw], R]
type DecoratedGenDec[**Pw, I, S, T] = Callable[Concatenate[DecoratedGen[Pw, I, S, T], Pw], Generator[I, S, T]]

type DecoratedFnRet[**Pw, R] = DecRet[Pw, R]
type DecoratedGenRet[**Pw, I, S, T] = DecRet[Pw, Generator[I, S, T]]


@overload
def dek[**Pw, R](deco: Callable[Concatenate[Callable[Pw, R], Pw], R]) -> DecRet[Pw, R]:
    ...


@overload
def dek[**Pw, I, S, T](deco: Callable[Concatenate[Callable[Pw, Generator[I, S, T]], Pw], Generator[I, S, T]]) -> DecRet[Pw, Generator[I, S, T]]:
    ...


def __is_generator_deco[**Pw, R, I, S, T](
        deco: DecoratedFnDec[Pw, R] | DecoratedGenDec[Pw, I, S, T],
        ref: DecoratedFn[Pw, R] | DecoratedGen[Pw, I, S, T],
) -> TypeIs[DecoratedGenDec[Pw, I, S, T]]:
    return deco and __is_generator(ref)


def __is_fn_deco[**Pw, R, I, S, T](
        deco: DecoratedFnDec[Pw, R] | DecoratedGenDec[Pw, I, S, T],
        ref: DecoratedFn[Pw, R] | DecoratedGen[Pw, I, S, T],
) -> TypeIs[DecoratedFnDec[Pw, R]]:
    return deco and __is_fn(ref)


def __is_generator[**Pw, R, I, S, T](deco: DecoratedFn[Pw, R] | DecoratedGen[Pw, I, S, T]) -> TypeIs[DecoratedGen[Pw, I, S, T]]:
    return isgeneratorfunction(deco)


def __is_fn[**Pw, R, I, S, T](deco: DecoratedFn[Pw, R] | DecoratedGen[Pw, I, S, T]) -> TypeIs[DecoratedFn[Pw, R]]:
    return not isgeneratorfunction(deco)


def dek[**Pw, R, I, S, T](
        deco: DecoratedFnDec[Pw, R] | DecoratedGenDec[Pw, I, S, T],
) -> (DecoratedFnRet[Pw, R] | DecoratedGenRet[Pw, I, S, T]):
    """
    Transform a function that takes a function and its parameters into a functoin decorator.

    :param deco:    The function to transform into a decorator.
    :returns:       The function wrapped as a decorator.

    Example
    -------

    >>> from what2_decorate.decdec import dek
    >>> from collections.abc import Callable
    >>> @dek
    ... def decorator[**P, R](fn: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
    ...     print(f"{fn.__name__} called")
    ...     return fn(*args, **kwargs)
    ...
    >>> @decorator
    ... def my_function(arg1: int) -> int:
    ...     return arg1
    ...
    >>> my_function(1)
    my_function called
    1
    """

    @overload
    def wrapper(wrapped: DecoratedFn[Pw, R]) -> DecoratedFn[Pw, R]:
        ...

    @overload
    def wrapper(wrapped: DecoratedGen[Pw, I, S, T]) -> DecoratedGen[Pw, I, S, T]:
        ...

    @wrap.definition(deco)
    def wrapper(wrapped: DecoratedFn[Pw, R] | DecoratedGen[Pw, I, S, T]) -> DecoratedFn[Pw, R] | DecoratedGen[Pw, I, S, T]:

        if __is_generator(wrapped) and __is_generator_deco(deco, wrapped):
            wrapped_fn = wrapped
            wrapped_deco = deco

            @wraps(wrapped_fn)
            def decorated_gen(*args: Pw.args, **kwargs: Pw.kwargs) -> Generator[I, S, T]:
                yield from wrapped_deco(wrapped_fn, *args, **kwargs)
                raise StopIteration

            if iscoroutinefunction(wrapped):
                return markcoroutinefunction(decorated_gen)
            return decorated_gen
        if __is_fn(wrapped) and __is_fn_deco(deco, wrapped):
            wrapped_fn = wrapped
            wrapped_deco = deco

            @wraps(wrapped)
            def decorated_fn(*args: Pw.args, **kwargs: Pw.kwargs) -> R:
                return wrapped_deco(wrapped_fn, *args, **kwargs)
            if iscoroutinefunction(wrapped):
                return markcoroutinefunction(decorated_fn)
            return decorated_fn
        raise ValueError
    return wrapper


type NoParamFn[R] = Callable[[], Callable[[Callable[[], R]], R]]
type NoParamRet[R] = Callable[[], Callable[[Callable[[], R]], Callable[[], R]]]


@overload
def dek_dek[**Pc, R](
        fn: Callable[[], Callable[Concatenate[Callable[Pc, R], Pc], R]],
) -> Callable[[Callable[Pc, R]], Callable[Pc, R]]:
    ...


@overload
def dek_dek[R](
        fn: Callable[[], Callable[[Callable[[], R]], R]],
) -> Callable[[], Callable[[Callable[[], R]], Callable[[], R]]]:
    ...


@overload
@deprecated("invalid usage - an argument-decorator should not take a callable as its only parameter.")
def dek_dek[**Pc, R](
    fn: Callable[[Callable[..., Any]], Callable[Concatenate[Callable[Pc, R], Pc], R]],
) -> NoReturn:
    ...


@overload
def dek_dek[**Pw, **Pc, R](
        fn: Callable[Pw, Callable[Concatenate[Callable[Pc, R], Pc], R]],
) -> Callable[Pw, Callable[[Callable[Pc, R]], Callable[Pc, R]]]:
    ...


type SimpleDecFn[**Pc, R] = Callable[[], Callable[Concatenate[Callable[Pc, R], Pc], R]]
type SimpleDecRet[**Pc, R] = Callable[[Callable[Pc, R]], Callable[Pc, R]]
type InvalidDec[**Pc, R] = Callable[[Callable[..., Any]], Callable[Concatenate[Callable[Pc, R], Pc], R]]
type ComplexDecFn[**Pw, **Pc, R] = Callable[Pw, Callable[Concatenate[Callable[Pc, R], Pc], R]]
type ComplexDecRet[**Pw, **Pc, R] = Callable[Pw, Callable[[Callable[Pc, R]], Callable[Pc, R]]]
type DekDekFn[**Pw, **Pc, R] = Callable[Pw, Callable[Concatenate[Callable[Pc, R], Pc], R]]
type DekDekRet[**Pw, **Pc, R] = (
    Callable[Pw, Callable[[Callable[Pc, R]], Callable[Pc, R]]] |
    Callable[[Callable[Pc, R]], Callable[Pc, R]]
)
type DekNoCall[**Pc, R] = Callable[[Callable[..., Any]], Callable[Concatenate[Callable[Pc, R], Pc], R]]

type DedekFnType[**Pw, **Pc, R] = (
    Callable[[], Callable[[Callable[[], R]], R]]
    |
    Callable[[], Callable[Concatenate[Callable[Pc, R], Pc], R]]
    |
    Callable[Pw, Callable[Concatenate[Callable[Pc, R], Pc], R]]
    |
    Callable[[Callable[..., Any]], Callable[Concatenate[Callable[Pc, R], Pc], R]]
)


def dek_dek[**Pw, **Pc, R](
        fn: DedekFnType[Pw, Pc, R],
) -> (
    Callable[[Callable[Pc, R]], Callable[Pc, R]]
    |
    Callable[[], Callable[[Callable[[], R]], Callable[[], R]]]
    |
    Callable[Pw, Callable[[Callable[Pc, R]], Callable[Pc, R]]]
):
    """
    Decorator to simplify creating configurable decorators.

    :param fn:  The function implementing your decorator.
                It should take either required or optional parameters.
                If it takes only optional parameters the returned type
                will allow usage as either an explicitly called decorator
                or as an uncalled decorator to a decorated function,
                and this function will infer correct usage.
    :returns:   A function that can be used either as an explicitly called
                decorator or implicitly called decorator.

    Example
    -------

    >>> from typing import Concatenate
    >>> from collections.abc import Callable
    >>> from what2_decorate.decdec import dek_dek
    >>> @dek_dek
    ... def decorate_optional[**P, R](arg1: int = 1, arg2: str = "1") -> Callable[Concatenate[Callable[P, R], P], R]:
    ...     print(f"decorate_optional called with arg1: {arg1}, arg2: {arg2}")
    ...     def inner(fn: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
    ...         print(f"{fn.__name__} called with *args: {args}, **kwargs: {kwargs}")
    ...         ret = fn(*args, **kwargs)
    ...         print(f"result: {ret}")
    ...         return ret
    ...     return inner
    >>> @decorate_optional
    ... def foo(arg1: int) -> int:
    ...     return arg1 ** 2
    decorate_optional called with arg1: 1, arg2: 1
    >>> print(foo(6))
    foo called with *args: (6,), **kwargs: {}
    result: 36
    36
    """
    @overload
    def wrapper(*args: Pw.args, **kwargs: Pw.kwargs) -> Callable[[Callable[Pc, R]], Callable[Pc, R]] | Callable[[Callable[[], R]], Callable[[], R]]:
        ...

    @overload
    def wrapper(user_dec: Callable[Pc, R], /) -> Callable[Pc, R]:
        ...

    def wrapper(
        *args: Any,
        **kwargs: Any,
    ) -> (
        Callable[Pc, R]
        |
        Callable[[Callable[[], R]], Callable[[], R]]
        |
        Callable[[Callable[Pc, R]], Callable[Pc, R]]
    ):
        def is_empty(fn: DedekFnType[Pw, Pc, R]) -> TypeIs[Callable[[], Callable[[Callable[[], R]], R]]]:
            return fn and (len(args) == 0) and (len(kwargs) == 0)
        if is_empty(fn):
            return dek(fn())

        def is_decorated(fn: DedekFnType[Pw, Pc, R]) -> TypeIs[Callable[[], Callable[Concatenate[Callable[Pc, R], Pc], R]]]:
            return fn and (len(args) == 1) and (len(kwargs) == 0) and callable(args[0])
        if is_decorated(fn):
            typed_fn = cast(Callable[[], Callable[Concatenate[Callable[Pc, R], Pc], R]], fn)
            wrapped_fn = cast(Callable[Pc, R], args[0])
            return dek(typed_fn())(wrapped_fn)

        typed_fn = cast(Callable[Pw, Callable[Concatenate[Callable[Pc, R], Pc], R]], fn)
        return dek(typed_fn(*args, **kwargs))
    return wrapper
