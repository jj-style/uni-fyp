from .types import Expression


def imports(*packages):
    def import_wrapper(func):
        def wrap(self, *args, **kwargs):
            for pkg in packages:
                self.import_package(pkg)
            return func(self, *args, **kwargs)

        return wrap

    return import_wrapper


def expression(func):
    def wrap(*args, **kwargs):
        def lazy():
            return func(*args, **kwargs)

        return Expression(lazy)

    return wrap
