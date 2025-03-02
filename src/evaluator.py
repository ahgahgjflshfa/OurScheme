from .ast_nodes import *


class Evaluator:
    def __init__(self, env):
        self.env = env

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
        if isinstance(node.value, (int, float, str)):
            return node.value

        elif node.value in self.env:    # user define variables or functions
            return self.env[node.value]

        else:
            raise RuntimeError(f"Undefined symbol: {node.value}")

    def _eval_list(self, node: ListNode):
        if not node.elements:
            raise RuntimeError("Cannot evaluate empty list.")

        first = node.elements[0]

        # First element is function call
        if isinstance(first, AtomNode) and first.value in self.env:
            func_name = first.value
            func = self.env[func_name]
            args = [self.eval(arg) for arg in node.elements[1:]]

            return func(*args)

        # First element is not function call, pure data list
        return ListNode([self.eval(el) for el in node.elements])

    def _eval_cons(self, node: ConsNode):
        car = self.eval(node.car)
        cdr = self.eval(node.cdr)

        # ✅ 如果 cdr 是 nil，應該轉成 ListNode([car])
        if isinstance(cdr, AtomNode) and cdr.value == "nil":
            return ListNode([car])

        # ✅ 如果 cdr 是 ListNode，轉成標準 Scheme List
        if isinstance(cdr, ListNode):
            return ListNode([car] + cdr.elements)

        # ✅ **確保 `car` 仍然是 Atom，不是 ListNode**
        return ConsNode(car, cdr)