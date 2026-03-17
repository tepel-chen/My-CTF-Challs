# Resume Maker

[English](./README.md)

## 説明

履歴書を作成してみんなにシェアしよう！

## Writeup

### 概要

脆弱性の本質は次のコードにあります。

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

信頼できない入力に対して `unserialize` を使うと、攻撃者は返り値を任意に制御できます。これは、**クラスインスタンスを返させることも可能**です。このような脆弱性を **unsafe deserialization** と呼びます。

この問題の目標は、任意ファイル読み取りが可能なガジェットを見つけて `/flag.txt` を読むことです。

### 解法

まず任意ファイル読み取りができるガジェットを見つけ、そこから逆算しましょう。

`Icon` クラスの `__toString` メソッドがファイル読み取りガジェットになっています。

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

`__toString` は、次のようにインスタンスが文字列へキャストされるときに呼ばれる特別なメソッドです。

```php
(string) $var;
```

または

```php
"Hello, " . $var;
```

`__toString` のように明示的に呼び出さなくても、PHP の言語仕様上の特定の挙動の中で自動的に呼ばれる特殊なメソッドを[**マジックメソッド**](https://www.php.net/manual/ja/language.oop5.magic.php) と言います。

フラグを得るには `$this->path` を `/../../../flag.txt` にしたいですが、ぱっと見では `__construct` により `/public/A.png`、`/public/B.png`、`/public/C.png` しか入れられないように見えます。

重要なのは、**デシリアライズ時には `__construct` が呼ばれない**ことです。代わりに `__wakeup` があればそれが呼ばれますが、ここでは定義されていません。したがって、プロパティに任意の値を入れられ、`$this->path = '/../../../flag.txt'` とすることも可能です。

では `Icon` インスタンスが文字列にキャストされる場所はどこでしょうか。答えは次の箇所です。

```php

function h($value): string
{
    return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
}
/* ... */

<h1><?= h($user->name) ?></h1>
```

`$user->name` には型チェックがないため、ここに `Icon` インスタンスを入れると文字列キャストが発生します。unsafe deserialization では、このような **type confusion** が有効なガジェットになることがあります。

完全な exploit は [solve.php](./solution/solve.php) を参照してください。

オブジェクトのプロパティを辿って悪意あるシリアライズデータを組み立てる手法は **POP (Property-Oriented Programming) chain** と呼ばれます。興味があれば、[PHPGGC](https://github.com/ambionics/phpggc) に実際のライブラリで見つかった POP chain の例がまとまっています。

## フラグ

`Alpaca{po_popopopop_PoPoPo_PoP_chain}`
