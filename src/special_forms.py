from src.ast_nodes import *
from src.environment import Environment
from src.errors import IncorrectArgumentNumber, DefineFormatError, CondFormatError
from src.base.callable import CallableEntity


class SpecialForm(CallableEntity):
    def __init__(self, name, func, min_args, max_args):
        super().__init__(name, func, min_args, max_args)

    def __call__(self, args, env, evaluator):
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

    env.define(symbol_name, evaluator.evaluate(value, env, "inner"))

    return AtomNode("SYMBOL", symbol)


@special(name="and", min_args=2)
def special_and(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    eval_result = None
    for arg in args:
        eval_result = evaluator.evaluate(arg, env, "inner")
        if eval_result == AtomNode("BOOLEAN", "nil"):
            return AtomNode("BOOLEAN", "nil")

    return eval_result


@special(name="or", min_args=2)
def special_or(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    for arg in args:
        eval_result = evaluator.evaluate(arg, env, "inner")
        if eval_result != AtomNode("BOOLEAN", "nil"):
            return eval_result

    return AtomNode("BOOLEAN", "nil")


@special(name="begin", min_args=1)
def special_begin(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    for expr in args[:-1]:
        evaluator.evaluate(expr, env, "inner")

    return evaluator.evaluate(args[-1], env, "inner")


@special(name="if", min_args=2, max_args=3)
def special_if(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    test_expr, then_expr, *rest = args
    else_expr = rest[0] if rest else None

    if evaluator.evaluate(test_expr, env, "inner") != AtomNode("BOOLEAN", "nil"):
        return evaluator.evaluate(then_expr, env, "inner")

    else:
        return evaluator.evaluate(else_expr, env, "inner")


@special(name="cond", min_args=1)
def special_cond(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode | None:
    def extract_branch(cons: ASTNode) -> tuple[ASTNode, ASTNode]:
        branch = []
        while isinstance(cons, ConsNode):
            branch.append(cons.car)
            cons = cons.cdr
        if cons != AtomNode("BOOLEAN", "nil") or len(branch) != 2:
            raise CondFormatError()
        return branch[0], branch[1]

    for clause in args[:-1]:
        if not isinstance(clause, ConsNode):
            raise CondFormatError()

        test, expr = extract_branch(clause)

        if evaluator.evaluate(test) != AtomNode("BOOLEAN", "nil"):
            return evaluator.evaluate(expr, env, "inner")

    test, expr = extract_branch(args[-1])
    if (test == AtomNode("SYMBOL", "else") or
            evaluator.evaluate(test) != AtomNode("BOOLEAN", "nil")):
        return evaluator.evaluate(expr, env, "inner")


__all__ = [
    "SpecialForm",
    "special_quote",
    "special_define",
    "special_and",
    "special_or",
    "special_begin",
    "special_if",
    "special_cond"
]
