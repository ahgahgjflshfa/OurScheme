## **📌 OurScheme Interpreter 架構總覽**
### **🔷 主要元件**
你的 Interpreter 由 **4 個主要部分** 組成：
1. **Lexer（詞法分析）** → **將輸入字串轉換為 Token**
2. **Parser（語法分析）** → **將 Token 轉換為 AST**
3. **Evaluator（AST 執行器）** → **計算 AST，並回傳結果**
4. **REPL（Read-Eval-Print Loop）** → **讀取輸入並不斷執行**

這 4 個部分依序運行，互相合作來讓 OurScheme 代碼可以解析與執行。

---

## **📌 各個元件的工作方式與架構**
### **1️⃣ Lexer（詞法分析器）**
**🔹 主要功能**
- **負責將輸入字串拆解成 Token**
- 例如：
  ```scheme
  (+ 3 4)
  ```
  **轉換為 Token**
  ```python
  ["(", "+", "3", "4", ")"]
  ```

**🔹 輸入 & 輸出**
| **輸入**  | **輸出**  |
|---------|---------|
| `"(+ 3 4)"`  | `["(", "+", "3", "4", ")"]` |

**🔹 與其他元件的關係**
- Lexer **將 Token 提供給 Parser**，Parser 依據 Token 產生 AST。

**🔹 Lexer 內部結構**
```python
class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0  # 當前讀取位置
        self.tokens = []

    def tokenize(self):
        """掃描 source 轉換成 Token"""
        pass  # 這裡會根據字元類型拆分 Token
```

---

### **2️⃣ Parser（語法分析器）**
**🔹 主要功能**
- **將 Token 轉換為 AST**
- 例如：
  ```python
  ["(", "+", "3", "4", ")"]
  ```
  轉換為：
  ```python
  ListNode([SymbolNode("+"), NumberNode(3), NumberNode(4)])
  ```

**🔹 輸入 & 輸出**
| **輸入**  | **輸出**  |
|---------|---------|
| `["(", "+", "3", "4", ")"]`  | `ListNode([SymbolNode("+"), NumberNode(3), NumberNode(4)])` |

**🔹 與其他元件的關係**
- **Parser 從 Lexer 取得 Token**，解析並轉換成 **AST**。
- **Evaluator 會執行 AST，計算結果**。

**🔹 Parser 內部結構**
```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0  # 當前讀取 Token 位置

    def parse(self):
        """解析 Token 並產生 AST"""
        pass  # 這裡會遞歸解析 S-Expression，產生 AST
```

---

### **3️⃣ Evaluator（AST 執行器）**
**🔹 主要功能**
- **執行 AST，並計算結果**
- 例如：
  ```python
  ListNode([SymbolNode("+"), NumberNode(3), NumberNode(4)])
  ```
  **執行後回傳**
  ```python
  7
  ```

**🔹 輸入 & 輸出**
| **輸入**  | **輸出**  |
|---------|---------|
| `ListNode([SymbolNode("+"), NumberNode(3), NumberNode(4)])` | `7` |

**🔹 與其他元件的關係**
- **Evaluator 讀取 AST 並執行**，回傳最終計算結果。

**🔹 Evaluator 內部結構**
```python
class Evaluator:
    def __init__(self):
        self.environment = {}  # 儲存變數

    def eval_ast(self, ast):
        """執行 AST 並計算結果"""
        pass  # 這裡會實作運算與變數儲存
```

---

### **4️⃣ REPL（Read-Eval-Print Loop）**
**🔹 主要功能**
- 讓 Interpreter **可以持續讀取、解析並執行**，直到使用者輸入 `(exit)`。
- 依序呼叫：
  - `Lexer`（詞法分析）
  - `Parser`（語法分析）
  - `Evaluator`（執行 AST）

**🔹 與其他元件的關係**
- **REPL 是所有元件的總控中心**，它調用 Lexer、Parser 和 Evaluator。

**🔹 REPL 內部結構**
```python
def repl():
    print("Welcome to OurScheme!")

    while True:
        try:
            # 1️⃣ 讀取使用者輸入
            expr = input("> ")

            # 2️⃣ 若輸入 (exit)，則退出
            if expr.strip() == "(exit)":
                break

            # 3️⃣ 進行 Tokenize & Parse
            tokens = Lexer(expr).tokenize()
            ast = Parser(tokens).parse()

            # 4️⃣ 執行 AST 並輸出結果
            result = Evaluator().eval_ast(ast)
            print(result)

        except EOFError:
            print("ERROR: END-OF-FILE encountered")
            break

    print("\nThanks for using OurScheme!")
```

---

## **📌 各元件如何互相合作？**
1️⃣ **REPL** 負責讀取輸入，將輸入字串傳給 `Lexer`。  
2️⃣ **Lexer** 將輸入字串轉換為 Token 列表，傳給 `Parser`。  
3️⃣ **Parser** 解析 Token，轉換成 AST，傳給 `Evaluator`。  
4️⃣ **Evaluator** 執行 AST，計算結果並回傳給 `REPL`。  
5️⃣ **REPL** 輸出結果，並回到第一步繼續迴圈。

**流程圖**
```
使用者輸入  "(+ 3 4)"
    ↓
[Lexer]  轉換為 Token: ["(", "+", "3", "4", ")"]
    ↓
[Parser]  轉換為 AST:  ListNode(["+", 3, 4])
    ↓
[Evaluator] 計算結果:  7
    ↓
[REPL] 輸出: 7
    ↓
等待下一個輸入...
```

---

## **📌 你現在應該做什麼？**
✅ **1. 確認架構清楚後，先寫 Lexer**（確保 Token 解析正確）  
✅ **2. 再寫 Parser**（確保 AST 能正常生成）  
✅ **3. 然後寫 Evaluator**（讓 AST 可以執行）  
✅ **4. 最後完成 REPL**（讓 Interpreter 可以互動）  

---

### **📌 這樣的架構你覺得清楚嗎？還有哪部分想要進一步確認？** 😃