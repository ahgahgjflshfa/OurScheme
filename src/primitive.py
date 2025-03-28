

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
    "+":        None,
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