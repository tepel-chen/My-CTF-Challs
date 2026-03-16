# Alpaca Rangers

[日本語版はこちら](./README-ja.md)

## Description

Hero of Justice, Alpaca Rangers!

## Writeup

### Overview

The goal of this challenge is to read the contents of `/flag.txt`.

```php
if (str_starts_with($targetPath, '/') || str_starts_with($targetPath, '\\') || str_contains($targetPath, '..')) {
    $errorMessage = 'Invalid path.';
} else {
    $contents = @file_get_contents($targetPath);
    /* ... */
}
```

It seems that it blocks common directory traversal attacks such as:
* `../../../flag.txt`
* `/flag.txt`

Can we bypass this filter?

### Solution

If you read the documentation for [`file_get_contents`](https://www.php.net/manual/en/function.file-get-contents.php), you will see that you can use a protocol instead of a filename. From [this page](https://www.php.net/manual/en/wrappers.php), you can see that it supports the `file://` protocol. Therefore, the payload

```
file:///flag.txt
```

is not filtered and still reads the file!

Another option is using the `php://` protocol, which also allows reading the file.

```
php://filter/resource=/flag.txt
```


## Flag

`Alpaca{Alpaca_gre3n_and_p1nk_com1ng_s0on}`
