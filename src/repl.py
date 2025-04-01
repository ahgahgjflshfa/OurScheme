from src.errors import *
from src.ast_nodes import *
from src.lexer import Lexer
from src.parser import Parser
from src.pretty_print import pretty_print
from src.evaluator import evaluate


def repl():
    lexer = Lexer()
    print("Welcome to OurScheme!")

    partial_input = ""  # for multiline input
    new_s_exp_start = 0
    while True:
        try:
            new_input = input()  # read new input
            if new_input.lower() == "(exit)":
                print("\n> ")
                break

            partial_input += new_input + "\n"  # add new line input

            lexer.reset(partial_input.rstrip("\n"))

            lexer.set_position(new_s_exp_start)

            parser = Parser(lexer)

            # Parsing
            try:
                while parser.current.type != "EOF": # Parse until lexer reached the end
                    result = parser.parse()

                    new_s_exp_start = parser.last_s_exp_pos + 1

                    # check if (exit) are an independent s exp
                    if isinstance(result, ConsNode):
                        if ((isinstance(result.car, AtomNode) and result.car.type == "SYMBOL" and result.car.value == "exit") and
                                (isinstance(result.cdr, AtomNode) and result.cdr.type == "BOOLEAN" and result.cdr.value == "nil")):
                            print("\n> \nThanks for using OurScheme!")
                            return

                    # Eval
                    try:
                        eval_result = evaluate(result)

                        # 特判 define，輸出 "x defined"
                        if (isinstance(result, ConsNode) and
                                isinstance(result.car, AtomNode) and result.car.value == "define" and
                                isinstance(result.cdr, ConsNode) and
                                isinstance(result.cdr.car, AtomNode)):

                            var_name = result.cdr.car.value
                            print(f"\n> {var_name} defined")

                        else:
                            print(f"\n> {pretty_print(eval_result).lstrip('\n')}")

                    except DefineFormatError as e:
                        print(f"\n> {str(e)} : {pretty_print(result)}")

                    except UnboundSymbolError as e:
                        print(f"\n> {str(e)} : {e.symbol}")

                    except IncorrectArgumentType as e:
                        print(f"\n> {str(e)} : {pretty_print(e.arg)}")

                    except NotCallableError as e:
                        print(f"\n> {str(e)} : {pretty_print(e.operator)}")

                    except NonListError as e:
                        print(f"\n> {str(e)} : {pretty_print(e.ast)}")

                    except DivisionByZeroError as e:
                        print(f"\n> {str(e)} : /")

                    except IncorrectArgumentNumber as e:
                        print(f"\n> {str(e)} : {e.operator}")

                partial_input = ""  # after parsing, clear input
                new_s_exp_start = 0

            except NotFinishError:
                pass    # wait for user input, so do nothing

            except (UnexpectedTokenError, NoClosingQuoteError) as e:
                print(f"\n> {e}")
                partial_input = ""
                new_s_exp_start = 0

        except EmptyInputError:
            continue

        except EOFError:
            print("\n> ERROR (no more input) : END-OF-FILE encountered")
            break

    print("Thanks for using OurScheme!", end="")