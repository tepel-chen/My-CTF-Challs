from z3 import *

m = {'c': ['t', '0'], 'd': ['_R', '1'], 'e': ['c', 'Xx'], 'f': ['w', '{'], 'h': ['1?', '_D'], 'l': ['3d'], 'm': ['B'], 'p': ['1l', 'r4'], 'r': ['_d', 'Se', '4_'], 's': ['S4', '3'], 't': ['f'], 'u': ['s', 'S4'], 'w': ['e', 'h1'], 'x': ['X!'], 'B': ['!'], 'D': ['1s', '_'], 'E': ['r', '_w'], 'M': ['p', 'xB'], 'R': ['39'], 'S': ['4', 's3'], 'U': ['_u', '1?'], 'X': ['x', '!_'], '0': ['M', '1R'], '1': ['l', '?', 'sS', 'D'], '3': ['d_', '9', 'm', '?'], '4': ['Ss'], '9': ['eX'], '{': ['c0', '3f'], '!': ['_w', 'E'], '?': ['h_', '}'], '_': ['R', 'wh', 'D1', 'd', 'U', 'u']}
 
charset = sorted(set(m.keys()) | {'}'})

char_to_int = {c: i for i, c in enumerate(charset)}
int_to_char = {i: c for c, i in char_to_int.items()}

n = 50

vars = [Int(f"x{i}") for i in range(n)]
s = Solver()

s.add(vars[0] == char_to_int['{'])
s.add(vars[-1] == char_to_int['}'])
for v in vars[1:-1]:
    s.add(Or([v == char_to_int[c] for c in charset if c not in '{}']))

for i in range(n - 1):
    for c in charset:
        if c == '}':
            continue
        nexts = []
        for cands in m[c]:
            if len(cands) + i >= n:
                continue
            nexts.append(And([vars[i + j + 1] == char_to_int[cands[j]] for j in range(len(cands))])) 
        s.add(Implies(vars[i] == char_to_int[c], Or(nexts)))


if s.check() == sat:
    model = s.model()
    result = [model[v].as_long() for v in vars]
    str_result = "".join(int_to_char[i] for i in result)
    print("Found string:", str_result)

    while True:

        s.push()
        s.add(Or([v != val for v, val in zip(vars, result)]))
        if s.check() == unsat:
            break
        else:
            result = [s.model()[v].as_long() for v in vars]
            str_result = "".join(int_to_char[i] for i in result)
            print("✘ 他にも解があります。例:", str_result)
else:
    print("No solution found.")