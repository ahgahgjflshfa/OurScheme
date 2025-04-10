from src.ast_nodes import *
from src.base.callable import CallableEntity
from src.builtins_registry import built_in_funcs
from src.environment import Environment
from src.errors import NotCallableError, NonListError, DefineLevelError, CleanEnvLevelError
from src.special_forms import SpecialForm


class Evaluator:
    def __init__(self, builtins: dict[str, object] = None, env: Environment = None):
        self.builtins = builtins if builtins is not None else built_in_funcs
        self.env = env if env is not None else Environment(self.builtins)

    def evaluate(self, ast: ASTNode, env: Environment = None, level: str = "toplevel"):
        env = env if env is not None else self.env

        if isinstance(ast, AtomNode):
            if ast.type == "SYMBOL":
                return env.lookup(ast.value)
            else:
                return ast

        elif isinstance(ast, QuoteNode):
            return ast.value

        elif isinstance(ast, ConsNode):
            func = self.evaluate(ast.car, env)
            args = Evaluator.extract_list(ast)

            if not isinstance(func, CallableEntity):
                raise NotCallableError(func)

            func.check_arity(args)

            if func is self.builtins["define"] and level != "toplevel":
                raise DefineLevelError()
            elif func is self.builtins["clean-environment"] and level != "toplevel":
                raise CleanEnvLevelError()


            if isinstance(func, SpecialForm):   # Special forms
                return func(args, env, self)
            else:  # Primitive functions
                evaluated_args = self.eval_list(args, env)
                return func(evaluated_args, env)

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
