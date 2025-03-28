from src.ast_nodes import *

def pretty_print(node, indent: int = 0):
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
        if isinstance(current, AtomNode) and current.type == "BOOLEAN" and current.value == "nil":    # ( ssp . nil ) === ( sp1 sp2 sp3 ... spn )
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
        result = f"( quote"

        result += f"\n{next_indent_str}{pretty_print(node.value, indent + 1)}"

        result += f"\n{indent_str})"
        return result

    return f"{indent_str}UNKNOWN_NODE"