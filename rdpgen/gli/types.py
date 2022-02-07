from enum import Enum, auto
from typing import Union


class Primitive(Enum):
    Int = auto()
    Float = auto()
    String = auto()


class Composite:
    class CType(Enum):
        Array = auto()

    def __init__(self, base: CType, sub):
        self.base = base
        self.sub = sub

    def __repr__(self):
        return f"{self.base}<{self.sub}>"

    @classmethod
    def array(cls, t):
        return cls(Composite.CType.Array, t)


Type = Union[Primitive, Composite, str]


class Expression:
    def __init__(self, expr_func):
        self.__f = expr_func

    def __str__(self):
        return self.__f()

    def __eq__(self, o):
        if type(o) is str:
            return str(self) == o
        return False


# TODO: subclass expressions so can error check on certain expression types
