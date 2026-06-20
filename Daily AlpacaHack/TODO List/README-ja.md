# TODO List

[English version is here](./README.md)

## 説明

TODO: このサイトにXSSが無いか確認する

### Beginner Hint1: Admin Botについて

- この問題では、Webアプリ本体とは別に Admin Bot が用意されています。
- Admin Bot はフラグ入りのCookieを持った状態で、指定されたパスを Headless Chrome で開きます。
- そのため、目標は「Admin Bot に自分の用意したペイロードを踏ませて、Cookieの内容を外部へ送らせること」です。
- 送信先は自分でサーバーを立ててもよいですし、HTTPリクエストを受け取って確認できる既存サービスを使っても構いません。
- Admin Bot の使い方や、外部から受信したリクエストの確認方法がまだ曖昧なら、先に [Fushigi Crawler](https://alpacahack.com/daily/challenges/fushigi-crawler?month=2026-01) を解いてWriteupを読むことをおすすめします。

### Beginner Hint2: この問題の概要
  
- このアプリはシンプルなTODOアプリです。最初にアクセスするとセッションIDが発行され、そのセッションに紐づくTODOリストを作成できます。
- `?sessionId=...` を指定すると、他人のセッションに対応するリストも閲覧できます。つまり、Admin Bot に自分のセッションIDを開かせることができます。
- TODOの各アイテムにはHTMLを入力できますが、そのまま表示しているわけではなく、[DOMPurify](https://github.com/cure53/DOMPurify) でサニタイズしてあります。
- DOMPurify 自体は最新版なので、「古い既知脆弱性をそのまま突く」方向ではなさそうです。

### Beginner Hint3: この問題のアプローチ

- DOMPurify のようなサニタイザを使うときの基本原則は、「サニタイズしたあとの文字列を、あとから別の形に加工しないこと」です。
- このアプリでは、サニタイズ後のデータは加工されているでしょうか？

## Writeup

WIP

## Flag
`Alpaca{4noth3r_sandb0x_An0ther_byp4s5}`
