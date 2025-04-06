<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# whats the difference between special form and not special form?

In Scheme, the distinction between a **special form** and a **non-special form (procedure)** lies in how arguments are evaluated and how the construct behaves. Here's a detailed breakdown:

---

### **Special Form**

- **Definition:** A special form is a syntactic construct in Scheme where the evaluation of its arguments does not follow the usual rules. Instead, the arguments may be evaluated selectively or not evaluated at all, depending on the semantics of the special form.
- **Key Characteristics:**

1. **Selective Evaluation:** Special forms control how and whether their arguments are evaluated. For example:
        - `and` stops evaluating as soon as it encounters `#f`.
        - `if` evaluates only one of its branches (either the "then" or "else" clause).
2. **Control Flow:** Special forms are often used to implement control structures like conditional execution (`if`), loops (`do`), and logical operations (`and`, `or`).
3. **Not a Procedure:** Special forms are not procedures, so they do not follow the standard evaluation rules for function calls.
- **Examples:**
    - `(if test-expression then-expression else-expression)`
        - Only one of `then-expression` or `else-expression` is evaluated based on the result of `test-expression`.
    - `(and expr1 expr2 ...)`
        - Stops evaluating as soon as an expression evaluates to `#f`.

---

### **Non-Special Form (Procedure)**

- **Definition:** A procedure is a regular function in Scheme, and all its arguments are fully evaluated before the procedure itself is executed.
- **Key Characteristics:**

1. **Full Evaluation:** All arguments are evaluated before the procedure is applied. This is standard behavior in Scheme.
2. **No Control Over Argument Evaluation:** Procedures cannot selectively evaluate or skip arguments; they rely on already-evaluated values passed to them.
3. **Purely Functional:** Procedures are used for computations rather than controlling program flow.
- **Examples:**
    - `(not expr)`
        - The argument `expr` is always fully evaluated before being passed to the `not` procedure.
    - `(+ 1 2)`
        - Both arguments (`1` and `2`) are evaluated before being passed to the `+` procedure.

---

### **Key Differences Between Special Forms and Procedures**

| Feature | Special Form | Procedure |
| :-- | :-- | :-- |
| **Argument Evaluation** | Selective or conditional evaluation | Full evaluation of all arguments |
| **Purpose** | Control flow (e.g., conditionals, looping) | Computation or transformation |
| **Examples** | `if`, `and`, `or`, `lambda` | `not`, `+`, `list`, `car` |
| **Short-Circuiting** | Supported (e.g., in `and`, `or`) | Not supported |

---

### Why This Matters

Special forms enable efficient control of program flow by avoiding unnecessary computations, while procedures focus on performing operations with fully evaluated inputs. This distinction allows Scheme to be both expressive and computationally efficient.

