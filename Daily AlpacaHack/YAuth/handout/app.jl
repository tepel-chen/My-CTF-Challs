import JSON
import YAML

yaml_constructors = merge(YAML.default_yaml_constructors, Dict{String, Function}(
    "tag:yaml.org,2002:map" => (constructor, node) ->
        YAML.construct_mapping(
            Dict{String, Any},
            constructor,
            node;
            strict_unique_keys=true, # Prohibit duplicate key
        )
))

flag = get(ENV, "FLAG", "Alpaca{dummy}")

println("JSON:")
body = readline(stdin)

try
    data = JSON.parse(body, Dict{String, Any})
    data["username"] = "Guest"

    yaml = YAML.write(data)
    result = YAML.load(yaml, yaml_constructors)

    if result["username"] == "Admin"
        result["flag"] = flag
    end

    println(JSON.json(result))
catch
    println("Error occurred")
end
