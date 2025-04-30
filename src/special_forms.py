from src.ast_nodes import *
from src.environment import Environment
from src.errors import DefineFormatError, CondFormatError, LambdaFormatError, LetFormatError, UnboundConditionError, \
    NoReturnValue
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
def special_quote(args: list[ASTNode], _env: Environment, _evaluator: "Evaluator") -> ASTNode:
    arg = args[0]
    return arg


@special(name="define")
def special_define(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    # Define has it own rules for the arguments, so I'm not using the decorator for checking argument
    if len(args) < 2:
        raise DefineFormatError()

    if isinstance(args[0], AtomNode):
        if len(args) != 2:
            raise DefineFormatError()

        symbol = args[0]

        if symbol.type != "SYMBOL":
            raise DefineFormatError()

        symbol_name = symbol.value
        value = args[1]

        evaled_value = evaluator.evaluate(value, env, "inner")
        if evaled_value is None:
            raise NoReturnValue(value)

        env.define(symbol_name, evaled_value)

        if evaluator.verbose:
            print(f"{symbol_name} defined")

    else:  # syntactic sugar for lambda, e.g. (define (f x y) (+ x y)) === (define f (lambda (x y) (+ x y)))
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

        env.define(func_name, UserDefinedFunction(name=func_name, param_list=params, body=body))

        if evaluator.verbose:
            print(f"{func_name} defined")

    return AtomNode("VOID", "")


@special(name="and", min_args=2)
def special_and(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    eval_result = None
    for arg in args:
        eval_result = evaluator.evaluate(arg, env, "inner")
        if eval_result is None:
            raise UnboundConditionError(arg)

        if eval_result == AtomNode("BOOLEAN", "nil"):
            return AtomNode("BOOLEAN", "nil")

    return eval_result


@special(name="or", min_args=2)
def special_or(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    for arg in args:
        eval_result = evaluator.evaluate(arg, env, "inner")
        if eval_result is None:
            raise UnboundConditionError(arg)

        if eval_result != AtomNode("BOOLEAN", "nil"):
            return eval_result

    return AtomNode("BOOLEAN", "nil")


@special(name="begin", min_args=1)
def special_begin(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode:
    for expr in args[:-1]:
        evaluator.evaluate(expr, env, "inner")

    return evaluator.evaluate(args[-1], env, "inner")


@special(name="if", min_args=2, max_args=3)
def special_if(args: list[ASTNode], env: Environment, evaluator: "Evaluator") -> ASTNode | None:
    test_expr, then_expr, *rest = args
    else_expr = rest[0] if rest else None

    if evaluator.evaluate(test_expr, env, "inner") != AtomNode("BOOLEAN", "nil"):
        return evaluator.evaluate(then_expr, env, "inner")
    elif else_expr is not None:
        return evaluator.evaluate(else_expr, env, "inner")

    return None


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
        if evaluator.evaluate(test, env, "inner") != AtomNode("BOOLEAN", "nil"):
            for expr in exprs[:-1]:
                evaluator.evaluate(expr, env, "inner")

            return evaluator.evaluate(exprs[-1], env, "inner")

    test, exprs = clauses[-1]
    if (test == AtomNode("SYMBOL", "else") or
            evaluator.evaluate(test, env, "inner") != AtomNode("BOOLEAN", "nil")):
        for expr in exprs[:-1]:
            evaluator.evaluate(expr, env, "inner")

        return evaluator.evaluate(exprs[-1], env, "inner")

    return None


@special(name="let")
def special_let(args: list[ASTNode], env: Environment, evaluator: "Evaluator"):
    def args_to_cons(args: list[ASTNode]) -> ASTNode:
        result = AtomNode("BOOLEAN", "nil")
        for node in reversed(args):  # 從最後一個開始包
            result = ConsNode(node, result)
        return result

    full_let_expr = ConsNode(AtomNode("SYMBOL", "let"), args_to_cons(args))

    if len(args) < 2:
        raise LetFormatError(full_let_expr)

    let_env = Environment(outer=env)
    bindings, *body = args

    if isinstance(bindings, AtomNode):
        if not (bindings.type == "BOOLEAN" and bindings.value == "nil"):
            raise LetFormatError(full_let_expr)
        binding_list = []
    else:
        if not isinstance(bindings, ConsNode):
            raise LetFormatError(full_let_expr)

        binding_list = []
        curr = bindings
        while isinstance(curr, ConsNode):
            pair = curr.car

            if not (isinstance(pair, ConsNode) and
                    isinstance(pair.car, AtomNode) and pair.car.type == "SYMBOL" and
                    isinstance(pair.cdr, ConsNode) and
                    pair.cdr.cdr == AtomNode("BOOLEAN", "nil")):
                raise LetFormatError(full_let_expr)

            symbol = pair.car.value
            expr = pair.cdr.car
            binding_list.append((symbol, expr))
            curr = curr.cdr

        if curr != AtomNode("BOOLEAN", "nil"):
            raise LetFormatError(full_let_expr)

    for symbol, expr in binding_list:
        value = evaluator.evaluate(expr, env, "inner")
        if value is None:
            raise NoReturnValue(expr)

        let_env.define(symbol, value)

    for expr in body[:-1]:
        evaluator.evaluate(expr, let_env, "inner")

    return evaluator.evaluate(body[-1], let_env, "inner")


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

    return UserDefinedFunction(name="lambda", param_list=param, body=body)


__all__ = [
    "special_quote",
    "special_define",
    "special_and",
    "special_or",
    "special_begin",
    "special_if",
    "special_cond",
    "special_let",
    "eval_lambda"
]
