# InstaTalk

[English](./README.md)

## 問題文

ユーザー登録なしで使えるメッセージアプリ、作りました！

## Writeup

### 概要

これは Server-Sent Events (SSE) を使用するメッセージングアプリケーションです。メッセージを受信する部分に、明らかにXSSが行えそうな箇所が存在します。

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

しかし、メッセージはサーバー側で DOMPurify を使ってサニタイズされています。

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

なんとかしてサニタイズをバイパスすることはできるでしょうか？

### Step 1: SSEインジェクション

サーバーは、DOMPurify からの出力に改行コード (`\n`) が含まれていないかをチェックしています。もし改行コードが含まれていた場合、ユーザーが改行を挿入して新しいメッセージ行を作成できてしまうためです。

このチェックは、SSEが `\n` のみを改行文字として扱うという前提に基づいています。しかし、これは正しくありません。[WHATWGの仕様](https://html.spec.whatwg.org/multipage/server-sent-events.html#parsing-an-event-stream)によると：

> Lines must be separated by either a U+000D CARRIAGE RETURN U+000A LINE FEED (CRLF) character pair, a single U+000A LINE FEED (LF) character, or a single U+000D CARRIAGE RETURN (CR) character.

これは、キャリッジリターン (`\r`) も改行として扱われることを意味します。

たとえば、サニタイズされた出力が以下のようになったとします。

```html
<li><p>00000000 → 11111111</p><p><a id="\r
\r
data: <img src=x onerror=alert(1)>">foobar</a></p></li>
```

この場合、3行目が次のメッセージイベントとしてみなされ、悪意のあるJavaScriptコードが実行されます。


### Step 2: DOMPurifyチェックのバイパス

あとは、DOMPurifyへの入力に `\r` を含めるだけで良さそうに思えます。

残念ながら、そうはいきません。DOMPurify（正確には、そのHTMLパーサーであるJSDOM）はすべての `\r` 文字を `\n` に正規化するため、サニタイズされた出力に直接 `\r` を表示させることはできません。

これに対しては、DOMPurifyがHTMLエンコードされた文字をUTF-8に暗黙的にデコードするという、ドキュメント化されていない挙動を利用することができます。

DOMPurifyは属性値の文字列から両端の空白のような文字を削除することに注意し、`\r` が `&#13;` としてHTMLエンコードできることを踏まえると：

```html
<li><p>00000000 → 11111111</p><p><a id="a&#13;&#13;data:<img src='X' onerror='alert(1)'>">a</a></p></li>
```

これは以下のようにサニタイズされます。

```html
<li><p>00000000 → 11111111</p><p><a id="a\r
\r
data:<img src='X' onerror='alert(1)'>">a</a></p></li>
```

3行目が別のメッセージイベントとして処理されるため、`alert(1)` が実行されます。

完全なソルバーについては、[solver.py](./solver.py) を参照してください。


## フラグ

`Alpaca{y0uve_g0t_4_m3ssage_fr0m_alpac4}`
