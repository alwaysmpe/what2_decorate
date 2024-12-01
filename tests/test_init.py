from dataclasses import dataclass
from inspect import getmodule, signature
from typing import Self

from what2_decorate.init import Decorate


@dataclass
class Base:
    base_attr1: int
    base_attr2: str

    def __init__(self, arg1: int, arg2: str) -> None:
        print("base init called")
        self.base_attr1 = arg1
        self.base_attr2 = arg2


@dataclass
class Child(Base):
    child_attr: str

    @Decorate[Self].init_of(Base)
    def __init__(self) -> None:
        print("child init called")
        self.child_attr = "attr"


def test_module_origin():

    child = Child(1, "1")
    assert str(child) == "Child(base_attr1=1, base_attr2='1', child_attr='attr')"
    assert str(signature(Child)) == "(arg1: int, arg2: str) -> None"

    child_module = getmodule(Child)
    assert child_module is not None
    init_module = getmodule(Child.__init__)
    assert init_module is not None
    assert init_module == child_module
