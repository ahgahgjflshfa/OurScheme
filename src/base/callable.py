from src.errors import IncorrectArgumentNumber, IncorrectArgumentType
from src.ast_nodes import ASTNode, AtomNode, ConsNode

class CallableEntity:
    def __init__(self, name, func, min_args=None, max_args=None):
        self.name = name
        self.func = func
        self.min_args = min_args
        self.max_args = max_args

    def check_arity(self, args: list[ASTNode]):
        if self.min_args is not None and len(args) < self.min_args:
            raise IncorrectArgumentNumber(self.name)

        if self.max_args is not None and len(args) > self.max_args:
            raise IncorrectArgumentNumber(self.name)

    def __call__(self, *args, **kwargs):
        raise NotImplementedError(f"{self.__class__.__name__} must override __call__()")

    def __repr__(self, *args, **kwargs):
        raise NotImplementedError(f"{self.__class__.__name__} must override __repr__()")