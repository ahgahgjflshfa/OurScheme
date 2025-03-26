from .lexer import *
from .ast_nodes import *
from .errors import *

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self._current_s_exp_start_pos = 0  # 記錄當前 S-Expression 的起始 column  ( 以 list 元素編號 )
        self._last_token_end_pos = -1  # 紀錄最新一個 consume_token 消耗掉的 token 在 source code 中的位置 也是以 list 元素編號
                                      # 所以 source_code[last_token_end_pos]還是舊的那個token，下一個才不是

        self._lexer_error = None  # 用來記錄 lexer 拋出的錯誤 ( 如果有 最好不要有 問題一堆 去你的 )

        try:
            self._current_token = self.lexer.next_token()

        except NoClosingQuoteError:
            self._handle_lexer_error()

        if self._current_token.type == "EOF" and self._lexer_error is None:
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

    @property
    def lexer_error(self):
        return self._lexer_error

    def parse(self) -> ASTNode:
        """Entry point of parser"""
        ast = self._parse_s_exp()

        self._current_s_exp_start_pos = self._last_token_end_pos + 1

        return ast

    def _handle_lexer_error(self):
        global_pos = self.lexer.position
        s_exp_start = self._last_token_end_pos + 1  # 包含
        column = 1
        for c in self.lexer.source_code[s_exp_start:global_pos]:
            if c == '\n':
                column = 1
            else:
                column += 1

        line = self.lexer.line


        self._lexer_error = NoClosingQuoteError(
            f"ERROR (no closing quote) : END-OF-LINE encountered at Line {line} Column {column}"
        )
        self._current_token = Token("EOF", None)

    def _consume_token(self) -> Token:
        token = self._current_token

        # TODO: 不知道如果是字串中的換行字元會不會有影響，如果是 list or cons 中有字串包含換行可能就會有問題
        self._last_token_end_pos = (
                sum(map(len, self.lexer.source_code.split("\n")[:token.line - 1]))  # 所有前面行的字元數
                + len(self.lexer.source_code.split("\n")[:token.line - 1])          # 每一行的一個 '\n'（換行補償）
                + (token.end_pos - 1)                                               # token 在當前行的結束 column（從 1 開始 → 減 1）
        )

        try:
            self._current_token = self.lexer.next_token()

        except NoClosingQuoteError:
            self._handle_lexer_error()

        return token

    def _convert_to_cons(self, elements: list, cdr: ASTNode) -> ASTNode:
        if not elements:
            return AtomNode("BOOLEAN", "nil")

        result = cdr if cdr else AtomNode("BOOLEAN", "nil")

        for elem in reversed(elements):
            result = ConsNode(elem, result)

        return result

    def _relative_token_position(self, token: Token):
        """給定 token，計算相對於 current s-exp 起始點的行列位置（從 1 開始）"""
        # 先算出 token 的「全域位置」：第幾個字元（以整個字串為基礎）
        global_char_pos = sum(
            len(line) + 1 for line in self.lexer.source_code.split("\n")[:token.line - 1]) + token.start_pos - 1

        # 把從目前這個 S-expression 的開始位置，到錯誤 token 位置為止，抓出來
        relative_text = self.lexer.source_code[self._current_s_exp_start_pos:global_char_pos]

        # 利用 \n 切出行數與欄位數
        lines = relative_text.split("\n")
        line = len(lines)
        column = len(lines[-1]) + 1  # human-style column
        return line, column

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
            value = token.value
            line, pos = self._relative_token_position(token)

            raise UnexpectedTokenError(
                f"ERROR (unexpected token) : atom or '(' expected when token at Line {line} Column {pos} is >>{value}<<"
            )

        elif token.type == "RIGHT_PAREN":
            value = token.value
            line, pos = self._relative_token_position(token)

            raise UnexpectedTokenError(
                f"ERROR (unexpected token) : atom or '(' expected when token at Line {line} Column {pos} is >>{value}<<"
            )

    def _parse_list(self) -> ASTNode:
        """Parse an S-Expression list"""
        elements = []

        while self._current_token.type not in ("RIGHT_PAREN", "EOF"):
            if self._current_token.type == "DOT":   # 如果遇到 `.`，要轉換成統一的 cons node 結構 e.g. (1 2 . 3) => (1 . (2 . 3))
                if not elements:
                    line, pos = self._relative_token_position(self._current_token)
                    value = self._current_token.value

                    raise UnexpectedTokenError(
                        f"ERROR (unexpected token) : atom or '(' expected when token at Line {line} Column {pos} is >>{value}<<"
                    )

                self._consume_token()  # skip `.`

                if self._current_token.type == "RIGHT_PAREN":  # Cons Node 不能沒有 cdr
                    line, pos = self._relative_token_position(self._current_token)
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
                    line, pos = self._relative_token_position(token)
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