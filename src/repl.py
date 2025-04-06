from src.errors import *
from src.ast_nodes import *
from src.lexer import Lexer
from src.parser import Parser
from src.pretty_print import pretty_print
from src.evaluator import Evaluator


def repl():
    lexer = Lexer()
    evaluator = Evaluator()
    print("Welcome to OurScheme!")

    empty_line_encountered = False

    partial_input = ""  # for multiline input
    new_s_exp_start = 0
    while True:
        try:
            if not empty_line_encountered:
                print("\n>", end=" ")

            new_input = input()  # read new input
            if new_input.lower() == "(exit)":
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
                            print("\nThanks for using OurScheme!")
                            return

                    # Eval
                    try:
                        eval_result = evaluator.evaluate(result)

                        # 特判 define，輸出 "x defined"
                        if (isinstance(result, ConsNode) and
                                isinstance(result.car, AtomNode) and result.car.value == "define" and
                                isinstance(result.cdr, ConsNode) and
                                isinstance(result.cdr.car, AtomNode)):

                            var_name = result.cdr.car.value
                            print(f"{var_name} defined")

                        else:
                            print(f"{pretty_print(eval_result).lstrip('\n')}")

                    except DefineFormatError as e:
                        print(f"{e} : {pretty_print(result)}")

                    except UnboundSymbolError as e:
                        print(f"{e} : {e.symbol}")

                    except IncorrectArgumentType as e:
                        print(f"{e} : {pretty_print(e.arg)}")

                    except NotCallableError as e:
                        print(f"{e} : {pretty_print(e.operator)}")

                    except NonListError as e:
                        print(f"{e} : {pretty_print(e.ast)}")

                    except DivisionByZeroError as e:
                        print(f"{e} : /")

                    except IncorrectArgumentNumber as e:
                        print(f"{e} : {e.operator}")

                partial_input = ""  # after parsing, clear input
                new_s_exp_start = 0

            except NotFinishError:
                empty_line_encountered = True   # wait for user input, so do nothing
                continue

            except NoClosingQuoteError as e:
                print(f"{e} : END-OF-LINE encountered at Line {e.line} Column {e.column}")
                partial_input = ""
                new_s_exp_start = 0

            except UnexpectedTokenError as e:
                if e.value in (".", ")"):
                    print(f"{e} : atom or '(' expected when token at Line {e.line} Column {e.column} is >>{e.value}<<")
                else:
                    print(f"{e} : ')' expected when token at Line {e.line} Column {e.column} is >>{e.value}<<")

                partial_input = ""
                new_s_exp_start = 0

        except EmptyInputError:
            empty_line_encountered = True
            continue

        except EOFError:
            print("ERROR (no more input) : END-OF-FILE encountered")
            break

        empty_line_encountered = False

    print("Thanks for using OurScheme!", end="")