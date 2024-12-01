"""
Utility to wrap an `__init__`function to behave like a `__post_init__`, using the signature of the base class.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Concatenate, cast

from what2_decorate import wrap


@dataclass
class _Ret[T, R, S]:
    t: T

    def __call__[C, **P](self: _Ret[type[C], Callable[P, C], S], fn: Callable[[S], None]) -> Callable[Concatenate[S, P], None]:
        __self = self
        __parent_type: type[S] | None = None

        def get_parent(self: S) -> type[S]:
            nonlocal __parent_type
            if __parent_type is None:
                mro = type(self).mro()
                t = __self.t
                if t not in mro or t == mro[0]:
                    raise ValueError
                self_t: type[S] | None = None
                for tpe in mro:
                    if cast(Any, tpe.__init__) is init_fn:
                        self_t = tpe
                if self_t is None:
                    raise ValueError

                self_t_bases = self_t.__bases__
                if (len(self_t_bases) == 0) or t is not self_t_bases[0]:
                    raise ValueError
                __parent_type = cast(type[S], self_t)
            return __parent_type

        @wrap.definition(fn)
        @wrap.signature(self.t.__init__)
        def init_fn(self: S, *args: P.args, **kwargs: P.kwargs) -> None:
            self_t = get_parent(self)
            super(self_t, self).__init__(*args, **kwargs)
            fn(self)

        return init_fn


class Decorate[SelfT]:
    """
    Wrap an `__init__`function to behave like a `__post_init__`, using the signature of the base class.

    >>> from typing import Self
    >>> from dataclasses import dataclass
    >>> from inspect import signature, getmodule
    >>> from what2_decorate.init import Decorate
    >>> class Base:
    ...     base_attr1: int
    ...     base_attr2: str
    ...     def __init__(self, arg1: int, arg2: str) -> None:
    ...         print("base init called")
    ...         self.base_attr1 = arg1
    ...         self.base_attr2 = arg2
    >>> class Child(Base):
    ...     child_attr: str
    ...     @Decorate[Self].init_of(Base)
    ...     def __init__(self) -> None:
    ...         print("child init called")
    ...         self.child_attr = "attr"
    ...
    >>> child = Child(1, "1")
    base init called
    child init called
    >>> print(child.__dict__)
    {'base_attr1': 1, 'base_attr2': '1', 'child_attr': 'attr'}
    >>> print(signature(Child))
    (arg1: 'int', arg2: 'str') -> 'None'
    """

    @classmethod
    def init_of[V](cls, base_type: V) -> _Ret[V, V, SelfT]:
        """
        Pass the base type to inherit an init signature from.

        :param base_type:   The parent type to inherit an init signature from.
                            Should be the first parent of the class.
        :returns:           A decorator to convert an `__init__` function to a
                            post-init like function.
                            The function will call super().__init__(*args, **kwargs)
                            as appropriate, so not needed to be called in your init.
        """
        return _Ret(base_type)
