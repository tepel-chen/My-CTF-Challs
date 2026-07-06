# Nano Services

[日本語はこちら](./README-ja.md)

## Description

Very small services.


### Beginner Hint 1: About the Admin Bot

- In this challenge, you are given not only the web application itself but also an Admin Bot.
- The Admin Bot has a cookie containing the flag, and it opens a specified path using headless Chrome.
- Therefore, your goal is to make the Admin Bot trigger your payload and send the cookie value to an external server.
- You can prepare your own server as the destination or use an existing service that lets you receive and inspect HTTP requests.
- If you are not yet familiar with how to use the Admin Bot or how to inspect incoming requests, it may help to solve [Fushigi Crawler](https://alpacahack.com/daily/challenges/fushigi-crawler?month=2026-01) first and read its writeup.

### Beginner Hint 2: Approach

- The cookie has the `HttpOnly` flag enabled. This means that even if you succeed in XSS, you cannot leak the cookie using `document.cookie`.
- It looks like there are 3 functions you can choose from via the `func` parameter. Is that all?

## Writeup

### Overview

```php
<?php

$message = '';
function currentTime(): string
{
    return date('Y-m-d H:i:s');
}

function ping(): string
{
    return "Pong!";
}

function echoString(): string
{
    return $_GET['string'];
}

$func = $_GET['func'] ?? null;

if ($func && function_exists($func)) {
    $message = $func();
}

?>
<!-- ... -->
<?php
    if ($message !== '') {
        echo $message;
    }
?>
```

This is a PHP application that allows the user to call specific functions. The `echoString` function is clearly vulnerable to XSS because it outputs the unescaped `string` query parameter directly.

Our goal is to exfiltrate the `HttpOnly` cookie:

```javascript
const page = await browser.newPage();
await page.setCookie({
  name: "FLAG",
  value: FLAG,
  domain: new URL(APP_URL).hostname,
  path: "/",
  // httpOnly flag hides the cookie from JavaScript. You cannot reference it using `document.cookie` in XSS.
  // httpOnlyフラグは、Javascriptからcookieを隠蔽します。したがって、XSSにおいて`document.cookie`を利用しても参照できなくなります。
  httpOnly: true
});
await page.goto(url, { timeout: 5000 });
await sleep(5000);
```

As the comment states, you cannot reference the cookie in JavaScript using `document.cookie` when `HttpOnly` is enabled. Can we somehow bypass this restriction and retrieve the cookie?

### Solution

The PHP function `function_exists` checks for both user-defined and built-in PHP functions.
If we can find a built-in function that:

* Requires no arguments (or only optional ones)
* Either returns or displays a string containing the `HttpOnly` cookie,

we can exfiltrate its content via XSS.

PHP has [over 1,000 built-in functions](https://www.php.net/manual/en/indexes.functions.php). While we could automate and fuzz all of them, there is an easier path.

A quick web search reveals (for example, in [this writeup](https://aleksikistauri.medium.com/bypassing-httponly-with-phpinfo-file-4e5a8b17129b)) that `phpinfo()`, which displays comprehensive information about the PHP configuration, also outputs the HTTP request headers. This includes the `Cookie` header, which exposes the `HttpOnly` cookie.

In our XSS payload, we can use `fetch` to request `/?func=phpinfo` and read the response. Since the `phpinfo` output is quite large, we can extract the flag using a regular expression and send it to an attacker-controlled server. Refer to [solver.py](./solver.py) for the complete exploit script.


## Flag

`Alpaca{http0nly_cook1e_is_m3rely_a_m1tigation}`
