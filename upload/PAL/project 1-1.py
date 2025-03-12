def ourscheme_repl():
    print("Welcome to OurScheme!")

    while True:
        try:
            line = input().strip()

            # if number
            try:
                num = float(line)

                if num.is_integer() and "." not in line:
                    print(f"\n> {int(num)}")
                else:
                    print(f"\n> {num:.3f}")
                continue

            except ValueError:
                if line == "(exit)":
                    print("\n> ")
                    break

                if line.startswith(";") or not line:
                    continue

                if line in ("()", "#f"):
                    print("\n> nil")

                elif line in ("#t", "t"):
                    print("\n> #t")

                elif line.startswith('"') and line.endswith('"'):  # 判斷是否為字串
                    raw_string = line[1:-1]  # 去掉開頭和結尾的雙引號

                    # ✅ **更好的方式：先檢查 \N，決定使用 decode 還是 replace**
                    if "\\N" in raw_string:
                        processed_string = (raw_string
                                           .replace("\\n", "\n")
                                           .replace("\\t", "\t")
                                           .replace("\\\"", "\""))  # 只轉換 `\"`
                    else:
                        processed_string = bytes(raw_string, "utf-8").decode("unicode_escape")

                    print(f'\n> "{processed_string}"')

                else:
                    print(f"\n> {line}")

        except EOFError:
            print("\n> ERROR (no more input) : END-OF-FILE encountered")
            break

    print("Thanks for using OurScheme!")


if __name__ == "__main__":
    # repl()
    n = input()
    ourscheme_repl()
    quit(0)