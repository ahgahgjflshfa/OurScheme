from src.ast_nodes import *
from src.environment import Environment
from src.errors import DivisionByZeroError, SchemeExitException, IncorrectArgumentType, NoClosingQuoteError, \
    EmptyInputError, UnexpectedTokenError, NotFinishError
from src.function_object import PrimitiveFunction
from src.pretty_print import pretty_print


def primitive(name=None, min_args=None, max_args=None, arg_types=None):
    def decorator(func):
        return PrimitiveFunction(
            name=name or func.__name__,
            func=func,
            min_args=min_args,
            max_args=max_args,
            arg_types=arg_types,
        )

    return decorator


@primitive(name="cons", min_args=2, max_args=2)
def prim_cons(args: list[ASTNode], _env, _evaluator) -> ConsNode:
    return ConsNode(args[0], args[1])


@primitive(name="list")
def prim_list(args: list[ASTNode], _env, _evaluator) -> AtomNode | ConsNode:
    if len(args) == 0:
        return AtomNode("BOOLEAN", "nil")

    # Convert list to cons
    cons_node = ConsNode(args[-1], AtomNode("BOOLEAN", "nil"))
    for arg in args[-2::-1]:
        cons_node = ConsNode(arg, cons_node)

    return cons_node


@primitive(name="car", min_args=1, max_args=1, arg_types=["pair"])
def prim_car(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    arg = args[0]
    return arg.car


@primitive(name="cdr", min_args=1, max_args=1, arg_types=["pair"])
def prim_cdr(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    arg = args[0]
    return arg.cdr


@primitive(name="atom?", min_args=1, max_args=1)
def prim_is_atom(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if not isinstance(arg, ConsNode) and not isinstance(arg, QuoteNode) else "nil")


@primitive(name="pair?", min_args=1, max_args=1)
def prim_is_pair(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    return AtomNode("BOOLEAN", "#t" if isinstance(args[0], ConsNode) else "nil")


@primitive(name="pair?", min_args=1, max_args=1)
def prim_is_list(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    current = args[0]

    # Unroll nested cons cells into a list
    while isinstance(current, ConsNode):
        current = current.cdr

    if isinstance(current, AtomNode) and current.type == "BOOLEAN" and current.value == "nil":
        return AtomNode("BOOLEAN", "#t")

    return AtomNode("BOOLEAN", "nil")


@primitive(name="null?", min_args=1, max_args=1)
def prim_is_null(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode(
        "BOOLEAN",
        "#t" if isinstance(arg, AtomNode) and arg.type == "BOOLEAN" and arg.value == "nil" else "nil"
    )


@primitive(name="integer?", min_args=1, max_args=1)
def prim_is_integer(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "INT" else "nil")


@primitive(name="real?", min_args=1, max_args=1)
def prim_is_real(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type in ("INT", "FLOAT") else "nil")


@primitive(name="number?", min_args=1, max_args=1)
def prim_is_number(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type in ("INT", "FLOAT") else "nil")


@primitive(name="string?", min_args=1, max_args=1)
def prim_is_string(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "STRING" else "nil")


@primitive(name="boolean?", min_args=1, max_args=1)
def prim_is_boolean(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "BOOLEAN" else "nil")


@primitive(name="symbol?", min_args=1, max_args=1)
def prim_is_symbol(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "SYMBOL" else "nil")


@primitive(name="+", min_args=2, arg_types=("INT", "FLOAT"))
def prim_add(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    """
    Performs addition.

    Args:
        args: List of arguments for addition.

    Returns:
        An atom node containing the result of addition.
    """
    total = 0
    have_float = False
    for arg in args:
        if arg.type == "FLOAT": have_float = True
        total += arg.value

    return AtomNode("FLOAT", total) if have_float else AtomNode("INT", total)


@primitive(name="-", min_args=2, arg_types=("INT", "FLOAT"))
def prim_sub(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    """
    Performs subtraction.

    Args:
        args: List of arguments for subtraction.

    Returns:
        An atom node containing the result of subtraction.
    """
    total = args[0].value
    have_float = False if args[0].type != "FLOAT" else True
    for arg in args[1:]:
        if arg.type == "FLOAT": have_float = True
        total -= arg.value

    return AtomNode("FLOAT", total) if have_float else AtomNode("INT", total)


@primitive(name="*", min_args=2, arg_types=("INT", "FLOAT"))
def prim_multiply(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    """
    Performs multiplication.

    Args:
        args: List of arguments for multiplication.

    Returns:
        A atom node containing the result of multiplication.
    """
    total = 1
    have_float = False
    for arg in args:
        if arg.type == "FLOAT": have_float = True

        total *= arg.value

    return AtomNode("FLOAT", total) if have_float else AtomNode("INT", total)


@primitive(name="/", min_args=2, arg_types=("INT", "FLOAT"))
def prim_divide(args: list[ASTNode], _env, _evaluator) -> AtomNode:
    """
    Performs division.

    Args:
        args:  List of arguments for division.

    Returns:
        A atom node containing the result of division.

    Raises:
        DivisionByZeroError: If divisor is zero.
    """
    total = args[0].value
    have_float = False if args[0].type != "FLOAT" else True
    for arg in args[1:]:
        if arg.type == "FLOAT": have_float = True

        if arg.value == 0:
            raise DivisionByZeroError()

        total /= arg.value

    return AtomNode("FLOAT", total) if have_float else AtomNode("INT", int(total))


@primitive(name="not", min_args=1, max_args=1)
def prim_not(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    # Only #f and nil are false, others are all true (`falsey`)
    arg = args[0]
    if arg == AtomNode("BOOLEAN", "nil"):
        return AtomNode("BOOLEAN", "#t")
    else:
        return AtomNode("BOOLEAN", "nil")


@primitive(name=">", min_args=2, arg_types=("INT", "FLOAT"))
def prim_greater(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value <= args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name=">=", min_args=2, arg_types=("INT", "FLOAT"))
def prim_greater_equal(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value < args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="<", min_args=2, arg_types=("INT", "FLOAT"))
def prim_smaller(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value >= args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="<=", min_args=2, arg_types=("INT", "FLOAT"))
def prim_smaller_equal(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value > args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="=", min_args=2, arg_types=("INT", "FLOAT"))
def prim_equal(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value != args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="string-append", min_args=2, arg_types=("STRING",))
def prim_string_append(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    new_string = ""

    for arg in args:
        new_string += arg.value

    return AtomNode("STRING", new_string)


@primitive(name="string>?", min_args=2, arg_types=("STRING",))
def prim_string_greater(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value <= args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="string<?", min_args=2, arg_types=("STRING",))
def prim_string_smaller(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value >= args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="string=?", min_args=2, arg_types=("STRING",))
def prim_string_equal(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value != args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="eqv?", min_args=2, max_args=2)
def prim_is_eqv(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    arg1 = args[0]
    arg2 = args[1]

    if not (type(arg1) == type(arg2)):
        return AtomNode("BOOLEAN", "nil")

    elif isinstance(arg1, AtomNode) and arg1.type != "STRING" and isinstance(arg2, AtomNode) and arg2.type != "STRING":
        # If arguments are atom node and not string, then compare the value of node, not the address
        # Note: only immutable atomic types are compared by value in `eqv?`
        return AtomNode("BOOLEAN", "#t" if arg1 == arg2 else "nil")

    else:
        return AtomNode("BOOLEAN", "#t" if id(arg1) == id(arg2) else "nil")


@primitive(name="equal?", min_args=2, max_args=2)
def prim_is_equal(args: list[ASTNode], _env, _evaluator) -> ASTNode:
    arg1 = args[0]
    arg2 = args[1]
    return AtomNode("BOOLEAN", "#t" if arg1 == arg2 else "nil")


@primitive(name="clean-environment", min_args=0, max_args=0)
def prim_clean_env(_args, env: "Environment", evaluator: "Evaluator") -> ASTNode:
    env.clear()
    if evaluator.verbose:
        print("environment cleaned")

    return AtomNode("VOID", "")


@primitive(name="create-error-object", min_args=1, max_args=1)
def prim_create_error_obj(args: list[ASTNode], _env: Environment, _evaluator: "Evaluator"):
    arg = args[0]
    if not (isinstance(arg, AtomNode) and arg.type == "STRING"):
        raise IncorrectArgumentType("create-error-object", arg)

    return AtomNode("ERROR", arg.value)


@primitive(name="error-object?", min_args=1, max_args=1)
def prim_is_error_obj(args: list[ASTNode], _env: Environment, _evaluator: "Evaluator"):
    is_error = isinstance(args[0], AtomNode) and args[0].type == "ERROR"
    return AtomNode("BOOLEAN", "#t" if is_error else "nil")


@primitive(name="display-string", min_args=1, max_args=1)
def prim_display_string(args: list[ASTNode], _env: Environment, _evaluator: "Evaluator"):
    node = args[0]
    if not (isinstance(node, AtomNode) and node.type in ("STRING", "ERROR")):
        raise IncorrectArgumentType("display-string", node)

    print(node.value, end="")
    return node


@primitive(name="newline", min_args=0, max_args=0)
def prim_newline(_args: list[ASTNode], _env: Environment, _evaluator: "Evaluator"):
    print()
    return AtomNode("BOOLEAN", "nil")


@primitive(name="symbol->string", min_args=1, max_args=1)
def prim_sym_to_str(args: list[ASTNode], _env: Environment, _evaluator: "Evaluator"):
    arg = args[0]
    if isinstance(arg, AtomNode) and arg.type == "SYMBOL":
        return AtomNode("STRING", arg.value)
    else:
        raise IncorrectArgumentType("symbol->string", arg)


@primitive(name="number->string", min_args=1, max_args=1)
def prim_num_to_str(args: list[ASTNode], _env: Environment, _evaluator: "Evaluator"):
    arg = args[0]
    if isinstance(arg, AtomNode) and arg.type in ("FLOAT", "INT"):
        if arg.type == "FLOAT":
            return AtomNode("STRING", f"{arg.value:.3f}")
        else:
            return AtomNode("STRING", f"{arg.value}")
    else:
        raise IncorrectArgumentType("number->string", arg)


@primitive(name="write", min_args=1, max_args=1)
def prim_write(args: list[ASTNode], _env: Environment, _evaluator: "Evaluator"):
    obj = args[0]
    print(pretty_print(obj), end="")
    return obj


@primitive(name="read", min_args=0, max_args=0)
def prim_read(_args, _env, evaluator: "Evaluator"):
    # do one parsing and return parsing result
    parser = evaluator.parser
    lexer = parser.lexer

    partial_input = lexer.source_code[parser.last_s_exp_pos + 1:]  # only get those not used

    while True:
        try:
            if parser.current.type == "EOF":
                # No token left in lexer, so need to get new input for (read)
                new_input = input()
                partial_input += '\n' + new_input

                lexer.reset(partial_input)
                lexer.set_position(0)
                parser.reset(lexer)

            result = parser.parse()
            return result

        except UnexpectedTokenError as e:
            try:
                lexer.reset("")
                parser.reset(lexer)
            except EmptyInputError:
                pass

            if e.type == 1:
                return AtomNode("ERROR", f"{e} : atom or '(' expected when token at Line {e.line} Column {e.column} is >>{e.value}<<")
            else:
                return AtomNode("ERROR", f"{e} : ')' expected when token at Line {e.line} Column {e.column} is >>{e.value}<<")

        except NoClosingQuoteError as e:
            try:
                lexer.reset("")
                parser.reset(lexer)
            except EmptyInputError:
                # this error are used for telling repl not to clear partial input, so need to catch this error
                pass

            return AtomNode("ERROR", f"{e} : END-OF-LINE encountered at Line {e.line} Column {e.column}")

        except (NotFinishError, EmptyInputError):
            continue


@primitive(name="eval", min_args=1, max_args=1)
def prim_eval(args: list[ASTNode], env: Environment, evaluator: "Evaluator"):
    return evaluator.evaluate(args[0], evaluator.global_env, level="toplevel")


@primitive(name="exit", min_args=0, max_args=0)
def prim_exit(_args, _env, _evaluator) -> None:
    raise SchemeExitException("Interpreter exited")


__all__ = [
    "prim_cons",
    "prim_list",
    "prim_car",
    "prim_cdr",
    "prim_is_atom",
    "prim_is_pair",
    "prim_is_list",
    "prim_is_null",
    "prim_is_integer",
    "prim_is_real",
    "prim_is_number",
    "prim_is_string",
    "prim_is_boolean",
    "prim_is_symbol",
    "prim_add",
    "prim_sub",
    "prim_multiply",
    "prim_divide",
    "prim_not",
    "prim_greater",
    "prim_greater_equal",
    "prim_smaller",
    "prim_smaller_equal",
    "prim_equal",
    "prim_string_append",
    "prim_string_greater",
    "prim_string_smaller",
    "prim_string_equal",
    "prim_is_eqv",
    "prim_is_equal",
    "prim_clean_env",
    "prim_create_error_obj",
    "prim_is_error_obj",
    "prim_display_string",
    "prim_newline",
    "prim_sym_to_str",
    "prim_num_to_str",
    "prim_write",
    "prim_read",
    "prim_eval",
    "prim_exit",
]
