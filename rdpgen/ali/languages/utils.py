from typing import Union, Dict, List
from ..types import Type


def format_function_arguments(
    arguments: Union[Dict[str, Type], List[Type], None]
) -> Dict[str, Type]:
    """format arguments into named:type pairs if arguments supplied without name
    as a List or None supplied at all"""
    args = {} if not arguments else arguments
    if isinstance(arguments, list):
        # not got named arguments to use so use arg1,..,argn
        args = {f"arg{idx+1}": t for idx, t in enumerate(arguments)}
    return args
