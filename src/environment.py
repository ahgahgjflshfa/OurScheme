from src.errors import DefineFormatError, UnboundSymbolError


class Environment:
    def __init__(self, builtins=None, outer=None):
        self.builtins = builtins or {}
        self.user_define = {}
        self.outer = outer

    def define(self, symbol: str, value):
        if self.builtins and symbol in self.builtins:
            raise DefineFormatError()

        self.user_define[symbol] = value

    def lookup(self, symbol: str):
        """Lookup the value of a symbol

        Args:
            symbol: the symbol name

        Returns: the corresponding value of `symbol`

        """
        if symbol in self.user_define:
            return self.user_define[symbol]

        elif self.builtins and symbol in self.builtins:
            return self.builtins[symbol]

        elif self.outer:
            return self.outer.lookup(symbol)

        else:
            raise UnboundSymbolError(symbol)

    def find(self, symbol: str):
        """Find which environment does the symbol defined.

        Args:
            symbol: the symbol name

        Returns: The environment where the symbol defined.
        """
        if symbol in self.user_define:
            return self
        elif self.outer:
            return self.outer.find(symbol)

        return None

    def clear(self):
        self.user_define.clear()
