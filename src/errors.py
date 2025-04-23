class NotFinishError(Exception):
    """讓parser等待多行輸入"""

    def __init__(self, msg_: str = "S expression not complete"):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class EmptyInputError(Exception):
    """遇到註解或是整行空白用的"""

    def __init__(self, msg_: str = "Empty Input"):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class SchemeExitException(Exception):
    pass


class OurSchemeError(Exception):
    def __init__(self, err_type_: str):
        self.err_type = err_type_
        super().__init__(f"ERROR ({err_type_})")


class NoClosingQuoteError(OurSchemeError):
    def __init__(self, line_: int, column_: int):
        self.line = line_
        self.column = column_
        super().__init__("no closing quote")


class UnexpectedTokenError(OurSchemeError):
    def __init__(self, type_, line, column, value):
        self.type = type_
        self.line = line
        self.column = column
        self.value = value
        super().__init__("unexpected token")


class DefineFormatError(OurSchemeError):
    def __init__(self):
        super().__init__(f"DEFINE format")
        

class CondFormatError(OurSchemeError):
    def __init__(self):
        super().__init__(f"COND format")


class LambdaFormatError(OurSchemeError):
    def __init__(self):
        super().__init__(f"lambda format")


class LetFormatError(OurSchemeError):
    def __init__(self, ast):
        self.ast = ast
        super().__init__(f"LET format")


class UnboundSymbolError(OurSchemeError):
    def __init__(self, symbol_: str):
        self.symbol = symbol_
        super().__init__(f"unbound symbol")


class IncorrectArgumentType(OurSchemeError):
    def __init__(self, operator_: str | int | float, arg_: any):
        self.operator = operator_
        self.arg = arg_
        super().__init__(f"{operator_} with incorrect argument type")


class NotCallableError(OurSchemeError):
    def __init__(self, operator_: "AtomNode"):
        self.operator = operator_
        super().__init__(f"attempt to apply non-function")


class NonListError(OurSchemeError):
    def __init__(self, ast_):
        self.ast = ast_
        super().__init__(f"non-list")


class DivisionByZeroError(OurSchemeError):
    def __init__(self):
        super().__init__(f"division by zero")


class IncorrectArgumentNumber(OurSchemeError):
    def __init__(self, operator_: str):
        self.operator = operator_
        super().__init__(f"incorrect number of arguments")


class LevelDefineError(OurSchemeError):
    def __init__(self):
        super().__init__(f"level of DEFINE")


class LevelCleanEnvError(OurSchemeError):
    def __init__(self):
        super().__init__(f"level of CLEAN-ENVIRONMENT")


class LevelExitError(OurSchemeError):
    def __init__(self):
        super().__init__(f"level of EXIT")


class NoReturnValue(OurSchemeError):
    def __init__(self, ast):
        self.ast = ast
        super().__init__(f"no return value")


class UnboundParameterError(OurSchemeError):
    def __init__(self, ast):
        self.ast = ast
        super().__init__(f"unbound parameter")


class UnboundConditionError(OurSchemeError):
    def __init__(self, ast):
        self.ast = ast
        super().__init__(f"unbound condition")


__all__ = [
    "OurSchemeError",
    "NoClosingQuoteError",
    "NotFinishError",
    "EmptyInputError",
    "UnexpectedTokenError",
    "DefineFormatError",
    "CondFormatError",
    "LambdaFormatError",
    "LetFormatError",
    "UnboundSymbolError",
    "IncorrectArgumentType",
    "NotCallableError",
    "NonListError",
    "DivisionByZeroError",
    "IncorrectArgumentNumber",
    "LevelDefineError",
    "LevelCleanEnvError",
    "LevelExitError",
    "NoReturnValue",
    "UnboundParameterError",
    "UnboundConditionError"
]
