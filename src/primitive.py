from src.ast_nodes import *
from src.errors import IncorrectArgumentType, DivisionByZeroError, IncorrectArgumentNumber


def prim_cons(args: list[ASTNode]):
    if len(args) != 2:
        raise IncorrectArgumentNumber("cons")

    return ConsNode(args[0], args[1])


def prim_list(args: list[ASTNode]):
    if len(args) < 0:
        raise IncorrectArgumentNumber("list")

    elif len(args) == 0:
        return AtomNode("BOOLEAN", "nil")

    # Convert list to cons
    cons_node = ConsNode(args[-1], AtomNode("BOOLEAN", "nil"))
    for arg in args[-2::-1]:
        cons_node = ConsNode(arg, cons_node)

    return cons_node


def prim_is_atom(args: list[ASTNode]) -> AtomNode:
    if len(args) > 1:
        raise IncorrectArgumentNumber("atom?")

    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) else "nil")


def prim_is_pair(args: list[ASTNode]) -> AtomNode:
    return AtomNode("BOOLEAN", "#t" if isinstance(args, ConsNode) else "nil")


def prim_is_list(args: list[ASTNode]) -> AtomNode:
    if len(args) > 1:
        raise IncorrectArgumentNumber("list?")

    current = args[0]

    # Unroll nested cons cells into a list
    while isinstance(current, ConsNode):
        current = current.cdr

    if isinstance(current, AtomNode) and current.type == "BOOLEAN" and current.value == "nil":
        return AtomNode("BOOLEAN", "#t")

    return AtomNode("BOOLEAN", "nil")


def prim_is_null(args: list[ASTNode]) -> AtomNode:
    if len(args) > 1:
        raise IncorrectArgumentNumber("null?")

    arg = args[0]
    return AtomNode(
        "BOOLEAN",
        "#t" if isinstance(arg, AtomNode) and arg.type == "BOOLEAN" and arg.value == "nil" else "nil"
    )


def prim_is_integer(args: list[ASTNode]) -> AtomNode:
    if len(args) > 1:
        raise IncorrectArgumentNumber("integer?")

    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "INT" else "nil")


def prim_is_real(args: list[ASTNode]) -> AtomNode:
    if len(args) > 1:
        raise IncorrectArgumentNumber("real?")

    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type in ("INT", "FLOAT") else "nil")


def prim_is_number(args: list[ASTNode]) -> AtomNode:
    if len(args) > 1:
        raise IncorrectArgumentNumber("number?")

    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type in ("INT", "FLOAT") else "nil")


def prim_is_string(args: list[ASTNode]) -> AtomNode:
    if len(args) > 1:
        raise IncorrectArgumentNumber("string?")

    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "STRING" else "nil")


def prim_is_boolean(args: list[ASTNode]) -> AtomNode:
    if len(args) > 1:
        raise IncorrectArgumentNumber("boolean?")

    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "BOOLEAN" else "nil")


def prim_is_symbol(args: list[ASTNode]) -> AtomNode:
    if len(args) > 1:
        raise IncorrectArgumentNumber("symbol?")

    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "SYMBOL" else "nil")


def prim_add(args: list[ASTNode]) -> AtomNode:
    """
    Performs addition.

    Args:
        args: List of arguments for addition.

    Returns:
        An atom node containing the result of addition.

    Raises:
        ArgumentNumberIncorrect: If number of argument is less than two.
    """
    if len(args) < 2:
        raise IncorrectArgumentNumber('+')

    total = 0
    have_float = False
    for arg in args:
        if not isinstance(arg, AtomNode) or arg.type not in ("INT", "FLOAT"):
            raise IncorrectArgumentType("+", arg)

        if arg.type == "FLOAT": have_float = True

        total += arg.value

    return AtomNode("FLOAT", total) if have_float else AtomNode("INT", total)


def prim_sub(args: list[ASTNode]) -> AtomNode:
    """
    Performs subtraction.

    Args:
        args: List of arguments for subtraction.

    Returns:
        An atom node containing the result of subtraction.

    Raises:
        ArgumentNumberIncorrect: If number of argument is less than two.
    """
    if len(args) < 2:
        raise IncorrectArgumentNumber('-')

    arg = args[0]
    if not isinstance(arg, AtomNode) or arg.type not in ("INT", "FLOAT"):
        raise IncorrectArgumentType("-", arg)

    total = arg.value
    have_float = False
    for arg in args[1:]:
        if not isinstance(arg, AtomNode) or arg.type not in ("INT", "FLOAT"):
            raise IncorrectArgumentType("-", arg)

        if arg.type == "FLOAT": have_float = True

        total -= arg.value

    return AtomNode("FLOAT", total) if have_float else AtomNode("INT", total)


def prim_multiply(args: list[ASTNode]) -> AtomNode:
    """
    Performs multiplication.

    Args:
        args: List of arguments for multiplication.

    Returns:
        A atom node containing the result of multiplication.

    Raises:
        ArgumentNumberIncorrect: If number of argument is less than two.
    """
    if len(args) < 2:
        raise IncorrectArgumentNumber('*')

    total = 1
    have_float = False
    for arg in args:
        if not isinstance(arg, AtomNode) or arg.type not in ("INT", "FLOAT"):
            raise IncorrectArgumentType("*", arg)

        if arg.type == "FLOAT": have_float = True

        total *= arg.value

    return AtomNode("FLOAT", total) if have_float else AtomNode("INT", total)


def prim_divide(args: list[ASTNode]) -> AtomNode:
    """
    Performs division.

    Args:
        args:  List of arguments for division.

    Returns:
        A atom node containing the result of division.

    Raises:
        ArgumentNumberIncorrect: If number of argument is less than two.

        DivisionByZeroError: If divisor is zero.
    """
    if len(args) < 2:
        raise IncorrectArgumentNumber('/')

    arg = args[0]
    if not isinstance(arg, AtomNode) or arg.type not in ("INT", "FLOAT"):
        raise IncorrectArgumentType("//", arg)

    total = arg.value
    have_float = False
    for arg in args[1:]:
        if not isinstance(arg, AtomNode) or arg.type not in ("INT", "FLOAT"):
            raise IncorrectArgumentType("+", arg)

        if arg.type == "FLOAT": have_float = True

        if arg.value == 0:
            raise DivisionByZeroError()

        total /= arg.value

    return AtomNode("FLOAT", total) if have_float or not total.is_integer() else AtomNode("INT", int(total))


global_func = {
    # 1. Constructors
    "cons":     prim_cons,
    "list":     prim_list,

    # 4. Part accessors
    "car":      None,       #
    "cdr":      None,       #

    # 5. Primitive predicates (all functions below can only take 1 argument)
    "atom?":    prim_is_atom,
    "pair?":    prim_is_pair,
    "list?":    prim_is_list,
    "null?":    prim_is_null,
    "integer?": prim_is_integer,
    "real?":    prim_is_real,       # real? == number?
    "number?":  prim_is_number,
    "string?":  prim_is_string,
    "boolean?": prim_is_boolean,
    "symbol?":  prim_is_symbol,

    # 6. Basic arithmetic, logical and string operations
    "+":        prim_add,
    "-":        prim_sub,
    "*":        prim_multiply,
    "/":       prim_divide,

    "not":      None,
    "and":      None,
    "or":       None,

    # 7. Equivalence tester
    "eqv?":     None,
    "equal?":   None,

    # 8. Sequencing and functional composition
    "begin":    None,

    # 9. Conditionals
    "if":       None,
    "cond":     None,

    # 10. Clean Environment
    "clean-environment":    None,
}