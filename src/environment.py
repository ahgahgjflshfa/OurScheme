from src.errors import DefineError, UnboundSymbolError


class Environment:
    def __init__(self, builtins_ = None):
        self.builtins = builtins_ or {}
        self.user_define = {}

    def define(self, symbol: str, value):
        if symbol in self.builtins:
            raise DefineError(value)

        self.user_define[symbol] = value

    def lookup(self, symbol: str):
        if symbol in self.user_define:
            return self.user_define[symbol]

        elif symbol in self.builtins:
            return self.builtins[symbol]

        else:
            raise UnboundSymbolError(symbol)

    def reset_user_definitions(self):
        self.user_define.clear()