# What2 Decorate

Decorators to help create decorators and a decorator
to convert an `__init__` to behave like a `__post_init__`.

## N

## Writing Decorators

Without this, writing a simple decorator:
```python
from collections.abc import Callable
from functools import wraps

def decorate[**P, R](fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"{fn.__name__} called")
        return fn(*args, **kwargs)
    return inner
```

With this:
```python
from what2_decorate import dek
from collections.abc import Callable

@dek
def decorate[**P, R](fn: Callable[P, R], *args: P.args, **kwargs) -> R:
    print(f"{fn.__name__} called")
    return fn(*args, **kwargs)
```
Which is nice, but not a huge saving. Lets look at a slightly more complicated example.

Without this, writing a decorator that takes optional arguments:
```python
from collections.abc import Callable
from typing import overload

@overload
def decorate[P, R](fn: Callable[P, R], /) -> Callable[P, R]:
    ...
@overload
def decorate[P, R](arg1: int = 1, arg2: str = "") -> Callable[[Callable[P, R]], Callable[P, R]]:
    ...

def decorate[P, R](arg1: int | Callable[P, R] = 1, arg2: str = "") -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    if isintance(arg1, int):
        def wrapper(fn: Callable[P, R]) -> Callable[P, R]:
            def inner(*args: P.args, **kwargs: P.kwargs) -> R:
                print(f"{fn.__name__} called")
                return fn(*args, **kwargs)
            return inner
        return wrapper

    fn: Callable[P, R] = arg1
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"{fn.__name__} called")
        return fn(*args, **kwargs)
    return inner
```
With this:
```python
from what2_decorate import dek_dek
from collections.abc import Callable
from typing import Concatenate

@dek_dek
def decorate[**P, R](arg1: int = 1, arg2: str = "1") -> Callable[Concatenate[Callable[P, R], P], R]:
    def inner(fn: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        print(f"{fn.__name__} called with *args: {args}, **kwargs: {kwargs}")
        return fn(*args, **kwargs)
    return inner
```
Which is quite a bit nicer and about quarter the length.

## Writing post-init

Suppose you want to inherit from a base class without modifying its signature:
```python
class Base:
    base_attr1: int
    base_attr2: str

    def __init__(self, arg1: int, arg2: str):
        self.base_attr1 = arg1
        self.base_attr2 = arg2

class Child(Base):
    child_attr1: str

    def __init__(self, arg1: int, arg2: str):
        super().__init__(arg1, arg2)
        self.child_attr1 = "child"
```
Firstly, using `dataclasses.dataclass` to
auto-generate the init for you is preferable, but
this only works if every class is a dataclass.

Writing an init function with 2 arguments isn't too
bad, but for large inits that may change in future,
this isn't ideal.

Using this:
```python
from typing import Self
from what2_decorate.init import Decorate
    
class Base:
    base_attr1: int
    base_attr2: str

    def __init__(self, arg1: int, arg2: str):
        self.base_attr1 = arg1
        self.base_attr2 = arg2

class Child(Base):
    child_attr1: str
    
    @Decorate[Self].init_of(Base)
    def __init__(self):
        self.child_attr1 = "child"
```
Which might be preferable.