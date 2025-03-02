class ASTNode:
    def __repr__(self):
        return f"{self.__class__.__name__}()"


class AtomNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"


class ListNode(ASTNode):
    def __init__(self, elements):
        self.elements = elements      # Nodes

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.elements)})"


class ConsNode(ASTNode):
    def __init__(self, car: ASTNode, cdr: ASTNode):
        self.car = car    # left value
        self.cdr = cdr    # right value

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.car)}, {repr(self.cdr)})"


class QuoteNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

