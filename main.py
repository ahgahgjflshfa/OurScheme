from src.parser import *
from src.pretty_print import *

def repl():
    lexer = Lexer()
    print("Welcome to OurScheme!")

    partial_input = ""  # 存儲多行輸入
    new_s_exp_start = 0
    while True:
        try:
            new_input = input()  # 讀取新的一行
            if new_input.lower() == "(exit)":
                print("\n> ")
                break

            partial_input += new_input + "\n"  # 儲存多行輸入

            lexer.reset(partial_input.rstrip("\n"))

            lexer.set_position(new_s_exp_start)

            parser = Parser(lexer)

            if parser.lexer_error:
                raise parser.lexer_error

            try:
                while parser.current.type != "EOF":
                    result = parser.parse()

                    new_s_exp_start = parser.last_s_exp_pos + 1

                    # 檢查 `(exit)` 是否是獨立的 S-Expression
                    if isinstance(result, ConsNode):
                        if ((isinstance(result.car, AtomNode) and result.car.type == "SYMBOL" and result.car.value == "exit") and
                                (isinstance(result.cdr, AtomNode) and result.cdr.type == "BOOLEAN" and result.cdr.value == "nil")):
                            print("\n> \nThanks for using OurScheme!")
                            return

                    print("\n> " + pretty_print(result).lstrip("\n"))

                    if parser.lexer_error:
                        raise parser.lexer_error

                partial_input = ""  # 解析成功後清空輸入
                new_s_exp_start = 0

            except NotFinishError as e:
                if parser.lexer_error:
                    raise parser.lexer_error

            except UnexpectedTokenError as e:
                # e.g. no closing quote ...
                print(f"\n> {e}")
                partial_input = ""
                new_s_exp_start = 0

        except EmptyInputError:
            continue

        except NoClosingQuoteError as e:
            print(f"\n> {e}")
            partial_input = ""
            new_s_exp_start = 0

        except EOFError:
            print("\n> ERROR (no more input) : END-OF-FILE encountered")
            break

    print("Thanks for using OurScheme!", end="")


if __name__ == "__main__":
    n = input()
    repl()
