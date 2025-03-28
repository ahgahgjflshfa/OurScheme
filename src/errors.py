from src.pretty_print import pretty_print


class NoClosingQuoteError(Exception):
    def __init__(self, line_, column_):
        self.line = line_
        self.column = column_
        super().__init__(f"ERROR (no closing quote) : END-OF-LINE encountered at Line {self.line} Column {self.column}")


class NotFinishError(Exception):
    """讓parser等待多行輸入"""
    def __init__(self, msg_="S expression not complete"):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class EmptyInputError(Exception):
    """遇到註解或是整行空白用的"""
    def __init__(self, msg_="Empty Input"):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class UnexpectedTokenError(Exception):
    def __init__(self, msg_="Unexpected Token"):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class DefineError(Exception):
    def __init__(self, value_):
        self.value = value_
        super().__init__(f"ERROR (DEFINE format) : {pretty_print(self.value)}")


class UnboundSymbolError(Exception):
    def __init__(self, symbol_):
        self.symbol = symbol_
        super().__init__(f"ERROR (unbound symbol) : {self.symbol}")