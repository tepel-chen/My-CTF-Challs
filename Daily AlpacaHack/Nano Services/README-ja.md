# Nano Services

[English](./README.md)

## 問題文

ちっちゃいちっちゃいサービス。

### Beginner Hint 1: Admin Botについて

- この問題では、Webアプリ本体とは別に Admin Bot が用意されています。
- Admin Bot はフラグ入りのCookieを持った状態で、指定されたパスを Headless Chrome で開きます。
- そのため、目標は「Admin Bot に自分の用意したペイロードを踏ませて、Cookieの内容を外部へ送らせること」です。
- 送信先は自分でサーバーを立ててもよいですし、HTTPリクエストを受け取って確認できる既存サービスを使っても構いません。
- Admin Bot の使い方や、外部から受信したリクエストの確認方法がまだ曖昧なら、先に [Fushigi Crawler](https://alpacahack.com/daily/challenges/fushigi-crawler?month=2026-01) を解いてWriteupを読むことをおすすめします。

### Beginner Hint 2: アプローチ

- Cookie には `HttpOnly` フラグが設定されています。そのため、たとえ XSS に成功したとしても、`document.cookie` を使って Cookie をリークさせることはできません。
- `func` パラメータで指定できる関数は3つあるようですが、本当にこれだけでしょうか？

## Writeup

### 概要

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

ユーザーが特定の関数を呼び出すことができる PHP アプリケーションです。`echoString` 関数は、クエリパラメータ `string` をエスケープせずに直接出力するため、明らかに XSS に対して脆弱です。

目標は、`HttpOnly` が有効な Cookie を外部に送信することです。

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

コメントにある通り、`HttpOnly` が有効になっている場合、JavaScript から `document.cookie` を用いて Cookie を参照することはできません。何とかしてこの制限を回避し、Cookie を取得することはできないでしょうか？

### 解法

PHP の `function_exists` 関数は、ユーザー定義の関数だけでなく、PHP の組み込み関数に対しても機能します。
もし以下のような組み込み関数が見つかれば、XSS を使ってその内容を外部に送信することができます。

* 引数を必要としない（または引数がすべてオプションである）
* `HttpOnly` Cookie を含む文字列を返す、あるいは表示する

PHP には [1,000 以上の組み込み関数](https://www.php.net/manual/en/indexes.functions.php) が存在します。自動化してすべての関数をファジングすることも可能ですが、より簡単なアプローチがあります。

Web 検索を行うと（例えば [このwriteup](https://aleksikistauri.medium.com/bypassing-httponly-with-phpinfo-file-4e5a8b17129b) などから）、PHP の設定情報を包括的に表示する `phpinfo()` が、HTTP リクエストヘッダーも出力することが分かります。これには `Cookie` ヘッダーが含まれており、`HttpOnly` Cookie も表示されます。

XSS ペイロードでは、`fetch` を使用して `/?func=phpinfo` にリクエストを送り、そのレスポンスを読み取ることができます。`phpinfo` の出力は非常に大きいため、正規表現を使用してフラグを抽出し、攻撃者が制御するサーバーに送信します。詳細なエクスプロイトスクリプトについては [solver.py](./solver.py) を参照してください。


## フラグ

`Alpaca{http0nly_cook1e_is_m3rely_a_m1tigation}`
