from src.ast_nodes import *
from src.environment import Environment
from src.primitive import global_func
from src.errors import NotCallableError, DefineFormatError, IncorrectArgumentNumber, NonListError


global_env = Environment(global_func)   # Initialize environment


def evaluate(ast: ASTNode, env: Environment = global_env):
    if isinstance(ast, AtomNode):
        if ast.type == "SYMBOL":
            return env.lookup(ast.value)
        else:
            return ast  # number / boolean / string 等直接回傳

    elif isinstance(ast, QuoteNode):
        return ast.value  # quote 回傳內容，不做 evaluate

    elif isinstance(ast, ConsNode):
        operator_node = ast.car

        if isinstance(operator_node, AtomNode):
            op = operator_node.value

            # === (quote <expr>)
            if op == "quote":
                args_node = ast.cdr
                if not (isinstance(args_node, ConsNode) and isinstance(args_node.cdr, AtomNode) and args_node.cdr.value == "nil"):
                    raise IncorrectArgumentNumber("quote")

                return args_node.car

            # === (define <symbol> <value>)
            elif op == "define":
                args_node = ast.cdr

                # 檢查 args_node 必須是 (symbol value)
                if not isinstance(args_node, ConsNode):
                    raise DefineFormatError()

                name_node = args_node.car
                value_pair = args_node.cdr

                if not (isinstance(name_node, AtomNode) and name_node.type == "SYMBOL"):
                    raise DefineFormatError()

                if not isinstance(value_pair, ConsNode):
                    raise IncorrectArgumentNumber("define")

                value_node = value_pair.car
                rest = value_pair.cdr

                if not (isinstance(rest, AtomNode) and rest.value == "nil"):
                    raise IncorrectArgumentNumber("define")

                value = evaluate(value_node, env)
                env.define(name_node.value, value)

                return AtomNode("SYMBOL", name_node.value)

            elif op == "if":
                pass

        # === 一般函數呼叫 ===
        operator = evaluate(operator_node, env)
        args = eval_list(ast, env)

        if not callable(operator):
            raise NotCallableError(operator)

        return operator(args)

def eval_list(cons_node: ConsNode, env: Environment) -> list:
    result = []
    curr_ast = cons_node.cdr
    while isinstance(curr_ast, ConsNode):
        result.append(evaluate(curr_ast.car, env))
        curr_ast = curr_ast.cdr

    if not (isinstance(curr_ast, AtomNode) and curr_ast.value == "nil"):
        raise NonListError(cons_node)

    return result