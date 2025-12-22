
# Log Viewer

## Description

Simple log viewer with regex feature.

## Writeup

### Overview

The core of the vulnerability is here:

```python
query = request.form.get("query", "")

command = ["awk", f"/{query}/", "info.log"]
result = subprocess.run(
    command,
    capture_output=True,
    timeout=0.5,
    text=True,
)
log = result.stderr or result.stdout
```

The `awk` command is often used to process a file line by line, for example to filter or transform text. Here, user input is embedded into `f"/{query}/"`, which is passed to awk as its program. This allows us to inject content into the awk program.

The flag exists in `/flag-<md5 hash of the flag>`. Can we extract the file's contents using this injection?

### Understanding OS command injection

At first glance, you might think a payload such as `foobar/ info.log; cat /flag* #` would work, because after the injection the command would look like:

```bash
awk /foobar/ info.log; cat /flag* # / info.log
```

However, that will not work because it is not injected like that. There is a difference between an OS command run through a shell (such as `bash`) and one that is not.

A typical example of an OS command run through a shell is `os.system` in Python. If the code had been:

```python
os.system(f"awk /{query}/ info.log")
```

then the payload above would have worked.

When a command is executed via a shell, an attacker can use techniques like:

- splitting the command using `;`, `&`, or `|`
- command substitution using `$(command)` or `` `command` ``
- referencing environment variables using `$ENV`

By contrast, commands executed without a shell cannot use those techniques, which makes it harder for an attacker to run arbitrary commands. For `subprocess.run`, the command is executed through a shell only if `shell=True` option is passed. That is not the case here, so we need a different approach.

### Understanding `awk`

If you search online for how to use `awk`, you'll find that it is not just a simple text-processing tool, but also a programming language. You can perform actions using a pattern-action form like `/pattern/{ action }`. In addition, the character `#` starts a comment in awk. Hence, if you send the payload `.*/{print $1} #`, the argument will become:

```
/.*/{print $1} #/
```

Note that this trailing `/` is added by the server because it wraps the input as `f"/{query}/"`. Therefore, we must comment it out by adding `#`, so it does not interfere with our injected awk program.

You can read the [`awk` manual](https://www.gnu.org/software/gawk/manual/html_node/Functions.html) to find useful functions. However, there is an easier way to find exploit payloads in situations like this.

[GTFOBins](https://gtfobins.github.io/) is a catalog of binaries and example payloads that can be used to bypass security restrictions. The [`awk` page on GTFOBins](https://gtfobins.github.io/gtfobins/awk/) shows that you can invoke a command with:

```awk
system("/bin/sh")
```

If you send `.*/{system("cat /flag*")} #`, the OS command `cat /flag*` will run. However, the service will return an error page instead of the result. This is because the `subprocess.run` call sets a timeout of 500 ms, and executing many `system()` calls will exceed that timeout.

To bypass this you can either:
- ensure that only one line is matched (for example: `242.24.138.42/{system("cat /flag*")} #`)
- exit the `awk` program after printing the flag using `exit` (for example: `.*/{system("cat /flag*"); exit 0} #`)

## Flag

`Alpaca{th3_AWK_Pr0gr4mming_Lan9u4g3}`
