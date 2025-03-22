import numpy as np


class NoClosingQuoteError(Exception):
    def __init__(self, msg_):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class NotFinishError(Exception):
    """讓parser等待多行輸入"""
    def __init__(self, msg_="S expression not complete"):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class EmptyInputError(Exception):
    """遇到註解或是整行空白用的"""
    def __init__(self, msg_):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class UnexpectedTokenError(Exception):
    def __init__(self, msg_):
        self.msg = msg_
        super().__init__(msg_)

    def __str__(self):
        return self.msg


class Token:
    def __init__(self, type_, value_, line_= 0, start_pos_ = 0, end_pos_ = 0):
        """

        :param type_:
        :param value_:
        :param line_:
        :param start_pos_: Token starting position
            (input[token_start_pos-1] 才是這個 token 的第一個字元，這是用來讓parser知道這個token在輸出中是第幾個字元，從1開始，不是0)
        :param end_pos_: End position is the token's last character position
            (input[token_end_pos-1] 才是這個 token 的最後一個字元，下一個不是)
        """
        # Note: String Token won't include `"` !
        self.type = type_
        self.value = value_
        self.line = line_
        self.start_pos = start_pos_ # Token starting position
                                    # (input[token_start_pos] 是這個 token 的第一個字元，上一個不是)
        self.end_pos = end_pos_     # End position is the token's last character position
                                    # (input[token_end_pos] 還是這個 token 的最後一個字元，下一個不是)

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value

        return False


class Lexer:
    def __init__(self):
        self.source_code = ""   # Store 1 line of user input in repl.
        self._position = 0      # Store current location.
        self._line_number = 1
        self._column_number = 1
        self._position_offset = 0  # 當前掃描區段在整個 source_code 的偏移量 

    @property
    def position(self):
        return self._position

    def reset(self, new_source_code):
        """Reset lexer status, let it tokenize new source code"""
        self.source_code = new_source_code # + "\n"
        self._position = 0
        self._line_number = 1
        self._column_number = 1

    def has_more_token(self) -> bool:
        """Check if lexer have more token

        :return: True if more token exist, else False.
        """
        return self._position < len(self.source_code)

    def peek(self):
        """Peek next character"""
        return self.source_code[self._position + 1] if self._position + 1 < len(self.source_code) else ""

    def peek_token(self):
        current_position = self._position
        token = self.next_token()
        self._position = current_position
        return token

    def set_position(self, pos: int):
        """
        將 Lexer 的掃描位置設為 pos，並將 pos 當作新的「Line 1 Column 1」起點。
        """
        self._position = pos
        self._line_number = 1
        self._column_number = 1

    def next_token(self):
        """Return next token from source code"""
        self._skip_whitespace_and_comments()

        if self._position >= len(self.source_code):
            return Token("EOF", None)

        char = self.source_code[self._position]

        if char in "()":
            return self._read_paren()

        elif char == "#":
            return self._read_symbol()

        elif char == "\'":
            return self._read_quote()

        elif char.isalpha():
            return self._read_symbol()

        elif char == "\"":
            return self._read_string()

        elif char in ("+", "-", "*", "/") and self.peek().isspace():   # function symbols
            return self._read_symbol()

        elif char == ".":
            peek = self.peek()
            if peek and (peek.isdigit() or peek in "eE"):
                return self._read_number_or_symbol()
            else:
                return self._read_dot()

        elif (char.isdigit() or
              (char in "+-" and (self.peek().isdigit() or self.peek() == "."))
        ):
            return self._read_number_or_symbol()

        else:
            return self._read_unknown()

    def _skip_whitespace_and_comments(self):
        """Skips whitespace and comments"""
        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char == "\n":
                self._line_number += 1
                self._column_number = 1
                self._position += 1

            elif char.isspace():  # whitespace
                self._column_number += 1
                self._position += 1

            elif char == ";":   # comments
                while self._position < len(self.source_code) and self.source_code[self._position] != "\n":
                    self._position += 1

            else:
                break

    def _read_string(self):
        """Read string token"""
        start_pos = self._column_number
        self._position += 1  # skip "
        self._column_number += 1
        result = ""

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if self.source_code[self.position] == "\"":
                end_pos = self._column_number   # 包含 "
                self._position += 1
                self._column_number += 1

                return Token("STRING", result, self._line_number, start_pos, end_pos)

            if char == "\\":
                self._position += 1
                self._column_number += 1

                if self.position >= len(self.source_code):
                    raise NoClosingQuoteError(
                        f"ERROR (no closing quote) : END-OF-LINE encountered at Line {self._line_number} Column {self._column_number}"
                    )

                if self.source_code[self._position] == "n":
                    result += "\n"
                elif self.source_code[self._position] == "t":
                    result += "\t"
                elif self.source_code[self._position] == "\"":
                    result += "\""
                elif self.source_code[self._position] == "\\":
                    result += "\\"
                else:
                    result += f"\\{self.source_code[self._position]}"

                self._position += 1
                self._column_number += 1
                continue

            result += char
            self._position += 1
            self._column_number += 1

        raise NoClosingQuoteError(
            f"ERROR (no closing quote) : END-OF-LINE encountered at Line {self._line_number} Column {self._column_number}"
        )

    def _read_number_or_symbol(self):
        """Read number token or symbol starting with a number"""
        start_pos = self._column_number
        number_str = ""

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char.isalnum() or char in ('.', '+', '-', 'e', 'E', '_'):
                number_str += char
                self._position += 1
                self._column_number += 1

            else:
                break


        end_pos = self._column_number - 1

        if "_" in number_str:
            return Token("SYMBOL", number_str, self._line_number, start_pos, end_pos)

        try:
            val = np.float64(number_str)
            if '.' in number_str or 'e' in number_str.lower():
                return Token("FLOAT", float(val), self._line_number, start_pos, end_pos)
            elif np.isclose(val, int(val)):
                return Token("INT", int(val), self._line_number, start_pos, end_pos)
            else:
                return Token("FLOAT", float(val), self._line_number, start_pos, end_pos)

        except ValueError:
            return Token("SYMBOL", number_str, self._line_number, start_pos, end_pos)

    def _read_symbol(self):
        """Read symbol token (variable names, function names)"""
        start_pos = self._column_number
        symbol = ""

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char.isalnum() or char in "+-*/_!?.#":   # TODO: check legal characters
                symbol += char
                self._position += 1
                self._column_number += 1

            elif char == "\n":
                break

            else:
                break

        end_pos = self._column_number - 1

        if symbol == "t":
            return Token("T", "#t", self._line_number, start_pos, end_pos)
        elif symbol == "nil":
            return Token("NIL", "nil", self._line_number, start_pos, end_pos)
        elif symbol == "#t":
            return Token("T", "#t", self._line_number, start_pos, end_pos)
        elif symbol == "#f":
            return Token("NIL", "nil", self._line_number, start_pos, end_pos)

        return Token("SYMBOL", symbol, self._line_number, start_pos, end_pos)

    def _read_dot(self):
        """Read DOT (.)"""
        dot_pos = self._column_number
        self._position += 1
        self._column_number += 1

        return Token("DOT", ".", self._line_number, dot_pos, dot_pos)

    def _read_quote(self):
        """Read quote"""
        quote_pos = self._column_number
        self._position += 1
        self._column_number += 1

        return Token("QUOTE", "quote", self._line_number, quote_pos, quote_pos)

    def _read_paren(self):
        """Read parenthesis"""
        char = self.source_code[self._position]
        paren_pos = self._column_number
        self._position += 1
        self._column_number += 1

        if char == "(":
            return Token("LEFT_PAREN", "(", self._line_number, paren_pos, paren_pos)
        else:
            return Token("RIGHT_PAREN", ")", self._line_number, paren_pos, paren_pos)

    def _read_unknown(self):
        start_pos = self._column_number
        unknown_str = ""

        while self._position < len(self.source_code):
            char = self.source_code[self._position]

            if char.isspace() or char in "()":
                break

            unknown_str += char
            self._position += 1
            self._column_number += 1

        end_pos = self._column_number - 1

        return Token("UNKNOWN", unknown_str, self._line_number, start_pos, end_pos)


class ASTNode:
    def __eq__(self, other):
        return isinstance(other, self.__class__) and vars(self) == vars(other)

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class AtomNode(ASTNode):
    def __init__(self, type_, value):
        self.type = type_   # "INT", "FLOAT", "SYMBOL", "BOOLEAN"
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type}, {repr(self.value)})"


class ConsNode(ASTNode):
    def __init__(self, car: list[ASTNode], cdr: ASTNode = None):
        self.car = car  # a list of ASTNode
        self.cdr = cdr  # cdr 可以是 ASTNode 或 None

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.car)}, {repr(self.cdr)})"


class QuoteNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self._current_token = self.lexer.next_token()

        self._current_s_exp_start_pos = 0   # 記錄當前 S-Expression 的起始 column  ( 以 list 元素編號 )
        self._last_token_end_pos = 0        # 紀錄最新一個 consume_token 消耗掉的 token 在 source code 中的位置 也是以 list 元素編號

        if self._current_token.type == "EOF":   # supposedly only empty line or a line starting with comment will encounter
            raise EmptyInputError(f"EOF encountered")

    @property
    def current(self):
        return self._current_token

    @property
    def last_s_exp_pos(self):
        """其實回傳的參數是parser中紀錄上一個token的position，
        但如果在parser剛好解析完一個完整的s exp之後呼叫的話，回傳上一個token的結束位置其實就是上一個s exp的結束位置
        """
        return  self._last_token_end_pos

    def parse(self):
        """Entry point of parser"""
        ast = self._parse_s_exp()

        self._current_s_exp_start_pos = self._last_token_end_pos

        return ast

    def _consume_token(self) -> Token:
        token = self._current_token

        self._last_token_end_pos = sum(map(len, self.lexer.source_code.split("\n")[:token.line - 1])) + token.end_pos

        self._current_token = self.lexer.next_token()
        return token

    def _convert_to_cons(self, elements, cdr):
        if not elements:
            return AtomNode("BOOLEAN", "nil")

        result = cdr if cdr else AtomNode("BOOLEAN", "nil")

        for elem in reversed(elements):
            result = ConsNode(elem, result)

        return result

    def _parse_s_exp(self) -> ASTNode | None:
        """Parse a single S-expression"""
        token = self._consume_token()

        if token.type in ("SYMBOL", "INT", "FLOAT", "STRING", "NIL", "T", "UNKNOWN"):
            return self._parse_atom(token)

        elif token.type == "QUOTE":
            return self._parse_quote()

        elif token.type == "LEFT_PAREN":
            if self._current_token.type == "RIGHT_PAREN":
                self._consume_token()   # consume right parenthesis
                return AtomNode("BOOLEAN", "nil")

            return self._parse_list()

        elif token.type == "DOT":
            pos = (sum(map(len, self.lexer.source_code.split("\n")[:token.line - 1])) + token.end_pos
                   - self._current_s_exp_start_pos)
            value = token.value

            raise UnexpectedTokenError(
                f"ERROR (unexpected token) : atom or '(' expected when token at Line {1} Column {pos} is >>{value}<<"
            )

        elif token.type == "RIGHT_PAREN":
            pos = (sum(map(len, self.lexer.source_code.split("\n")[:token.line - 1])) + token.end_pos
                   - self._current_s_exp_start_pos)
            value = token.value

            raise UnexpectedTokenError(
                f"ERROR (unexpected token) : atom or '(' expected when token at Line {1} Column {pos} is >>{value}<<"
            )

    def _parse_list(self) -> ASTNode:
        """Parse an S-Expression list"""
        elements = []

        while self._current_token.type not in ("RIGHT_PAREN", "EOF"):
            if self._current_token.type == "DOT":   # 如果遇到 `.`，要轉換成統一的 cons node 結構 e.g. (1 2 . 3) => (1 . (2 . 3))
                if not elements:
                    line = self._current_token.line
                    pos = self._current_token.start_pos
                    value = self._current_token.value

                    raise UnexpectedTokenError(
                        f"ERROR (unexpected token) : atom or '(' expected when token at Line {line} Column {pos} is >>{value}<<"
                    )

                self._consume_token()  # skip `.`

                if self._current_token.type == "RIGHT_PAREN":  # Cons Node 不能沒有 cdr
                    line = self._current_token.line
                    pos = self._current_token.start_pos
                    value = self._current_token.value

                    raise UnexpectedTokenError(
                        f"ERROR (unexpected token) : atom or '(' expected when token at Line {line} Column {pos} is >>{value}<<"
                    )

                elif self._current_token.type == "EOF":
                    # 告訴 parser 和 repl 等待用戶輸入剩下的部分
                    raise NotFinishError("Unexpected EOF while parsing list.")  # 讓 `repl()` 繼續等待輸入

                cdr = self._parse_s_exp()   # 解析 cdr

                token = self._consume_token()
                if token.type == "EOF":   # 沒輸入完
                    # 告訴 parser 和 repl 等待用戶輸入剩下的部分
                    raise NotFinishError("Unexpected EOF while parsing list.")  # 讓 `repl()` 繼續等待輸入

                elif token.type != "RIGHT_PAREN":
                    line = token.line

                    pos = token.start_pos

                    value = token.value

                    raise UnexpectedTokenError(f"ERROR (unexpected token) : ')' expected when token at Line {line} Column {pos} is >>{value}<<")

                return self._convert_to_cons(elements, cdr) # 轉換成統一格式

            elements.append(self._parse_s_exp())

        if self._current_token.type == "EOF":
            raise NotFinishError("Unexpected EOF while parsing list.")  # 讓 `repl()` 繼續等待輸入

        self._consume_token()  # consume `)`

        # 統一用 Cons Node 表達 (1 2 3) => (1 . (2 . (3 .nil)))
        return self._convert_to_cons(elements, AtomNode("BOOLEAN", "nil"))

    def _parse_quote(self) -> ASTNode:
        if self._current_token.type == "EOF":
            raise NotFinishError("Unexpected EOF while parsing list.")

        return QuoteNode(self._parse_s_exp())  # Consume and parse quoted expression

    def _parse_atom(self, token: Token) -> ASTNode:
        """Parse atom and preserve type information"""
        if token.type in ("INT", "FLOAT", "SYMBOL", "STRING", "UNKNOWN"):
            return AtomNode(token.type, token.value)

        elif token.type == "T":  # #t
            return AtomNode("BOOLEAN", "#t")

        elif token.type == "NIL":  # #f
            return AtomNode("BOOLEAN", "nil")

        raise SyntaxError(f"Unexpected atom type: {token.type}")


def pretty_print(node, indent=0):
    """格式化 Pretty Print 輸出 Scheme AST，確保排版嚴格符合要求"""
    indent_str = "  " * indent  # 當前縮排
    next_indent_str = "  " * (indent + 1)  # 下一層縮排

    if isinstance(node, AtomNode):
        """處理基本類型 (數字、布林值、符號、字串)"""
        if node.type == "STRING":
            return f'"{node.value}"'
        elif node.type == "FLOAT":
            return f"{node.value:.3f}"
        else:
            return f"{node.value}"

    elif isinstance(node, ConsNode):
        elements = []
        current = node

        while isinstance(current, ConsNode):    # 從最裡面開始，要轉換成等價的Cons ( ssp . sp )
            elements.append(current.car)     # car 是一個 list，所以是要用 concat 的方式
            current = current.cdr

        # 如果 `cdr` 最終是 `nil`，則轉換成 ListNode 格式
        if isinstance(current, AtomNode) and current.value == "nil":    # ( ssp . nil ) === ( sp1 sp2 sp3 ... spn )
            result = f"( {pretty_print(elements[0], indent + 1)}"

            for elem in elements[1:]:
                result += f"\n{next_indent_str}{pretty_print(elem, indent + 1)}"

            result += f"\n{indent_str})"
            return result

        result = f"( {pretty_print(elements[0], indent + 1)}"
        for element in elements[1:]:
            result += f"\n{next_indent_str}{pretty_print(element, indent + 1)}"

        # `.` 必須獨立一行
        result += f"\n{next_indent_str}."

        # `cdr` 部分處理
        result += f"\n{next_indent_str}{pretty_print(current, indent + 1)}"

        result += f"\n{indent_str})"
        return result

    elif isinstance(node, QuoteNode):
        """處理 `quote` 內部的 ListNode，確保 `(` 與 `quote` 的 `q` 對齊"""
        result = f"{indent_str}( quote"

        result += f"\n{next_indent_str}{pretty_print(node.value, indent + 1)}"

        result += f"\n{indent_str})"
        return result

    return f"{indent_str}UNKNOWN_NODE"


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
                    result = parser.parse()

                    new_s_exp_start = parser.last_s_exp_pos + 1

                    # 檢查 `(exit)` 是否是獨立的 S-Expression
                    if isinstance(result, ConsNode):
                        if isinstance(result.car, AtomNode) and result.car.value == "exit":
                            print("\n> \nThanks for using OurScheme!")
                            return

                    print("\n> " + pretty_print(result).lstrip("\n"))

                partial_input = ""  # 解析成功後清空輸入
                new_s_exp_start = 0

            except NotFinishError as e:
                pass    # 讓 repl 等待下一行用戶輸入

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
