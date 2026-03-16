# You are being redirected

[日本語版はこちら](./README-ja.md)

## Description

You don't want the browser to go to external websites without warning, do you?

## Writeup

The relevant vulnerable code is shown below. The page is designed to redirect to the URL specified by the `to` query parameter after 2 seconds.

```javascript
const FORBIDDEN = ["data", "javascript", "blob"];

const params = new URLSearchParams(window.location.search);
let dest = params.get('to') ?? "/";
const link = document.getElementById("link");

if(FORBIDDEN.some(str => dest.toLowerCase().includes(str))) {
    dest = "/";
}

const url = new URL(dest, window.location.href);
link.href = url.href;
link.innerText = url.href;
setTimeout(() => {
    window.location.replace(url.href);
}, 2000);
```

Because redirects using `window.location` support the [javascript scheme](https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Schemes/javascript), we want to use it to trigger XSS. However, if the URL contains the literal string `javascript`, the filter blocks it. Can we bypass this filtering?

To make it short, if you insert a newline (`%0a`) as shown below, it is removed during `new URL(dest).href`, and XSS succeeds.

```
javas%0acript:<JavaScript code>
```

So, how can we reason our way to this payload?

### Approach 1: If you know the vulnerability name

A vulnerability that allows redirecting users from one web page to an arbitrary page (unintentionally) is called an **Open Redirect**. (This does not always lead to XSS. Depending on the redirect behavior, it may instead lead to phishing, CSP bypass, etc.)

If you know this, you can search for "Open Redirect filter bypass" and refer to pages like [this one](https://www.diverto.hr/en/blog/2024-12-30-open-redirection-url-filter-bypasses/). You can also check collections of filter bypass techniques such as [HackTricks](https://book.hacktricks.wiki/en/pentesting-web/open-redirect.html?highlight=open#open-redirect-1) and [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Open%20Redirect). Then you can simply copy a suitable payload.

### Approach 2: If you do not know the vulnerability name

What if you did not know this vulnerability name? Or what if this were a less common issue and no articles like the above existed?

This validation contains two bad practices:
1. It uses a blacklist instead of a whitelist.
    - There may be filter gaps.
2. It does filtering before parsing, instead of parsing before filtering.
    - Strings that should have been filtered may appear after parsing.

A safer filter would look like this:

```javascript
let url = new URL(dest, window.location.href).href;
if(url.startsWith("http://") || url.startsWith("https://")) {
    window.location.replace(url);
}
```

Since the current code does not do that, we can think: **there might be an input that does not contain `javascript` before filtering, but becomes a `javascript:` URL after passing through `new URL().href`.**

#### Approach 2a: Read source/specs

Reading source code is important, but Chromium is huge and can take time to navigate. So first, you should check the URL parser specification.

According to [MDN](https://developer.mozilla.org/en-US/docs/Web/API/URL/parse_static#specifications), the behavior is defined by WHATWG. Following that leads to [this section](https://url.spec.whatwg.org/#concept-basic-url-parser), which includes:

> 3. 1. Remove all [ASCII tab or newline](https://infra.spec.whatwg.org/#ascii-tab-or-newline) from input.

That step leads to the payload above.

#### Approach 2b: Fuzzing and experiments

In CTFs, you often see problems where parsing reconstructs strings that filters tried to block. Most of them fall into one of these categories:

1. A "similar" character gets converted to another character (uppercase to lowercase, Unicode normalization, conversion across encodings, etc.).
2. Some characters are ignored (null bytes, control characters, newlines, invalid Unicode removal, etc.).

You can test hypotheses manually, but if you suspect "some characters may be ignored," fuzzing is effective. For example, create an HTML file like this and open it in your browser:

```html
<script>
// Replacement pattern
for(let i = 0; i < 0xFFFF /* UTF-16 max value */; i++) {
    const dest = `jav${String.fromCharCode(i)}script:alert(1)`;
    if(dest.toLowerCase().includes("javascript")) {
        continue;
    }
    const after = new URL(dest, window.location.href).href;
    if(after.startsWith("javascript:")) console.log("replace", i, JSON.stringify(String.fromCharCode(i)));
}

// Removal pattern
for(let i = 0; i < 0xFFFF /* UTF-16 max value */; i++) {
    const dest = `java${String.fromCharCode(i)}script:alert(1)`;
    if(dest.toLowerCase().includes("javascript")) {
        continue;
    }
    const after = new URL(dest, window.location.href).href;
    if(after.startsWith("javascript:")) console.log("remove", i, JSON.stringify(String.fromCharCode(i)));

}
</script>
```

From the console output, you can confirm that `\t`, `\r`, and `\n` are removed.

## Flag

`Alpaca{wh4t_comes_after_the_redir3ct_pa9e}`
