# What's Next

[English](./README.md)

## 問題文

Next.js、大好き！

### 初心者向けヒント1: この問題の概要

- `Dockerfile`を読むと、`secret.js`がランダムなファイル名に変えられています。したがって、`/secret`ではなく`/secret-{ランダムな32文字}`にアクセスしなければなりません
- その他のコードは、Next.jsの最小限の構成のようです

### 初心者向けヒント2: 問題へのアプローチ

- メインページにアクセスしたときにどのような通信が行われているでしょうか？
- 過去に、隠したページが見つかってしまって困った人が報告しているかもしれません。インターネットで探してみましょう。

## Writeup

### 解法1: ブラウザのNetworkタブを調べる

ブラウザのNetworkタブで読み込まれているリソースを確認すると、有効なページの一覧が`_buildManifest.js`に含まれていることが分かります。

![alt text](image.png)

### 解法2: インターネットで類似事例を探す

広く使われているフレームワークやライブラリを使ったCTF問題では、GoogleやGitHubで似た報告を探してみる価値があります。この問題では、[このディスカッション](https://github.com/vercel/next.js/discussions/61755)がまさに同じ問題を扱っています。

> でも、あなたのヒントのおかげで、どこに全ページの一覧があるのか分かりました: `_next/static/HASH_0123456789_HASH/_buildManifest.js`


## フラグ

`Alpaca{wh1ch_i5_worse?rand0mized_path_0r_pag3s_rout3r?}`
