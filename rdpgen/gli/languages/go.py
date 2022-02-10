from ..language import Language, Context
from ..types import Type, Primitive, Composite, Expression
from ..utils import imports, expression
from ..errors import MissingTypeError
from .utils import format_function_arguments
from typing import Dict, Union, Optional, List, Any
import shlex
import regex


class Go(Language):
    def __init__(self, ctx: Context = None):
        super().__init__(ctx)
        self.__var_dec_count = {}

    @property
    def name(self) -> str:
        return "golang"

    def varn(self, var: str) -> str:
        if var not in self.__var_dec_count:
            self.__var_dec_count[var] = 0
            return var

        self.__var_dec_count[var] += 1
        return f"{var}{self.__var_dec_count}"

    def prelude(self, **kwargs):
        package = kwargs.get("package", "main")
        imports = ""
        if len(self.imports) > 0:
            pkgs = "\n".join(
                self.whitespace_char + self.string(pkg) for pkg in sorted(self.imports)
            )
            imports = f"import (\n{pkgs}\n)\n\n"
        return f"package {package}\n\n{imports}"

    def types(self, t: Type) -> str:
        if isinstance(t, Primitive):
            if t is Primitive.Int:
                return "int"
            elif t is Primitive.Float:
                return "float64"
            elif t is Primitive.String:
                return "string"
        elif isinstance(t, Composite):
            if t.base is Composite.CType.Array:
                return f"[]{self.types(t.sub)}"
        else:
            # allow special types in certain functions
            # e.g. command() needs type Cmd
            return str(t)

    def string(self, s: str, double: bool = True):
        return f'"{s}"' if double else f"`{s}`"

    @imports("strings")
    def string_split(self, s: str, delim: str):
        return self.call("strings.Split", s, delim)

    def array(self, t: Type, elements: List[Any]):
        joined = ", ".join(str(e) for e in elements)
        return f"[]{self.types(t)}{{{joined}}}"

    def array_length(self, expression):
        return f"len({expression})"

    def array_append(self, id: str, item):
        return self.assign(id, self.call("append", id, str(item)))

    def array_remove(self, id: str, idx: int):
        return self.assign(
            id,
            self.call(
                "append",
                self.index(id, f":{idx}"),
                f"{self.index(id, str(idx+1) + ':')}...",
            ),
        )

    def array_iterate(
        self,
        id: str,
        it: str,
        *statements,
        declare_it: bool = True,
        iterate_items: bool = False,
        type: Type = None,
    ):
        return self.array_enumerate(
            id,
            "_" if iterate_items else it,
            it if iterate_items else "_",
            *statements,
            declare_it=(not iterate_items) and declare_it,
            declare_item=declare_it and iterate_items,
            type=type,
        )

    @expression
    def array_enumerate(
        self,
        id: str,
        it: str,
        item: str,
        *statements,
        declare_it: bool = True,
        declare_item: bool = False,
        type: Type = None,
    ):
        stmts = []
        if declare_it:
            stmts.append(self.declare(it, Primitive.Int))
        if declare_item:
            if type is None:
                raise MissingTypeError()
            stmts.append(self.declare(item, type))
        stmts.append(
            self.indent(f"for {it}, {item} = range {id} {self.block(*statements)}")
        )
        return self.linesep.join(stmts)

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
        args = format_function_arguments(arguments)
        arg_list = ", ".join([f"{name} {self.types(t)}" for name, t in args.items()])
        ret_part = "" if return_type is None else " " + self.types(return_type)

        stmts = self.block(*statements)
        func = f"func {id}({arg_list}){ret_part} {stmts}"
        return func

    def block(self, *statements):
        block = f"{{{self.linesep}"
        self.ctx.indent_lvl += 1
        for stmt in statements:
            block += self.indent(str(stmt)) + self.linesep
        self.ctx.indent_lvl -= 1
        block += self.indent("}") if self.ctx.indent_lvl > 0 else "}"
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

    @expression
    def for_loop(
        self,
        it: str,
        start,
        stop,
        step,
        *statements,
    ):
        return f"for {self.assign(it, start)}; {stop}; {step} {self.block(*statements)}"

    @expression
    def while_loop(self, *statements, condition=None):
        stmts = list(statements)
        if condition is not None:
            stmts.insert(0, self.if_else(self.negate(condition), [self.break_loop()]))
        loop = f"for {self.block(*stmts)}"
        return loop

    @expression
    def if_else(
        self,
        condition,
        true_stmts,
        false_stmts=None,
    ):
        return f"if {condition} {self.block(*true_stmts)}{(' else ' + self.block(*false_stmts)) if false_stmts else ''}"  # noqa

    @imports("os/exec")
    @expression
    def command(
        self, command: str, suppress_output: bool = True, exit_on_failure: bool = True
    ):
        stmts = []
        m = regex.match(r"""\"(?P<inner>.*)\"""", command)
        if m:
            groups = m.groupdict()
            args = [self.string(a) for a in shlex.split(groups["inner"])]
        else:
            args = [command]
        if suppress_output:
            cmd_var = self.varn("cmd")
            stmts.append(self.declare(cmd_var, "*exec.Cmd"))
            if exit_on_failure:
                err_var = self.varn("err")
                stmts.append(self.declare(err_var, "error"))
            stmts.append(
                self.assign(
                    "cmd",
                    self.call("exec.Command", *args),
                )
            )
            to_assign = "err" if exit_on_failure else "_"
            stmts.append(self.assign(to_assign, self.call("cmd.Run")))
            if exit_on_failure:
                stmts.append(self.if_else(self.neq("err", "nil"), [self.exit(1)]))

        else:
            stmts.append(self.declare("out", Composite.array("byte")))
            if exit_on_failure:
                stmts.append(self.declare("err", "error"))
            to_assign = "err" if exit_on_failure else "_"
            stmts.append(
                self.assign(
                    f"out, {to_assign}",
                    self.call("exec.Command", *args) + f".{self.call('Output')}",
                )
            )
            if exit_on_failure:
                stmts.append(self.if_else(self.neq("err", "nil"), [self.exit(1)]))
            stmts.append(self.println("string(out)"))

        return self.linesep.join([stmts[0]] + [self.indent(s) for s in stmts[1:]])

    @imports("os")
    def exit(self, code: int = 0):
        return self.call("os.Exit", code)

    @imports("bufio", "os")
    def read_lines(self, file: str):
        func_name = "readLines"

        def lib():
            s1 = self.declare("f", "*os.File")
            s2 = self.declare("err", "error")
            s3 = self.assign("f, err", self.call("os.Open", "file"))
            s4 = self.if_else(self.neq("err", "nil"), [self.exit(1)])
            s5 = self.declare("scanner", "*bufio.Scanner")
            s6 = self.assign("scanner", self.call("bufio.NewScanner", "f"))
            s7 = self.call("scanner.Split", "bufio.ScanLines")
            s8 = self.declare("lines", Composite.array(Primitive.String))
            s9 = Expression(
                lambda: f"for {self.call('scanner.Scan')} {self.block(self.assign('lines', self.call('append', 'lines', self.call('scanner.Text'))))}"  # noqa
            )
            s10 = self.call("f.Close")
            s11 = self.do_return(expression="lines")
            stmts = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11]
            return self.function(
                func_name,
                Composite.array(Primitive.String),
                {"file": Primitive.String},
                *stmts,
            )

        self.register_helper(func_name, lib())
        return self.call(func_name, file)

    @imports("io/ioutil")
    def read_file(self, file: str):
        func_name = "readFile"

        def lib():
            s1 = self.declare("content", Composite.array("byte"))
            s2 = self.declare("err", "error")
            s3 = self.assign("content, err", self.call("ioutil.ReadFile", "file"))
            s4 = self.if_else(
                self.neq("err", "nil"), [self.println("err"), self.exit(1)]
            )
            s5 = self.do_return(expression=self.call("string", "content"))
            stmts = [s1, s2, s3, s4, s5]
            return self.function(
                func_name,
                Primitive.String,
                {"file": Primitive.String},
                *stmts,
            )

        self.register_helper(func_name, lib())
        return self.call(func_name, file)
