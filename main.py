from src.lexer import *
from src.parser import *
from src.evaluator import Evaluator

global_env = {
    "+": lambda *args: sum(args),
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y if y != 0 else RuntimeError("Division by zero"),
    "car": lambda pair: pair.car if isinstance(pair, ConsNode) else RuntimeError("car: not a pair"),
    "cdr": lambda pair: pair.cdr if isinstance(pair, ConsNode) else RuntimeError("cdr: not a pair"),
}

def repl():
    """Scheme REPL（讀取-解析-執行-輸出）"""
    while True:
        try:
            s_exp = input("> ")  # ✅ 讀取輸入
            if s_exp.lower() in ("exit", "quit"):
                break

            lexer = Lexer(s_exp)  # ✅ 進行詞法分析
            parser = Parser(lexer)  # ✅ 解析 AST
            ast_tree = parser.parse()

            evaluator = Evaluator(global_env)  # ✅ 創建 Evaluator
            result = evaluator.eval(ast_tree)  # ✅ 執行 AST

            print(result)  # ✅ 輸出結果

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    while 1:
        repl()