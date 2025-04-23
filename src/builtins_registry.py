from src.primitive import *
from src.special_forms import *
from src.function_object import DummySymbolReference

# `quote`, `define`, `and`, `or` are special forms, others are just normal procedures.
# distinction between special forms and procedures are how arguments evaluates and how the construct behaves
built_in_funcs = {
    # 1. Constructors
    "cons": prim_cons,
    "list": prim_list,

    # 2. Bypassing the default evaluation
    "quote": special_quote,  # special form

    # 3. The binding of a symbol to an S-expression
    "define": special_define,  # special form

    # 4. Part accessors
    "car": prim_car,
    "cdr": prim_cdr,

    # 5. Primitive predicates (all functions below can only take 1 argument
    "atom?": prim_is_atom,
    "pair?": prim_is_pair,
    "list?": prim_is_list,
    "null?": prim_is_null,
    "integer?": prim_is_integer,
    "real?": prim_is_real,  # real? == number?
    "number?": prim_is_number,
    "string?": prim_is_string,
    "boolean?": prim_is_boolean,
    "symbol?": prim_is_symbol,

    # 6. Basic arithmetic, logical and string operations
    "+": prim_add,
    "-": prim_sub,
    "*": prim_multiply,
    "/": prim_divide,

    "not": prim_not,
    "and": special_and,  # special form
    "or": special_or,  # special form

    ">": prim_greater,
    ">=": prim_greater_equal,
    "<": prim_smaller,
    "<=": prim_smaller_equal,
    "=": prim_equal,

    "string-append": prim_string_append,
    "string>?": prim_string_greater,
    "string<?": prim_string_smaller,
    "string=?": prim_string_equal,

    # 7. Equivalence tester
    "eqv?": prim_is_eqv,
    "equal?": prim_is_equal,

    # 8. Sequencing and functional composition
    "begin": special_begin,  # special form

    # 9. Conditionals
    "if": special_if,  # special form
    "cond": special_cond,  # special form

    # 10. Clean Environment
    "clean-environment": prim_clean_env,

    # 11. Exit Interpreter
    "exit": prim_exit,


    # ========
    "let": special_let,

    # Dummy symbols
    "lambda": DummySymbolReference("lambda"),
    "verbose": DummySymbolReference("verbose"),
    "verbose?": DummySymbolReference("verbose?"),
}
