from src.ast_nodes import *
from src.environment import Environment
from src.errors import IncorrectArgumentType, DivisionByZeroError, SchemeExitException
from src.base.callable import CallableEntity


class PrimitiveFunction(CallableEntity):
    def __init__(self, name, func, min_args=None, max_args=None, arg_types=None):
        super().__init__(name, func, min_args, max_args)
        self.arg_types = arg_types

    def check_arg_types(self, args: list[ASTNode]):
        if not self.arg_types:
            return

        for i, arg in enumerate(args):
            # 如果 arg_types 是單一類型集合，套用到所有參數
            if isinstance(self.arg_types, (tuple, set)):
                valid_types = self.arg_types
            elif isinstance(self.arg_types, list):
                if i >= len(self.arg_types):
                    break  # 超過定義不檢查

                expected_type = self.arg_types[i]
                valid_types = (expected_type,)

            # 開始比對類型
            if not self._is_type_valid(arg, valid_types):
                raise IncorrectArgumentType(self.name, arg)

    def _is_type_valid(self, arg, expected_types):
        # atom 型別對應
        if isinstance(expected_types, str):
            expected_types = (expected_types,)

        for t in expected_types:
            if t == "any":
                return True
            elif t == "pair":
                if isinstance(arg, ConsNode):
                    return True
            elif isinstance(arg, AtomNode) and arg.type == t:
                return True
        return False

    def __call__(self, args: list[ASTNode], env: Environment):
        self.check_arg_types(args)
        return self.func(args, env)


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
def prim_cons(args: list[ASTNode], _) -> ConsNode:
    return ConsNode(args[0], args[1])


@primitive(name="list")
def prim_list(args: list[ASTNode], _) -> AtomNode | ConsNode:
    if len(args) == 0:
        return AtomNode("BOOLEAN", "nil")

    # Convert list to cons
    cons_node = ConsNode(args[-1], AtomNode("BOOLEAN", "nil"))
    for arg in args[-2::-1]:
        cons_node = ConsNode(arg, cons_node)

    return cons_node


@primitive(name="car", min_args=1, max_args=1, arg_types=["pair"])
def prim_car(args: list[ASTNode], _) -> ASTNode:
    arg = args[0]
    return arg.car


@primitive(name="cdr", min_args=1, max_args=1, arg_types=["pair"])
def prim_cdr(args: list[ASTNode], _) -> ASTNode:
    arg = args[0]
    return arg.cdr


@primitive(name="atom?", min_args=1, max_args=1)
def prim_is_atom(args: list[ASTNode], _) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if not isinstance(arg, ConsNode) and not isinstance(arg, QuoteNode) else "nil")


@primitive(name="pair?", min_args=1, max_args=1)
def prim_is_pair(args: list[ASTNode], _) -> AtomNode:
    return AtomNode("BOOLEAN", "#t" if isinstance(args[0], ConsNode) else "nil")


@primitive(name="pair?", min_args=1, max_args=1)
def prim_is_list(args: list[ASTNode], _) -> AtomNode:
    current = args[0]

    # Unroll nested cons cells into a list
    while isinstance(current, ConsNode):
        current = current.cdr

    if isinstance(current, AtomNode) and current.type == "BOOLEAN" and current.value == "nil":
        return AtomNode("BOOLEAN", "#t")

    return AtomNode("BOOLEAN", "nil")


@primitive(name="null?", min_args=1, max_args=1)
def prim_is_null(args: list[ASTNode], _) -> AtomNode:
    arg = args[0]
    return AtomNode(
        "BOOLEAN",
        "#t" if isinstance(arg, AtomNode) and arg.type == "BOOLEAN" and arg.value == "nil" else "nil"
    )


@primitive(name="integer?", min_args=1, max_args=1)
def prim_is_integer(args: list[ASTNode], _) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "INT" else "nil")


@primitive(name="real?", min_args=1, max_args=1)
def prim_is_real(args: list[ASTNode], _) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type in ("INT", "FLOAT") else "nil")


@primitive(name="number?", min_args=1, max_args=1)
def prim_is_number(args: list[ASTNode], _) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type in ("INT", "FLOAT") else "nil")


@primitive(name="string?", min_args=1, max_args=1)
def prim_is_string(args: list[ASTNode], _) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "STRING" else "nil")


@primitive(name="boolean?", min_args=1, max_args=1)
def prim_is_boolean(args: list[ASTNode], _) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "BOOLEAN" else "nil")


@primitive(name="symbol?", min_args=1, max_args=1)
def prim_is_symbol(args: list[ASTNode], _) -> AtomNode:
    arg = args[0]
    return AtomNode("BOOLEAN", "#t" if isinstance(arg, AtomNode) and arg.type == "SYMBOL" else "nil")


@primitive(name="+", min_args=2, arg_types=("INT", "FLOAT"))
def prim_add(args: list[ASTNode], _) -> AtomNode:
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
def prim_sub(args: list[ASTNode], _) -> AtomNode:
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
def prim_multiply(args: list[ASTNode], _) -> AtomNode:
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
def prim_divide(args: list[ASTNode], _) -> AtomNode:
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
def prim_not(args: list[ASTNode], _) -> ASTNode:
    # Only #f and nil are false, others are all true (`falsey`)
    arg = args[0]
    if arg == AtomNode("BOOLEAN", "nil"):
        return AtomNode("BOOLEAN", "#t")
    else:
        return AtomNode("BOOLEAN", "nil")


@primitive(name=">", min_args=2, arg_types=("INT", "FLOAT"))
def prim_greater(args: list[ASTNode], _) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value <= args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name=">=", min_args=2, arg_types=("INT", "FLOAT"))
def prim_greater_equal(args: list[ASTNode], _) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value < args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="<", min_args=2, arg_types=("INT", "FLOAT"))
def prim_smaller(args: list[ASTNode], _) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value >= args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="<=", min_args=2, arg_types=("INT", "FLOAT"))
def prim_smaller_equal(args: list[ASTNode], _) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value > args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="=", min_args=2, arg_types=("INT", "FLOAT"))
def prim_equal(args: list[ASTNode], _) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value != args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="string-append", min_args=2, arg_types=("STRING",))
def prim_string_append(args: list[ASTNode], _) -> ASTNode:
    new_string = ""

    for arg in args:
        new_string += arg.value

    return AtomNode("STRING", new_string)


@primitive(name="string>?", min_args=2, arg_types=("STRING",))
def prim_string_greater(args: list[ASTNode], _) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value <= args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="string<?", min_args=2, arg_types=("STRING",))
def prim_string_smaller(args: list[ASTNode], _) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value >= args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="string=?", min_args=2, arg_types=("STRING",))
def prim_string_equal(args: list[ASTNode], _) -> ASTNode:
    for i in range(len(args) - 1):
        if args[i].value != args[i + 1].value:
            return AtomNode("BOOLEAN", "nil")

    return AtomNode("BOOLEAN", "#t")


@primitive(name="eqv?", min_args=2, max_args=2)
def prim_is_eqv(args: list[ASTNode], _) -> ASTNode:
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
def prim_is_equal(args: list[ASTNode], _) -> ASTNode:
    arg1 = args[0]
    arg2 = args[1]
    return AtomNode("BOOLEAN", "#t" if arg1 == arg2 else "nil")


@primitive(name="clean-environment", min_args=0, max_args=0)
def prim_clean_env(_, env: Environment) -> ASTNode:
    env.clear()
    return AtomNode("SYMBOL", "environment cleaned")


@primitive(name="exit", min_args=0, max_args=0)
def prim_exit(_, __) -> None:
    raise SchemeExitException("Interpreter exited")


__all__ = [
    "CallableEntity",
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
    "prim_exit"
]
