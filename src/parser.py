class ASTNode:
    def __repr__(self):
        pass

    def eval(self, env):
        pass


class AtomNode(ASTNode):
    def __init__(self):
        pass


class ListNode(ASTNode):
    def __init__(self):
        super().__init__()


class ConsNode(ASTNode):
    def __init__(self):
        super().__init__()


class QuoteNode(ASTNode):
    def __init__(self):
        super().__init__()


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def _peek_token(self):
        token = self.current_token
        self.current_token = self.lexer.next_token()

    def _parse_s_exp(self):
        """HI"""
        pass

    def _parser_atom(self, token):
        """Parse atom"""
        pass

    def _parse_list(self):
        pass

    def _parse_quote(self):
        pass
