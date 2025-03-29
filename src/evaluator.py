from src.ast_nodes import *
from src.environment import Environment
from src.primitive import global_func
from src.errors import NotCallableError, NonListError


global_env = Environment(global_func)   # Initialize environment


def evaluate(ast: ASTNode):
    if isinstance(ast, AtomNode):
        if ast.type == "SYMBOL":
            return global_env.lookup(ast.value)

        else:
            return ast

    elif isinstance(ast, QuoteNode):
        return ast.value

    elif isinstance(ast, ConsNode):
        # 1. evaluate operator
        operator_node = ast.car
        operator = evaluate(operator_node)

        # Check if operator are callable
        if not callable(operator):
            raise NotCallableError(operator)

        # 2. evaluate all arguments
        args = eval_list(ast.cdr)

        # 3. call function
        return operator(args)


def eval_list(cons_node: ASTNode) -> list:
    result = []
    while isinstance(cons_node, ConsNode):
        result.append(evaluate(cons_node.car))
        cons_node = cons_node.cdr

    if not (isinstance(cons_node, AtomNode) and cons_node.value == "nil"):
        raise NonListError()

    return result