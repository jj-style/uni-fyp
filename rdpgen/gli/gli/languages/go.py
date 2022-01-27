from ..language import Language, Type, imports, expression
from typing import Dict, Union, Optional, List


class Go(Language):
    @property
    def name(self) -> str:
        return "golang"

    def types(self, t: Type) -> str:
        if t is Type.Int:
            return "int"
        elif t is Type.Float:
            return "float64"
        elif t is Type.String:
            return "string"

    def string(self, s: str):
        return f'"{s}"'

    def declare(self, id: str, type: Type):
        return f"var {id} {self.types(type)}"

    def assign(self, id: str, expr):
        return f"{id} = {expr}"

    @expression
    def function(
        self,
        id: str,
        return_type: Optional[Type],
        arguments: Union[Dict[str, Type], List[Type], None],
        *statements,
    ):
        args = {} if not arguments else arguments
        if isinstance(arguments, list):
            # not got named arguments to use so use arg1,..,argn
            args = {f"arg{idx+1}": self.types(t) for idx, t in enumerate(arguments)}

        arg_list = ", ".join([f"{name} {t}" for name, t in args.items()])
        ret_part = "" if return_type is None else " " + self.types(return_type)

        # TODO: make Expression class take this function so can make __str__ make string
        # so don't have to do callable()

        stmts = self.block(*statements)
        return f"func {id}({arg_list}){ret_part} {stmts}"

    def block(self, *statements):
        block = f"{{{self.linesep}"
        self.ctx.indent_lvl += 1
        for stmt in statements:
            block += self.indent(stmt if not callable(stmt) else stmt()) + self.linesep
        self.ctx.indent_lvl -= 1
        block += "}"
        return block

    def do_return(self, expression=None):
        if expression is None:
            return "return"
        else:
            return f"return {expression}"

    @imports("fmt")
    def println(self, *args) -> str:
        return f"""fmt.Println({", ".join([str(a) for a in args])})"""

    @imports("fmt")
    def print(self, *args) -> str:
        return f"""fmt.Print({", ".join([str(a) for a in args])})"""
