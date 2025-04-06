from src.ast_nodes import *
from src.environment import Environment
from src.errors import IncorrectArgumentNumber, DefineFormatError


class SpecialForm:
    def __init__(self, name, func, min_args, max_args):
        self.name = name
        self.func = func
        self.min_args = min_args
        self.max_args = max_args

    def __call__(self, args, env, evaluator):
        # arity check
        if self.min_args is not None and len(args) < self.min_args:
            raise IncorrectArgumentNumber(self.name)

        if self.max_args is not None and len(args) > self.max_args:
            raise IncorrectArgumentNumber(self.name)

        return self.func(args, env, evaluator)

    def __repr__(self):
        return f"<Special Function: {self.name}>"


def special(name, min_args=None, max_args=None):
    def decorator(func):
        return SpecialForm(
            name=name,
            func=func,
            min_args=min_args,
            max_args=max_args
        )

    return decorator


@special(name="quote", min_args=1, max_args=1)
def special_quote(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    arg = args[0]
    return arg


@special(name="define")
def special_define(args: list[str, ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    # Define has it own rules for the arguments, so I'm not using the decorator for checking argument
    if len(args) != 2:
        raise DefineFormatError()

    symbol = args[0]

    if not isinstance(symbol, AtomNode) or symbol.type != "SYMBOL":
        raise DefineFormatError()

    symbol_name = symbol.value
    value = args[1]

    env.define(symbol_name, evaluator.evaluate(value))

    return AtomNode("SYMBOL", symbol)


@special(name="and", min_args=2)
def special_and(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    eval_result = None
    for arg in args:
        eval_result = evaluator.evaluate(arg)
        if eval_result == AtomNode("BOOLEAN", "nil"):
            return AtomNode("BOOLEAN", "nil")

    return eval_result


@special(name="or", min_args=2)
def special_or(args: list[ASTNode], env: Environment) -> ASTNode:
    pass


__all__ = [
    "SpecialForm",
    "special_quote",
    "special_define",
    "special_and",
    "special_or"
]
