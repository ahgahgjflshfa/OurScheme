from src.ast_nodes import *
from src.environment import Environment
from src.errors import DefineFormatError, CondFormatError, LambdaFormatError
from src.function_object import SpecialForm, UserDefinedFunction


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
    if len(args) < 2:
        raise DefineFormatError()

    if isinstance(args[0], AtomNode):
        symbol = args[0]

        if symbol.type != "SYMBOL":
            raise DefineFormatError()

        symbol_name = symbol.value
        value = args[1]

        env.define(symbol_name, evaluator.evaluate(value, env, "inner"))

        if evaluator.verbose:
            print(f"{symbol_name} defined")

    else:   # syntactic sugar for lambda, e.g. (define (f x y) (+ x y)) === (define f (lambda (x y) (+ x y)))
        # Function name and parameters
        func_sig = args[0]
        curr = func_sig
        signatures = []
        while isinstance(curr, ConsNode):
            if not isinstance(curr.car, AtomNode) or curr.car.type != "SYMBOL":
                raise DefineFormatError()

            signatures.append(curr.car.value)
            curr = curr.cdr

        if curr != AtomNode("BOOLEAN", "nil"):
            raise DefineFormatError()

        func_name = signatures[0]
        params = signatures[1:]

        # Body list
        body = args[1:]

        env.define(func_name, UserDefinedFunction(params, body, env))

        if evaluator.verbose:
            print(f"{func_name} defined")

    return AtomNode("VOID", "")


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


@special(name="cond")
def special_cond(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode | None:
    def extract_clause(cons: ASTNode) -> tuple[ASTNode, list[ASTNode]]:
        branch = []
        while isinstance(cons, ConsNode):
            branch.append(cons.car)
            cons = cons.cdr

        if cons != AtomNode("BOOLEAN", "nil"):
            raise CondFormatError()

        if len(branch) < 2:
            raise CondFormatError()

        return branch[0], branch[1:]

    if len(args) < 1:
        raise CondFormatError()

    clauses = []
    for arg in args:
        if not isinstance(arg, ConsNode):
            raise CondFormatError()

        clauses.append(extract_clause(arg))

    for test, exprs in clauses[:-1]:
        if evaluator.evaluate(test) != AtomNode("BOOLEAN", "nil"):
            for expr in exprs[:-1]:
                evaluator.evaluate(expr, env, "inner")

            return evaluator.evaluate(exprs[-1], env, "inner")

    test, exprs = clauses[-1]
    if (test == AtomNode("SYMBOL", "else") or
            evaluator.evaluate(test) != AtomNode("BOOLEAN", "nil")):
        for expr in exprs[:-1]:
            evaluator.evaluate(expr, env, "inner")

        return evaluator.evaluate(exprs[-1], env, "inner")


def eval_lambda(args: ConsNode, env: Environment) -> UserDefinedFunction:
    """

    Args:
        args: A pair which car is the param list for lambda and cdr is the body (at least one body).
        env: The closure environment.

    Returns:
        A UserDefinedFunction class representing a lambda expression.
    """
    # Check legality of car (a list or empty)
    param = []
    curr_param = args.car

    while isinstance(curr_param, ConsNode):
        if not isinstance(curr_param.car, AtomNode) or curr_param.car.type != "SYMBOL":
            raise LambdaFormatError()

        param.append(curr_param.car.value)
        curr_param = curr_param.cdr

    if curr_param != AtomNode("BOOLEAN", "nil"):
        raise LambdaFormatError()


    # Body shouldn't be empty
    body = []
    curr_body = args.cdr

    while isinstance(curr_body, ConsNode):
        body.append(curr_body.car)  # 你原本放的是 curr_param（誤）
        curr_body = curr_body.cdr

    if len(body) == 0 or curr_body != AtomNode("BOOLEAN", "nil"):
        raise LambdaFormatError()


    return UserDefinedFunction(param_list=param, body=body, env=env)


__all__ = [
    "special_quote",
    "special_define",
    "special_and",
    "special_or",
    "special_begin",
    "special_if",
    "special_cond",
    "eval_lambda"
]
