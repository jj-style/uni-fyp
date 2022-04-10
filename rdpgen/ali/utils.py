import functools
import regex
from .types import Expression


def imports(*packages):
    def import_wrapper(func):
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            for pkg in packages:
                self.import_package(pkg)
            return func(self, *args, **kwargs)

        return wrap

    return import_wrapper


def expression(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        def lazy():
            return func(*args, **kwargs)

        return Expression(lazy)

    return wrap


def convert_case(index, *indices):
    """Converts arguments at each index given to the language's case.
    Indices start from 0 and exclude 'self' on a class method
    Arguments:
        index - index of argument to check for being non-negative (required)
        indices - indices of arguments to check for being non-negative (optional)
    """

    def converter(f):
        @functools.wraps(f)
        def wrap(self, *args, **kwargs):
            args = list(args)
            if "no_cc" not in kwargs:
                # HACK: for Go language, where a few assigns have
                # assigned multiple variables at once like res,err =
                match = regex.match(
                    r"(?P<var1>.*)\s*,\s*(?P<var2>.*)", str(args[index])
                )
                if match:
                    groups = match.groupdict()
                    v1 = self.convert_case(groups["var1"])
                    v2 = (
                        self.convert_case(groups["var2"])
                        if groups["var2"] != "_"
                        else "_"
                    )
                    args[index] = f"{v1}, {v2}"
                elif isinstance(args[index], str):
                    arg = args[index]
                    # HACK: for Go language if assigned _ so user can fill
                    # in errors later
                    if arg != "_":
                        args[index] = ".".join(
                            [self.convert_case(part) for part in arg.split(".")]
                        )
                for idx in indices:
                    if isinstance(args[idx], str):
                        arg = args[idx]
                        if arg != "_":
                            args[idx] = ".".join(
                                [self.convert_case(part) for part in arg.split(".")]
                            )
            return f(self, *args, **kwargs)

        return wrap

    return converter
