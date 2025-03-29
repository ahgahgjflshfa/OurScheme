from src.ast_nodes import *
from src.errors import IncorrectArgumentType


def PrimAdd(args: list[ASTNode]):
    total = 0
    have_float = False
    for arg in args:
        if not isinstance(arg, AtomNode) or arg.type not in ("INT", "FLOAT"):
            raise IncorrectArgumentType("+", arg)

        if arg.type == "FLOAT": have_float = True

        total += arg.value

    return AtomNode("FLOAT", total) if have_float else AtomNode("INT", total)

global_func = {
    # 1. Constructors
    "cons":     None,
    "list":     None,       # ()

    # 2. Bypassing the default evaluation
    "quote":    None,       # (quote s-exp)

    # 3. The binding of a symbol to an S-expression
    "define":   None,       # (define sym val)

    # 4. Part accessors
    "car":      None,       #
    "cdr":      None,       #

    # 5. Primitive predicates (all functions below can only take 1 argument)
    "atom?":    None,
    "pair?":    None,
    "list?":    None,
    "null?":    None,
    "integer?": None,
    "real?":    None,       # real? = number?
    "number?":  None,
    "string?":  None,
    "boolean?": None,
    "symbol?":  None,

    # 6. Basic arithmetic, logical and string operations
    "+":        PrimAdd,
    "-":        None,
    "*":        None,
    "//":       None,

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