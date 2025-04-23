from src.ast_nodes import *
from src.errors import *
from src.errors import SchemeExitException
from src.evaluator import Evaluator
from src.lexer import Lexer
from src.parser import Parser
from src.pretty_print import pretty_print
from src.builtins_registry import built_in_funcs
from src.environment import Environment


def repl():
    lexer = Lexer()
    global_env = Environment(built_in_funcs)
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

            partial_input += new_input + "\n"  # add new line input

            lexer.reset(partial_input.rstrip("\n"))

            lexer.set_position(new_s_exp_start)

            parser = Parser(lexer)

            # Parsing
            first = True
            try:
                while parser.current.type != "EOF":  # Parse until lexer reached the end
                    if not first:
                        print("\n>", end=" ")

                    result = parser.parse()

                    first = False

                    new_s_exp_start = parser.last_s_exp_pos + 1

                    # Eval
                    try:
                        eval_result = evaluator.evaluate(result, global_env, "toplevel")
                        if isinstance(eval_result, AtomNode) and eval_result.type == "VOID":    # for verbose
                            continue
                        else:
                            print(f"{pretty_print(eval_result).lstrip('\n')}")

                    except (DefineFormatError, CondFormatError, LambdaFormatError, LetFormatError) as e:
                        print(f"{e} : {pretty_print(result)}")

                    except UnboundSymbolError as e:
                        print(f"{e} : {e.symbol}")

                    except IncorrectArgumentType as e:
                        print(f"{e} : {pretty_print(e.arg)}")

                    except NotCallableError as e:
                        print(f"{e} : {pretty_print(e.operator)}")

                    except (NonListError, NoReturnValue) as e:
                        print(f"{e} : {pretty_print(e.ast)}")

                    except DivisionByZeroError as e:
                        print(f"{e} : /")

                    except IncorrectArgumentNumber as e:
                        print(f"{e} : {e.operator}")

                    except (LevelDefineError, LevelCleanEnvError, LevelExitError) as e:
                        print(f"{e}")

                partial_input = ""  # after parsing, clear input
                new_s_exp_start = 0

            except NotFinishError:
                empty_line_encountered = True  # wait for user input, so do nothing
                continue

            except NoClosingQuoteError as e:
                print(f"{e} : END-OF-LINE encountered at Line {e.line} Column {e.column}")
                partial_input = ""
                new_s_exp_start = 0

            except UnexpectedTokenError as e:
                if e.type == 1:
                    print(f"{e} : atom or '(' expected when token at Line {e.line} Column {e.column} is >>{e.value}<<")
                else:
                    print(f"{e} : ')' expected when token at Line {e.line} Column {e.column} is >>{e.value}<<")

                partial_input = ""
                new_s_exp_start = 0

        except SchemeExitException:
            break

        except EmptyInputError:
            empty_line_encountered = True
            continue

        except EOFError:
            print("ERROR (no more input) : END-OF-FILE encountered", end="")
            break

        empty_line_encountered = False

    print("\nThanks for using OurScheme!", end="")
