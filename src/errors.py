class OurSchemeError(Exception):
    def __init__(self, err_type_: str):
        self.err_type = err_type_
        super().__init__(f"ERROR ({err_type_})")


class NoClosingQuoteError(Exception):
    def __init__(self, line_: int, column_: int):
        self.line = line_
        self.column = column_
        super().__init__(f"ERROR (no closing quote) : END-OF-LINE encountered at Line {self.line} Column {self.column}")


class NotFinishError(Exception):
    """讓parser等待多行輸入"""
    def __init__(self, msg_: str="S expression not complete"):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class EmptyInputError(Exception):
    """遇到註解或是整行空白用的"""
    def __init__(self, msg_: str="Empty Input"):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class UnexpectedTokenError(Exception):
    def __init__(self, msg_: str="Unexpected Token"):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class DefineFormatError(OurSchemeError):
    def __init__(self):
        super().__init__(f"DEFINE format")


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


__all__ = [
    "OurSchemeError",
    "NoClosingQuoteError",
    "NotFinishError",
    "EmptyInputError",
    "UnexpectedTokenError",
    "DefineFormatError",
    "UnboundSymbolError",
    "IncorrectArgumentType",
    "NotCallableError",
    "NonListError",
    "DivisionByZeroError",
    "IncorrectArgumentNumber"
]