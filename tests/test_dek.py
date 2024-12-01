from collections.abc import Callable, Iterator
from inspect import cleandoc, isgeneratorfunction, signature
from typing import Concatenate, assert_type, reveal_type

from what2 import dbg

from what2_decorate.decdec import dek, dek_dek


def test_dek_calls():
    dec_called = False

    @dek
    def decorator[**P, R](fn: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        nonlocal dec_called
        dec_called = True
        return fn(*args, **kwargs)

    @decorator
    def foo(arg1: int | str, arg2: int | str) -> tuple[int | str, str | int]:
        """
        My foo doc
        """
        return arg1, arg2

    dbg(foo)
    dbg(signature(foo))
    dbg(foo.__doc__)
    assert cleandoc(foo.__doc__ or "") == "My foo doc"

    assert foo(1, "1") == (1, "1")
    assert dec_called


def test_dek_defaults():
    @dek
    def decorator[**P, R](fn: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        assert not args
        assert not kwargs
        return fn(*args, **kwargs)

    @decorator
    def foo(arg1: int = 1, arg2: str = "1") -> str:
        return f"{arg1}, {arg2}"
    foo()


def test_dek_dek():
    dec_called = False

    @dek_dek
    def dec_dec[**P, R](arg1: int, arg2: str) -> Callable[Concatenate[Callable[P, R], P], R]:
        print("in dec_dec test")
        dbg(arg1)
        dbg(arg2)
        assert_type(arg1, int)
        assert_type(arg2, str)

        def wrapped(fn: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
            nonlocal dec_called
            dec_called = True
            return fn(*args, **kwargs)
        return wrapped

    @dek
    def decorator[**P, R](fn: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        nonlocal dec_called
        dec_called = True
        return fn(*args, **kwargs)

    dbg(signature(decorator))

    @decorator
    def dek_gen() -> Iterator[int]:
        yield from range(10)

    def gen() -> Iterator[int]:
        yield from range(10)

    @decorator
    def dek_non_gen() -> Iterator[int]:
        return iter(range(10))

    def non_gen() -> Iterator[int]:
        return iter(range(10))

    assert isgeneratorfunction(dek_gen)
    assert isgeneratorfunction(gen)
    assert not isgeneratorfunction(dek_non_gen)
    assert not isgeneratorfunction(non_gen)

    @dec_dec(1, "")
    def foo(param: int) -> None:
        pass

    foo(1)

    assert dec_called


def test_dek_dek_default():
    dec_called = False

    @dek_dek
    def dec_dec[**P, R](arg1: int = 1, arg2: str = "") -> Callable[Concatenate[Callable[P, R], P], R]:
        print("in dec_dec default")
        dbg(arg1)
        dbg(arg2)
        assert_type(arg1, int)
        assert_type(arg2, str)
        assert isinstance(arg1, int)
        assert isinstance(arg2, str)

        def wrapped(fn: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
            nonlocal dec_called
            dec_called = True
            return fn(*args, **kwargs)
        return wrapped

    @dec_dec
    def foo(param: int) -> None:
        pass

    foo(1)
    reveal_type(foo)
    reveal_type(dec_dec)

    assert dec_called
