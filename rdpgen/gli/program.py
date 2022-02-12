"""Create a source file with a given language as a dependency"""

from .language import Language
from typing import List


class Program:
    def __init__(self, lang: Language):
        self.lang = lang
        # TODO: get a better way than add statments via prog.lang
        # maybe program inherits language and proxies all methods to the .lang instance
        # and adds it to __statements
        self.__statements: List[str] = []

    def add(self, stmt: str):
        self.__statements.append(stmt)

    def generate(self) -> str:
        """Generate the full source code"""
        # generate language prelude
        program = f"{self.lang.prelude()}"
        # add in the helper functions
        for helper in self.lang.helper_funcs.values():
            program += str(helper) + "\n\n"
        for stmt in self.__statements:
            program += str(stmt) + "\n\n"
        program += str(self.lang.postlude())
        return program

    def write_file(self, filename: str):
        """Write the generated source code to a file"""
        with open(filename, "w") as out:
            out.write(self.generate())

    def __str__(self):
        """Generate the source file when converted to a string"""
        return self.generate()

    @property
    def extension(self) -> str:
        return self.lang.extension
