class NoClosingQuoteError(Exception):
    def __init__(self, line, column):
        self.line = line
        self.column = column
        super().__init__(f"ERROR (no closing quote) : END-OF-LINE encountered at Line {line} Column {column}")


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
