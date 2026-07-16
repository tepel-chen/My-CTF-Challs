import shlex

code = input("jail >")

if not code.isascii():
    # Why? Because https://alpacahack.com/daily/challenges/super-short-system-exit
    print("Not ascii")
    exit()

if "_" in code:
    print("No dunder methods/attributes")
    exit()

eval(code, {"shlex": shlex, "__builtins__": {}})