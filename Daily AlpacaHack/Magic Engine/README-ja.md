# Magic Engine

[English version](./README.md)

## 説明

Nginxはまるで魔法だ。

## Writeup

### 概要

サーバは Nginx を使って静的ファイルを配信しています。目標は `secret.html` を読むことです。

```nginx
server {
    listen 80;
    server_name admin.alpaca.secret;

    root /usr/share/nginx/html;

    location = / {
        try_files /secret.html =404;
    }
}

server {
    listen 80;
    server_name *.nip.io;

    root /usr/share/nginx/html;

    location = / {
        try_files /hello.html =404;
    }
}

server {
    listen 80 default_server;
    server_name _;

    root /usr/share/nginx/html;

    location = / {
        try_files /index.html =404;
    }
}
```

リモートサーバの URL にアクセスすると `index.html` が表示されます。

![alt text](image.png)

`http://<IP>.nip.io:<PORT>/` へのリンクを開くと `hello.html` が表示されます。

![alt text](image-1.png)

`server_name *.nip.io;` の行は、ブラウザが `*.nip.io` の URL を使ったときに Nginx が 2 つ目の server ブロックを使うことを示しているようです。

では、ブラウザで `http://admin.alpaca.secret/` にアクセスすれば `secret.html` が見えるのでしょうか？

残念ながらそうではありません。これは、`admin.alpaca.secret` がリモートサーバの IP アドレスに解決されなければならないからです。そもそも、`secret` は `.com`、`.net`、`.org` のようなトップレベルドメイン (TLD) ではないため、これは有効な URL ではありません。

### `Host` ヘッダの理解

サーバはどの URL で IP にアクセスされたかをどうやって知るのでしょうか？答えは `Host` ヘッダです。Chrome のインスペクタを見ると、`http://<IP>:<PORT>/` と `http://<IP>.nip.io:<PORT>/` にアクセスしたときでこのヘッダが異なることが分かります。

![alt text](image-2.png)

![alt text](image-3.png)

つまり、`Host` ヘッダを `admin.alpaca.secret` にしてリクエストを送ればフラグが取得できます。`curl` で簡単に実行できます。

```sh
curl -H "Host:admin.alpaca.secret" http://34.170.146.252:47872/
```

### 非想定解法

この問題には大きな作問ミスがありました。`root` ディレクティブのドキュメントを見ると、次のように書かれています。

> Sets the root directory for requests. For example, with the following configuration

```
location /i/ {
    root /data/w3;
}
```

> The /data/w3/i/top.gif file will be sent in response to the “/i/top.gif” request.

つまり、`http://<IP>:<PORT>/secret.html` にアクセスするだけで取得できてしまいます。これを防ぐには、次のように書くべきでした。

```
server {
    listen 80;
    server_name admin.alpaca.secret;

    location = / {
        alias /usr/share/nginx/html;
        try_files /secret.html =404;
    }
}
```

この点を[writeup](https://github.com/EdamAme-x/writeup/blob/main/alpaca-hack/magic-engine/README.md)で指摘してくださった edamame-x 様に感謝します！

## フラグ

```
Alpaca{Host_works_just_like_Magic}
```
