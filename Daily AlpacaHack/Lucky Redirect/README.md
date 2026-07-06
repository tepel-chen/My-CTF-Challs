# Lucky Redirect

[日本語はこちら](./README-ja.md)

## Description

I've never used the "Search" button on Google Search; the "I'm Feeling Lucky" button is enough for me.

### Beginner Hint

- While it is theoretically possible to solve this solely in the browser, we highly recommend automating the process using a script.

## Writeup

### Overview

```python
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("nope"))


for i in range(len(FLAG)):
    def make_route(i):
        @app.get("/" + "/".join(FLAG[:i+1]), endpoint=f"flag_{i}")
        def route():
            is_lucky = secrets.randbelow(5) == 0
            if is_lucky and i == len(FLAG) - 1:
                return f"Well done! The flag is: {FLAG}"
            elif is_lucky:
                return redirect(url_for(f"flag_{i+1}"))
            else:
                return redirect(url_for("nope"))

        return route

    make_route(i)


@app.get("/nope")
def nope():
    return "Nope"
```

When you access `/A`, you have a 20% chance of being redirected to `/A/l` and an 80% chance of being redirected to `/nope`. Accessing `/A/l` also redirects you to `/A/l/p` 20% of the time, and to `/nope` otherwise. This process continues until, if you are extremely lucky, you are redirected to `/A/l/p/a/c/a/{/[flag content separated by /]/}`, which will give you the flag.

The probability of reaching the end by chance is extremely low. Can you somehow cheat your way to the final route?

### Understanding how redirects work

To solve this challenge, you must first understand how HTTP redirection works. 

When a server redirects a client to another page, it returns an HTTP response like this:

```
HTTP/1.1 302 FOUND
Server: Werkzeug/3.1.8 Python/3.14.5
Date: Mon, 06 Jul 2026 03:48:24 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 197
Location: /nope
Connection: close

<!doctype html>
<html lang=en>
<title>Redirecting...</title>
<h1>Redirecting...</h1>
<p>You should be redirected automatically to the target URL: <a href="/nope">/nope</a>. If not, click the link.
```

There are two key things to keep in mind:

* The HTTP status code is `302`, which instructs the client to redirect to another page.
* The `Location` header specifies the target route of the redirection.

Note that following the redirection is entirely the client's responsibility. In this challenge, instead of blindly following the redirect to `/nope`, we can intercept the response and retry the request until the server redirects us to the next character of the flag.

### Automating the retry

The flag is 42 characters long. Since each step has a 20% success rate, you need to make an average of 210 requests (5 requests per character) to get the entire flag. While doing this manually is theoretically possible, it would be extremely tedious. Let's automate it using Python and the [requests](https://pypi.org/project/requests/) library.

By default, the `requests` library automatically follows redirects. We can disable this behavior by setting the `allow_redirects` parameter to `False`:

```python
response = requests.get(f"http://localhost:3000/A", allow_redirects=False)
```

You can inspect `response.headers["Location"]` to see where the server is trying to redirect you. If it redirects to `/nope`, you retry the current path. If it redirects to a new subpath, you proceed to that new URL.

If the server does not redirect (i.e., `response.status_code` is `200` instead of `302`), it means you have successfully reached the final route. 

The final solver script looks like this:

```python
import requests
import os
URL = os.environ.get("URL", "http://localhost:3000/").rstrip("/")

known = "/A/l/p/a/c/a/%7B"

while True:
    response = requests.get(f"{URL}/" + known, allow_redirects=False)
    if response.status_code == 200:
        print(response.text)
        break
    if response.headers["Location"] != "/nope":
        known = response.headers["Location"]
```


## Flag

`Alpaca{Ill_never_gamble_again_I_bet_on_it}`
