from rdpgen.gli.languages.utils import format_function_arguments
from rdpgen.gli import Type, Primitive, Composite


def test_format_function_arguments():
    args = [Primitive.Int, Primitive.String]
    result = format_function_arguments(args)
    assert result == {"arg1": Primitive.Int, "arg2": Primitive.String}

    named_args = {"name": Primitive.String, "scores": Composite.array(Primitive.Int)}
    result = format_function_arguments(named_args)
    assert result == named_args

    assert format_function_arguments(arguments=None) == {}
