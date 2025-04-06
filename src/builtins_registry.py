from src.primitive import *
from src.special_forms import *


# `quote`, `define`, `and`, `or` are special forms, others are just normal procedures.
# distinction between special forms and procedures are how arguments evaluates and how the construct behaves
built_in_funcs = {
    # 1. Constructors
    "cons":                 prim_cons,
    "list":                 prim_list,

    # 2. Bypassing the default evaluation
    "quote":                special_quote,       # special form

    # 3. The binding of a symbol to an S-expression
    "define":               special_define,     # special form

    # 4. Part accessors
    "car":                  prim_car,
    "cdr":                  prim_cdr,

    # 5. Primitive predicates (all functions below can only take 1 argument
    "atom?":                prim_is_atom,
    "pair?":                prim_is_pair,
    "list?":                prim_is_list,
    "null?":                prim_is_null,
    "integer?":             prim_is_integer,
    "real?":                prim_is_real,       # real? == number?
    "number?":              prim_is_number,
    "string?":              prim_is_string,
    "boolean?":             prim_is_boolean,
    "symbol?":              prim_is_symbol,

    # 6. Basic arithmetic, logical and string operations
    "+":                    prim_add,
    "-":                    prim_sub,
    "*":                    prim_multiply,
    "/":                    prim_divide,

    "not":                  prim_not,
    "and":                  special_and,   # special form
    "or":                   None,   # special form

    ">":                    None,
    ">=":                   None,
    "<":                    None,
    "<=":                   None,
    "=":                    None,

    "string-append":        None,
    "string>?":             None,
    "string<?":             None,
    "string=?":             None,

    # 7. Equivalence tester
    "eqv?":                 prim_is_eqv,
    "equal?":               prim_is_equal,

    # 8. Sequencing and functional composition
    "begin":                None,   # special form

    # 9. Conditionals
    "if":                   None,   # special form
    "cond":                 None,   # special form

    # 10. Clean Environment
    "clean-environment":    prim_clean_env,
}