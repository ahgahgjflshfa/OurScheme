from src.ast_nodes import *
from src.environment import Environment
from src.builtins_registry import built_in_funcs
from src.errors import NotCallableError, DefineFormatError, NonListError
from src.special_forms import SpecialForm


class Evaluator:
    def __init__(self, builtins: dict[str, object]=None, env: Environment=None):
        self.builtins = builtins if builtins is not None else built_in_funcs
        self.env = env if env is not None else Environment(self.builtins)

    def evaluate(self, ast: ASTNode, env: Environment=None):
        env = env if env is not None else self.env

        if isinstance(ast, AtomNode):
            if ast.type == "SYMBOL":
                return env.lookup(ast.value)
            else:
                return ast

        elif isinstance(ast, QuoteNode):
            return ast.value

        elif isinstance(ast, ConsNode):
            operator_node = ast.car
            operator = self.evaluate(operator_node, env)
            args = Evaluator.extract_list(ast)

            if isinstance(operator, SpecialForm):   # Special forms
                return self.apply_function(operator, args, env)
            else:   # Primitive functions
                evaluated_args = self.eval_list(args, env)
                return self.apply_function(operator, evaluated_args, env)

    @staticmethod
    def extract_list(cons_node: ConsNode) -> list[ASTNode]:
        args = []
        curr_ast = cons_node.cdr
        while isinstance(curr_ast, ConsNode):
            args.append(curr_ast.car)
            curr_ast = curr_ast.cdr

        if not (isinstance(curr_ast, AtomNode) and curr_ast.value == "nil"):
            raise NonListError(cons_node)

        return args

    def eval_list(self, args: list[ASTNode], env: Environment) -> list[ASTNode]:
        return [self.evaluate(arg, env) for arg in args]

    def apply_function(self, func, args, env) -> ASTNode:
        if hasattr(func, '__call__'):
            if isinstance(func, SpecialForm):
                return func(args, env, self)
            else:
                return func(args, env)

        raise NotCallableError(func)