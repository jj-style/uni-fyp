from gli.language import Type
from gli.languages import Go

if __name__ == "__main__":
    g = Go()
    for lang in [g]:
        print(lang.name, "represents an integer as", lang.types(Type.Int))
        print(lang.imports)
        print(lang.println("hi"))
        print(lang.imports)
        print(lang.declare("x", Type.Float))
        print(lang.assign("x", lang.string("hi")))
        print(lang.println(lang.string("x = "), "x"))
