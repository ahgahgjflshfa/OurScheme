from .ast_nodes import *


class Evaluator:
    def __init__(self, env=None):
        self.env = env if env is not None else {}

    def eval(self, node: ASTNode):
        if isinstance(node, AtomNode):
            return self._eval_atom(node)

        elif isinstance(node, ListNode):
            return self._eval_list(node)

        elif isinstance(node, ConsNode):
            return self._eval_cons(node)

        elif isinstance(node, QuoteNode):
            return node.value

        else:
            raise RuntimeError(f"Unknown AST node: {node}")

    def _eval_atom(self, node: AtomNode):
        if node.type in ("INT", "FLOAT", "STRING", "BOOLEAN"):
            return node.value

        elif node.type == "SYMBOL" and node.value in self.env:
            return self.env[node.value]

        raise RuntimeError(f"Undefined symbol: {node.value}")

    def _eval_list(self, node: ListNode):
        if not node.elements:
            raise RuntimeError("Cannot evaluate empty list.")

        first = node.elements[0]

        # (define x 10)
        if isinstance(first, AtomNode) and first.value == "define":
            if len(node.elements) != 3:
                raise RuntimeError("define expects 2 arguments: (define name value)")
            _, name, value = node.elements
            if not isinstance(name, AtomNode) or name.type != "SYMBOL":
                raise RuntimeError("define expects a symbol as the first argument")

            self.env[name.value] = self.eval(value)
            return None  # define 不應該回傳值

        # 一般函數呼叫
        if isinstance(first, AtomNode) and first.value in self.env:
            func = self.env[first.value]
            args = [self.eval(arg) for arg in node.elements[1:]]
            return func(*args)

        return ListNode([self.eval(el) for el in node.elements])

    def _eval_cons(self, node: ConsNode):
        car = self.eval(node.car)
        cdr = self.eval(node.cdr)

        if isinstance(cdr, ListNode):
            return ListNode([car] + cdr.elements)

        return ConsNode(car, cdr)
