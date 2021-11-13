from gli.gli.language import Language, Type, imports, Expression
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
        arguments: Union[Dict[str, Type], List[Type]],
        *statements,
    ) -> Expression:
        if isinstance(arguments, list):
            # not got named arguments to use so use arg1,..,argn
            arguments = {
                f"arg{idx+1}": self.types(t) for t, idx in enumerate(arguments)
            }
        arg_list = ",".join([f"{name} {t}" for name, t in arguments.items()])
        ret_part = "" if return_type is None else " " + self.types(return_type)
        # TODO - block part of function and statements in it properly
        return Expression(
            f"func {id}({arg_list}){ret_part} {{\n\t{str(e) for e in statements}}}"
        )

    def do_return(self, expression: Optional[Expression]):
        if expression is None:
            return Expression("return")
        else:
            return Expression(f"return {expression}")

    @imports("fmt")
    def println(self, *args) -> str:
        return f"""fmt.Println({", ".join([str(a) for a in args])})"""
