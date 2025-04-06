from src.errors import NonListError


class ASTNode:
    def __eq__(self, other):
        return isinstance(other, self.__class__) and vars(self) == vars(other)

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class AtomNode(ASTNode):
    def __init__(self, type_, value):
        self.type = type_  # "INT", "FLOAT", "SYMBOL", "BOOLEAN"
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type}, {repr(self.value)})"


class ConsNode(ASTNode):
    def __init__(self, car: ASTNode, cdr: ASTNode = None):
        self.car = car
        self.cdr = cdr  # cdr 可以是 ASTNode 或 None

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.car)}, {repr(self.cdr)})"

    def __iter__(self):
        curr = self
        while isinstance(curr, ConsNode):
            yield curr.car
            curr = curr.cdr

        if not (isinstance(curr, AtomNode) and curr.value == "nil"):
            raise NonListError(self)


class QuoteNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"


# Prepare but don't use yet
class LambdaNode(ASTNode):
    def __init__(self, params: list[str], body: ASTNode, env=None):
        self.params = params
        self.body = body
        self.env = env


__all__ = [
    "ASTNode",
    "AtomNode",
    "ConsNode",
    "QuoteNode"
]
