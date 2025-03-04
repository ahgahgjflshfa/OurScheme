from src.lexer import *
from src.parser import *
from src.evaluator import Evaluator

global_env = {
    "+": lambda *args: sum(args),
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y if y != 0 else RuntimeError("Division by zero"),
    "car": lambda pair: pair.car if isinstance(pair, ListNode) else RuntimeError("car: not a pair"),
    "cdr": lambda pair: pair.cdr if isinstance(pair, ListNode) else RuntimeError("cdr: not a pair"),
}

def repl():
    """Scheme REPL（讀取-解析-執行-輸出）"""
    while True:
        try:
            s_exp = input("> ")
            if s_exp.lower() in ("exit", "quit"):
                break

            lexer = Lexer(s_exp)
            parser = Parser(lexer)
            ast_tree = parser.parse()

            print(ast_tree)

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    while 1:
        repl()