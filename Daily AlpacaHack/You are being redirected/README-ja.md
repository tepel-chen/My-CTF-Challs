# You are being redirected

[English version](./README.md)

## 問題文

警告なしにブラウザが外部サイトに飛ぶのは嫌ですよね？

## Writeup

関連コードは以下のとおりです。ページを開いて２秒後に`to`のクエリパラメータで指定されたURLにリダイレクトする設計になっています。

```javascript
const FORBIDDEN = ["data", "javascript", "blob"];

const params = new URLSearchParams(window.location.search);
let dest = params.get('to') ?? "/";
const link = document.getElementById("link");

if(FORBIDDEN.some(str => dest.toLowerCase().includes(str))) {
    dest = "/";
}

const url = new URL(dest, window.location.href);
link.href = url.href;
link.innerText = url.href;
setTimeout(() => {
    window.location.replace(url.href);
}, 2000);
```

`window.location`を利用したリダイレクトでは、[javascriptスキーム](https://developer.mozilla.org/ja/docs/Web/URI/Reference/Schemes/javascript)をサポートするので、これを利用してXSSを実行したいです。しかし、URLに`javascript`の文字列を含むと失敗するようになっています。このフィルタリングをバイパスできるでしょうか？


結論から申し上げると、次のように改行コードを挿入すると、`new URL(dest).href`の過程で改行コード(`%0a`)が取り除かれるので、XSSに成功します。

```
javas%0acript:<Javascriptコード>
```

では、どのように考えればこの解に辿り着けるでしょうか？


### アプローチ1: 脆弱性の名前を知っていた場合

このように、あるWebページから（意図せず）任意のWebページにリダイレクトできてしまう脆弱性を**Open Redirect**と呼びます。（このようにXSSに繋がるパターンとは限りません。リダイレクトの方法により、フィッシングに繋がるパターンや、CSPバイパスに繋がるパターンなど様々あります。）

これを知っていれば「Open Redirect filter bypass」と検索し、[出てくるページ](https://www.diverto.hr/en/blog/2024-12-30-open-redirection-url-filter-bypasses/)を参考にできます。あるいは、[Hacktricks](https://book.hacktricks.wiki/en/pentesting-web/open-redirect.html?highlight=open#open-redirect-1)や[PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Open%20Redirect)のような、フィルタのバイパス手法をまとめたサイトを参考にしてもよいです。そこで見つけたペイロードをコピペしましょう。

### アプローチ2: 脆弱性の名前を知らない場合

では、この脆弱性の名前を知らなかったらどうでしょうか？あるいは、あまり一般的な脆弱性ではなく、上記のような記事が見当たらないケースもあるかもしれません。

このバリデーションには、二つのバッドプラクティスが含まれています。
1. ホワイトリストではなく、ブラックリストが利用されている
    - フィルタ漏れがある可能性がある
2. パース→フィルタの順序ではなく、フィルタ→パースの順序になっている
    - パース後にフィルタされるべき文字列が出現してしまうかもしれない
安全にフィルタを行うなら次のようにやるべきです。

```javascript
let url = new URL(dest, window.location.href).href;
if(url.startsWith("http://") || url.startsWith("https://")) {
    window.location.replace(url);
}
```

こうなっていないということは**フィルタ前は`javascript`の文字列が含まれないが、`new URL().href`を通すとjavascriptスキームになる文字列が存在するかもしれない**、と発想できます。

#### アプローチ2a: ソースや仕様書を読む

ソースを読むのも大切ですが、Chromiumのソースは膨大で探すのに時間がかかるので、まずは仕様書からURLパーサの仕様を調べましょう。

[MDN](https://developer.mozilla.org/ja/docs/Web/API/URL/parse_static#仕様書)によれば、仕様はWHATWGにより定義されているようです。リンクを辿っていけば[このページ](https://url.spec.whatwg.org/#concept-basic-url-parser)に辿り着き

> 3. 1. Remove all [ASCII tab or newline](https://infra.spec.whatwg.org/#ascii-tab-or-newline) from input.

というステップがあることがわかります。これを利用して上記のペイロードにたどり着きます。

#### アプローチ2b: fuzzingや実験をする

CTFにおいて、パースの結果フィルタしたい文字列が復元されてしまう、という問題設定を度々見かけます。そしてその大半は以下のいずれかに分類できます。

1. 「似た」文字が別の文字に置き換わる（大文字が小文字に変換される、Unicodeが正規化される、別のエンコーディングに変換される、など）
2. 一部の文字列が無視される（ヌル文字、制御文字、改行、無効なUnicodeの削除など）

これを前提に色々実験してみるのも良いですが、「無視される文字があるかも？」と疑う場合は、fuzzingも有効です。例えば、以下のようなhtmlファイルを作成して、ブラウザで開いてみましょう。

```html
<script>
// 置き換わるパターン
for(let i = 0; i < 0xFFFF /* UTF-16の最大値 */; i++) {
    const dest = `jav${String.fromCharCode(i)}script:alert(1)`;
    if(dest.toLowerCase().includes("javascript")) {
        continue;
    }
    const after = new URL(dest, window.location.href).href;
    if(after.startsWith("javascript:")) console.log("replace", i, JSON.stringify(String.fromCharCode(i)));
}

// 取り除かれるパターン
for(let i = 0; i < 0xFFFF /* UTF-16の最大値 */; i++) {
    const dest = `java${String.fromCharCode(i)}script:alert(1)`;
    if(dest.toLowerCase().includes("javascript")) {
        continue;
    }
    const after = new URL(dest, window.location.href).href;
    if(after.startsWith("javascript:")) console.log("remove", i, JSON.stringify(String.fromCharCode(i)));

}
</script>
```

コンソールに表示された結果を使えば、`\t`、`\r`、`\n`が取り除かれることがわかります。



## Flag

`Alpaca{wh4t_comes_after_the_redir3ct_pa9e}`
