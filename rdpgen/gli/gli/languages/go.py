from ..language import Language, Type, imports, Expression
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

    def string(self, s: str) -> Expression:
        return Expression(f'"{s}"')

    def declare(self, id: str, type: Type) -> Expression:
        return Expression(f"var {id} {self.types(type)}")

    def assign(self, id: str, expr: Expression) -> Expression:
        return Expression(f"{id} = {expr}")

    def function(
        self,
        id: str,
        return_type: Optional[Type],
        arguments: Union[Dict[str, Type], List[Type], None],
        *statements,
    ) -> Expression:
        args = {} if not arguments else arguments
        if isinstance(arguments, list):
            # not got named arguments to use so use arg1,..,argn
            args = {f"arg{idx+1}": self.types(t) for idx, t in enumerate(arguments)}

        arg_list = ", ".join([f"{name} {t}" for name, t in args.items()])
        ret_part = "" if return_type is None else " " + self.types(return_type)

        stmts = self.block(*statements)

        return Expression(f"func {id}({arg_list}){ret_part} {stmts}")

    def block(self, *statements) -> Expression:
        block = f"{{{self.linesep}"
        # TODO: make this indentation a contextmanager???
        self.ctx.indent_lvl += 1
        for stmt in statements:
            block += self.indent(stmt) + self.linesep
        self.ctx.indent_lvl -= 1
        block += "}"
        return Expression(block)

    def do_return(self, expression: Optional[Expression]):
        if expression is None:
            return Expression("return")
        else:
            return Expression(f"return {expression}")

    @imports("fmt")
    def println(self, *args) -> str:
        return f"""fmt.Println({", ".join([str(a) for a in args])})"""

    @imports("fmt")
    def print(self, *args) -> str:
        return f"""fmt.Print({", ".join([str(a) for a in args])})"""
