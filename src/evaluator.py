from src.ast_nodes import *
from src.builtins_registry import built_in_funcs
from src.environment import Environment
from src.errors import (NotCallableError, NonListError, LevelDefineError,
                        LevelCleanEnvError, LevelExitError, NoReturnValue, LambdaFormatError, IncorrectArgumentNumber,
                        UnboundParameterError)
from src.function_object import SpecialForm, PrimitiveFunction, UserDefinedFunction
from src.special_forms import eval_lambda
from src.parser import Parser


class Evaluator:
    def __init__(self, global_env: Environment, parser: Parser, builtins: dict[str, object]=None, verbose: bool=True):
        self.global_env = global_env
        self.parser = parser
        self.builtins = builtins if builtins is not None else built_in_funcs
        self.verbose = verbose

    def evaluate(self, ast: ASTNode, env: Environment, level: str):
        if isinstance(ast, AtomNode):
            if ast.type == "SYMBOL":
                return env.lookup(ast.value)
            else:
                return ast

        elif isinstance(ast, QuoteNode):
            return ast.value

        elif isinstance(ast, ConsNode):
            return self._process_cons(ast, env, level)

        raise NotImplementedError(f"Unhandled AST node: {ast}")

    def _process_cons(self, ast, env, level):
        first = ast.car

        result = self._handle_verbose(ast, env)
        if result is not None:
            return result

        # === Special form based constructions ===
        if first == AtomNode("SYMBOL", "lambda"):
            if not isinstance(ast.cdr , ConsNode):
                raise LambdaFormatError()

            return eval_lambda(ast.cdr, env)

        # === Others ===
        func = self.evaluate(first, env, "inner")
        if func is None:
            raise NoReturnValue(first)

        args = Evaluator.extract_list(ast.cdr)
        if args is None:
            raise NonListError(ast)

        if not isinstance(func, (PrimitiveFunction, SpecialForm, UserDefinedFunction)):
            raise NotCallableError(func)

        self._handle_level_error(func, level)

        func.check_arity(args)

        if isinstance(func, (SpecialForm, )):   # Special forms
            eval_result = func(args, env, self)
        else:  # Primitive functions
            evaluated_args = self.eval_list(args, env)
            eval_result = func(evaluated_args, env, self)

        return eval_result

    def _handle_level_error(self, func, level):
        if func is self.builtins["define"] and level != "toplevel":
            raise LevelDefineError()
        elif func is self.builtins["clean-environment"] and level != "toplevel":
            raise LevelCleanEnvError()
        elif func is self.builtins["exit"] and level != "toplevel":
            raise LevelExitError()

    def _handle_verbose(self, ast, env):
        first = ast.car

        # === Verbose Setting ===
        if first == AtomNode("SYMBOL", "verbose"):
            args = Evaluator.extract_list(ast.cdr)
            if len(args) != 1:
                raise IncorrectArgumentNumber("verbose")

            value = self.evaluate(args[0], env, "inner")
            self.verbose = True if value != AtomNode("BOOLEAN", "nil") else False
            return AtomNode("BOOLEAN", "#t" if value != AtomNode("BOOLEAN", "nil") else "nil")

        if first == AtomNode("SYMBOL", "verbose?"):
            args = Evaluator.extract_list(ast.cdr)
            if len(args) != 0:
                raise IncorrectArgumentNumber("verbose")

            return AtomNode("BOOLEAN", "#t") if self.verbose else AtomNode("BOOLEAN", "nil")

        return None

    @staticmethod
    def extract_list(cons_node: ASTNode) -> list[ASTNode] | None:
        args = []
        curr_ast = cons_node
        while isinstance(curr_ast, ConsNode):
            args.append(curr_ast.car)
            curr_ast = curr_ast.cdr

        if not (isinstance(curr_ast, AtomNode) and curr_ast.value == "nil"):
           return None

        return args

    def eval_list(self, args: list[ASTNode], env: Environment) -> list[ASTNode]:
        evaled_args = []

        for arg in args:
            evaled = self.evaluate(arg, env, "inner")
            if evaled is None:
                raise UnboundParameterError(arg)

            evaled_args.append(evaled)

        return evaled_args
