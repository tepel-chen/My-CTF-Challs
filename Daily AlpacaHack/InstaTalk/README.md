# InstaTalk

[日本語はこちら](./README-ja.md)

## Description

I made a message that requires no registration!

## Writeup

### Overview

This is a messaging application that uses Server-Sent Events (SSE). There is an obvious XSS sink where the message is received:

```javascript
const eventSource = new EventSource("/api/events");
/* ... */
eventSource.addEventListener("message", (event) => {
  try {
    $messages.innerHTML += event.data;
  } catch (error) {
    $error.hidden = false;
    $error.textContent = error;
  }
});
```

However, the message is sanitized using DOMPurify on the server:

```javascript
function createMessage(message: string, from: UUID, to: UUID) {
  const payload: string = DOMPurify.sanitize(
    `<li><p>${from.slice(0, 8)} → ${to.slice(0, 8)}</p><p>${message}</p></li>`.replaceAll("\n", ""),
  );
  if(payload.includes("\n")) {
    return `event: message\ndata: [Deleted for security reason.]\n\n`;
  }
  return `event: message\ndata: ${payload}\n\n`;
}
```

Can we somehow bypass the sanitization?

### Step 1: SSE Injection

The server checks if the output from DOMPurify doesn't include a line feed (`\n`). This is because if it did, the user would be able to start a new line and create a new message line.

This check assumes that SSE only treats `\n` as an end-of-line character. However, this is not true. According to the [WHATWG Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html#parsing-an-event-stream):

> Lines must be separated by either a U+000D CARRIAGE RETURN U+000A LINE FEED (CRLF) character pair, a single U+000A LINE FEED (LF) character, or a single U+000D CARRIAGE RETURN (CR) character.

This means that a carriage return (`\r`) is also treated as a line break.

For example, if the sanitized output looks like this:

```html
<li><p>00000000 → 11111111</p><p><a id="\r
\r
data: <img src=x onerror=alert(1)>">foobar</a></p></li>
```

the third line is considered as the next message event, and malicious JavaScript code will be executed.


### Step 2: Bypassing the DOMPurify check

Now this challenge sounds simple: just include `\r` in the input to DOMPurify, right?

Unfortunately, no. DOMPurify (more precisely, its HTML parser JSDOM) normalizes all `\r` characters to `\n`, so you cannot make `\r` appear in the sanitized output directly.

However, you can leverage an undocumented behavior where DOMPurify silently decodes HTML-encoded characters to UTF-8. 

Also, keep in mind that DOMPurify strips whitespace-like characters from the string. 

Given that `\r` can be HTML-encoded as `&#13;`:

```html
<li><p>00000000 → 11111111</p><p><a id="a&#13;&#13;data:<img src='X' onerror='alert(1)'>">a</a></p></li>
```

will be sanitized to:

```html
<li><p>00000000 → 11111111</p><p><a id="a\r
\r
data:<img src='X' onerror='alert(1)'>">a</a></p></li>
```

Since the third line will be treated as a different message event, `alert(1)` will be executed.

See [solver.py](./solver.py) for the full solve script.

## Flag

`Alpaca{y0uve_g0t_4_m3ssage_fr0m_alpac4}`

