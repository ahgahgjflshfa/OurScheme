from functools import partial

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
    lexer = Lexer()
    print("Welcome to OurScheme!")

    partial_input = ""  # 存儲多行輸入
    while True:
        try:
            new_input = input()  # 讀取新的一行
            if new_input.lower() == "(exit)":
                break

            partial_input += new_input + "\n"  # 🔥 儲存多行輸入
            lexer.reset(partial_input)
            parser = Parser(lexer)

            try:
                result = parser.parse()
                if isinstance(result, AtomNode) and result.type == "STRING":
                    print(f'\n> "{result.value}"')
                elif isinstance(result, ListNode) and not result.elements:
                    print("\n> nil")
                elif isinstance(result, AtomNode) and result.type == "FLOAT":
                    print(f"\n> {result.value:.3f}")
                else:
                    print(f"\n> {result}")

                partial_input = ""  # 🔥 解析成功後清空輸入

            except SyntaxError as e:
                if "Unexpected EOF" in str(e):
                    continue  # 🔥 繼續等待輸入（多行解析）
                print(f"\n> {e}")
                partial_input = ""  # 🔥 出錯後清空輸入

        except Exception as e:
            print(f"\n> {e}")
            partial_input = ""  # 🔥 出錯後清空輸入

    print("Thanks for using OurScheme!")


if __name__ == "__main__":
    n = input()
    repl()
    quit(0)