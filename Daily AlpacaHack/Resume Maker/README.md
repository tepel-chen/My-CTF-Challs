# Resume Maker

[日本語はこちら](./README-ja.md)

## Description

Create your resume and share to others!

## Writeup

### Overview

The core vulnerability is here.

```php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!empty($_POST['serialized'])) {
        $decoded = base64_decode($_POST['serialized'], true);
        if ($decoded !== false) {
            $user = unserialize($decoded);
        }
        /* ... */
    }
    /* ... */
}
```

Using `unserialize` on untrusted input allows an attacker to control the returned value, **including class instances**. This is called **unsafe deserialization**.

The goal of this challenge is to read `/flag.txt` by finding a gadget that allows arbitrary file reads.

### Solution

First, find a gadget that allows arbitrary file reads, then work backward from there.

The `Icon` class appears to contain a file-read gadget in its `__toString` method.

```php
class Icon {
    public $path;

    public function __construct(string $type)
    {
        $allowed = ['A', 'B', 'C'];
        if (!in_array($type, $allowed, true)) {
            throw new InvalidArgumentException('Unknown icon type.');
        }

        $this->path = "/public/{$type}.png";
    }

    /* ... */

    public function __toString(): string
    {
        $contents = file_get_contents(__DIR__ . $this->path);
        if ($contents === false) {
            return '';
        }
        return 'data:image/png;base64,' . base64_encode($contents);
    }
}
```

`__toString` is a special method that is called whenever an instance is cast to a string, such as:

```php
(string) $var;
```

or

```php
"Hello, " . $var;
```

Methods like `__toString` are called [**magic methods**](https://www.php.net/manual/en/language.oop5.magic.php): PHP invokes them automatically during specific language-level behavior, even if you do not call them explicitly.

To get the flag, you want `$this->path` to be `/../../../flag.txt`. At first glance, however, `__construct` only allows `/public/A.png`, `/public/B.png`, or `/public/C.png`.

The key point is that **deserialization does not call `__construct`**. Instead, it calls the `__wakeup` magic method if it exists. Since `__wakeup` is not defined here, you can set object properties to arbitrary values, including `$this->path = '/../../../flag.txt'`.

Where do we cast the `Icon` instance to string? The answer lies here:

```php

function h($value): string
{
    return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
}
/* ... */

<h1><?= h($user->name) ?></h1>
```

`$user->name` is never type-checked, so we can set it to an `Icon` instance and have it cast to a string. In unsafe deserialization, this kind of **type confusion** can become a useful gadget.

Please see [solve.php](./solution/solve.php) for the full exploit.

Chaining objects via their properties to build malicious serialized data is called a **POP (Property-Oriented Programming) chain**. If you are interested, [PHPGGC](https://github.com/ambionics/phpggc) contains many real-world POP chains from vulnerable library versions.

### Flag

`Alpaca{po_popopopop_PoPoPo_PoP_chain}`
