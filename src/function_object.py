from src.ast_nodes import *
from src.errors import IncorrectArgumentType, IncorrectArgumentNumber, UnboundParameterError
from src.base.callable import CallableEntity
from src.environment import Environment


class PrimitiveFunction(CallableEntity):
    def __init__(self, name, func, min_args=None, max_args=None, arg_types=None):
        self.name = name
        self.func = func
        self.min_args = min_args
        self.max_args = max_args
        self.arg_types = arg_types

    def check_arity(self, args: list[ASTNode]):
        if self.min_args is not None and len(args) < self.min_args:
            raise IncorrectArgumentNumber(self.name)

        if self.max_args is not None and len(args) > self.max_args:
            raise IncorrectArgumentNumber(self.name)

    def check_arg_types(self, args: list[ASTNode]):
        if not self.arg_types:
            return

        for i, arg in enumerate(args):
            # 如果 arg_types 是單一類型集合，套用到所有參數
            if isinstance(self.arg_types, (tuple, set)):
                valid_types = self.arg_types
            elif isinstance(self.arg_types, list):
                if i >= len(self.arg_types):
                    break  # 超過定義不檢查

                expected_type = self.arg_types[i]
                valid_types = (expected_type,)

            # 開始比對類型
            if not self._is_type_valid(arg, valid_types):
                raise IncorrectArgumentType(self.name, arg)

    def _is_type_valid(self, arg, expected_types):
        # atom 型別對應
        if isinstance(expected_types, str):
            expected_types = (expected_types,)

        for t in expected_types:
            if t == "any":
                return True
            elif t == "pair":
                if isinstance(arg, ConsNode):
                    return True
            elif isinstance(arg, AtomNode) and arg.type == t:
                return True
        return False

    def __call__(self, args: list[ASTNode], env: "Environment", evaluator: "Evaluator"):
        self.check_arg_types(args)
        return self.func(args, env, evaluator)

    def __repr__(self):
        return f"#<procedure {self.name}>"


class SpecialForm(CallableEntity):
    def __init__(self, name, func, min_args, max_args):
        self.name = name
        self.func = func
        self.min_args = min_args
        self.max_args = max_args

    def check_arity(self, args: list[ASTNode]):
        if self.min_args is not None and len(args) < self.min_args:
            raise IncorrectArgumentNumber(self.name)

        if self.max_args is not None and len(args) > self.max_args:
            raise IncorrectArgumentNumber(self.name)

    def __call__(self, args, env, evaluator):
        return self.func(args, env, evaluator)

    def __repr__(self):
        return f"#<procedure {self.name}>"


class UserDefinedFunction(CallableEntity):
    def __init__(self, name, param_list: list[str], body: list[ASTNode], env: "Environment"):
        self.name = name
        self.param_list = param_list
        self.body = body
        self.env = env      # closure

    @staticmethod
    def deepcopy(env: Environment):
        """避免外界影響裡邊，但好像project就要影響"""
        closure = Environment(builtins=env.builtins, outer=env.outer)

        for symbol, value in env.user_define.items():
            closure.define(symbol, value)

        return closure

    def check_arity(self, args: list[ASTNode]):
        if len(self.param_list) != len(args):
            raise IncorrectArgumentNumber("lambda")

    def __call__(self, args: list[ASTNode], call_site_env: Environment, evaluator: "Evaluator"):
        if len(self.param_list) != len(args):
            raise IncorrectArgumentNumber("lambda")

        call_env = Environment(builtins=self.env.builtins, outer=self.env)
        for param, value in zip(self.param_list, args):
            evaled_value = evaluator.evaluate(value, call_site_env, "inner")

            if evaled_value is None:
                raise UnboundParameterError(value)

            call_env.define(param, evaled_value)

        for expr in self.body[:-1]:
            evaluator.evaluate(expr, call_env, "inner")

        return evaluator.evaluate(self.body[-1], call_env, "inner")

    def __repr__(self):
        return f"#<procedure {self.name}>"


class DummySymbolReference(CallableEntity):
    """Just a dummy"""
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        raise NotImplementedError(f"Symbol '{self.name}' is not callable")

    def __repr__(self):
        return f"#<procedure {self.name}>"


__all__ = [
    "PrimitiveFunction",
    "SpecialForm",
    "UserDefinedFunction",
    "DummySymbolReference"
]