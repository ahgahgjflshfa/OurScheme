from src.ast_nodes import *
from src.environment import Environment
from src.primitive import global_func
from src.pretty_print import pretty_print


global_env = Environment(global_func)   # Initialize environment

def evaluate(ast: ASTNode):
    if isinstance(ast, AtomNode):
        if ast.type == "SYMBOL":
            func = global_env.lookup(ast.value)

        else:
            pretty_print(ast)

    elif isinstance(ast, ConsNode):
        pass

    elif isinstance(ast, QuoteNode):
        pass