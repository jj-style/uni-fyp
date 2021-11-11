from gli import Language, Type, imports, Expression


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

    @imports("fmt")
    def println(self, *args) -> str:
        return f"""fmt.Println({", ".join([str(a) for a in args])})"""
