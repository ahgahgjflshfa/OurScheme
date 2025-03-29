from src.errors import *
from src.ast_nodes import *
from src.lexer import Lexer
from src.parser import Parser
from src.pretty_print import pretty_print
from src.evaluator import evaluate


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

            try:
                while parser.current.type != "EOF":
                    # Parse
                    result = parser.parse()

                    new_s_exp_start = parser.last_s_exp_pos + 1

                    # 檢查 `(exit)` 是否是獨立的 S-Expression
                    if isinstance(result, ConsNode):
                        if ((isinstance(result.car, AtomNode) and result.car.type == "SYMBOL" and result.car.value == "exit") and
                                (isinstance(result.cdr, AtomNode) and result.cdr.type == "BOOLEAN" and result.cdr.value == "nil")):
                            print("\n> \nThanks for using OurScheme!")
                            return

                    # print("\n> " + pretty_print(result).lstrip("\n"))

                    # Eval
                    try:
                        eval_result = evaluate(result)
                        print(f"\n> {pretty_print(eval_result).lstrip("\n")}")

                    except DefineError as e:
                        print(f"\n> {str(e)} : {pretty_print(result)}")

                    except UnboundSymbolError as e:
                        print(f"\n> {str(e)} : {e.symbol}")

                    except IncorrectArgumentType as e:
                        print(f"\n> {str(e)} : {pretty_print(e.arg)}")

                    except NotCallableError as e:
                        print(f"\n> {str(e)} : {pretty_print(e.operator)}")

                    except NonListError as e:
                        print(f"\n> {str(e)} : {pretty_print(result)}")

                partial_input = ""  # 解析成功後清空輸入
                new_s_exp_start = 0

            except NotFinishError:
                pass

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