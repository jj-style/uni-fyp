from ..language import Language, Type, imports
from typing import Dict, Union, Optional, List


class Cpp(Language):
    @property
    def name(self) -> str:
        return "c++"

    def types(self, t: Type) -> str:
        if t is Type.Int:
            return "int"
        elif t is Type.Float:
            return "double"
        elif t is Type.String:
            return "std::string"

    def string(self, s: str):
        return f'"{s}"'

    def declare(self, id: str, type: Type):
        return f"{self.types(type)} {id};"

    def assign(self, id: str, expr):
        return f"{id} = {expr};"

    def function(
        self,
        id: str,
        return_type: Optional[Type],
        arguments: Union[Dict[str, Type], List[Type]],
        *statements,
    ):
        if isinstance(arguments, list):
            # not got named arguments to use so use arg1,..,argn
            arguments = {
                f"arg{idx+1}": self.types(t) for t, idx in enumerate(arguments)
            }
        arg_list = ",".join([f"{name} {t}" for name, t in arguments.items()])
        ret_part = "void" if return_type is None else " " + self.types(return_type)

        # TODO - block part of function and statements in it properly
        stmts = "\n".join(str(e) for e in statements)
        return f"{ret_part} {id}({arg_list}) {{\n\t{stmts}\n}}"

    def do_return(self, expression=None):
        if expression is None:
            return "return;"
        else:
            return f"return {expression};"

    @imports("iostream")
    def println(self, *args) -> str:
        # TODO - change return type to Expression and separate out
        # print logic from prinln so println just calls print with args + newline
        a = " << ".join(list(args).append("std::endl"))
        if len(a) > 0:
            return_s = f"std::cout << {a};"
        else:
            return_s = 'std::cout << "";'
        return return_s
